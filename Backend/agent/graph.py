import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import RetryPolicy

from rag.llm import get_backup_llm, get_llm
from .tools import TOOLS

SYSTEM_PROMPT = """You are ShopEasy's friendly customer support assistant.

How to answer:
- For any policy question (returns, refunds, shipping, cancellation, payments, warranty, account), ALWAYS use search_policies. Never answer policy questions from your own knowledge.
- For a specific order, use get_order_status or get_refund_status. If the customer did not give an order ID, ask for it. If they don't remember it, ask for their registered phone number and use get_customer_orders.
- You may combine tools. Example: refund status from get_refund_status plus refund timelines from search_policies.

Cancelling orders:
- First call cancel_order with confirmed=false, tell the customer the order details, and ask them to confirm.
- Call cancel_order with confirmed=true ONLY after the customer clearly says yes.

Escalation:
- Use create_ticket when the customer asks for a human, is very unhappy, or you cannot solve the problem. Write a short summary of the issue, pass the order ID if known, and tell the customer the ticket number.
- Use high priority for payment problems or very angry customers.

Rules:
- Never invent order details, amounts, dates, or policies. Use only tool results.
- Reply in the same language the customer used (English, Telugu, Hindi, or Telugu written in English letters). Tool results are in English, so translate them into the customer's language.
- Keep replies short and friendly: 2 to 4 sentences.
- If the question is not related to ShopEasy, politely say you can only help with ShopEasy orders and policies."""

# Primary LLM fail aithe backup LLM (rendu ki tools bind)
llm_with_tools = get_llm().bind_tools(TOOLS).with_fallbacks(
    [get_backup_llm().bind_tools(TOOLS)]
)


def language_hint(text: str):
    """Telugu / Hindi script detect chesi extra instruction istundi."""
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "The customer is writing in Telugu script. Write your ENTIRE reply in Telugu script."
    if re.search(r"[\u0900-\u097F]", text):
        return "The customer is writing in Hindi (Devanagari script). Write your ENTIRE reply in Hindi."
    return None


def agent_node(state: MessagesState):
    last_user = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), ""
    )
    system = SYSTEM_PROMPT
    hint = language_hint(last_user)
    if hint:
        system += f"\n\nIMPORTANT: {hint}"

    messages = [SystemMessage(content=system)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ---------- Graph build ----------
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node, retry_policy=RetryPolicy(max_attempts=3))
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # tool_call unte "tools", lekapothe END
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=InMemorySaver())


def chat(message: str, thread_id: str):
    """Customer message ki agent reply + e tools vadindo return chestundi."""
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 12},
    )
    msgs = result["messages"]
    last_human = max(i for i, m in enumerate(msgs) if isinstance(m, HumanMessage))
    tools_used = [
        tc["name"] for m in msgs[last_human:] if isinstance(m, AIMessage) for tc in m.tool_calls
    ]
    return msgs[-1].text, tools_used