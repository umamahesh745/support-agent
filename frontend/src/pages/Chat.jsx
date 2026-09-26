import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getMessages, sendMessage } from "../api";

const TOOL_LABELS = {
  search_policies: "📄 Policies",
  get_order_status: "📦 Order status",
  get_refund_status: "💰 Refund status",
  get_customer_orders: "🧾 Customer orders",
  cancel_order: "❌ Cancel order",
  create_ticket: "🎫 Ticket created",
};

const SUGGESTIONS = [
  "What is your return policy?",
  "Where is my order 1024?",
  "Order 1006 refund status?",
  "I want to talk to a human",
];

const WELCOME = {
  role: "agent",
  content:
    "Hi! I'm the ShopEasy assistant. Ask me about orders, refunds, returns or shipping. You can write in English, Telugu or Hindi.",
};

// Agent replies lo Markdown (bold, lists) styling
const MD = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
};

export default function Chat() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(() => {
    const saved = localStorage.getItem("conversationId");
    return saved ? Number(saved) : null;
  });
  const [escalated, setEscalated] = useState(() => localStorage.getItem("escalated") === "true");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Kotha message vachinappudu kindaki scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Page ki tirigi vachinappudu / refresh chesinappudu history load
  useEffect(() => {
    if (!conversationId) return;
    getMessages(conversationId)
      .then((history) => {
        if (history.length) {
          setMessages([WELCOME, ...history.map((m) => ({ role: m.role, content: m.content }))]);
        }
      })
      .catch(() => {
        localStorage.removeItem("conversationId");
        localStorage.removeItem("escalated");
        setConversationId(null);
        setEscalated(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function send(text) {
    const message = text.trim();
    if (!message || loading) return;

    setMessages((m) => [...m, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(message, conversationId);
      setConversationId(data.conversation_id);
      setEscalated(data.escalated);
      localStorage.setItem("conversationId", data.conversation_id);
      localStorage.setItem("escalated", data.escalated);
      setMessages((m) => [...m, { role: "agent", content: data.reply, tools: data.tools_used }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "agent",
          content: "Sorry, I couldn't reach the server. Please check that the backend is running.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function newChat() {
    localStorage.removeItem("conversationId");
    localStorage.removeItem("escalated");
    setMessages([WELCOME]);
    setConversationId(null);
    setEscalated(false);
  }

  return (
    <div className="max-w-3xl w-full mx-auto flex flex-col p-4 h-[calc(100vh-3.5rem)]">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500">
          {conversationId ? `Conversation #${conversationId}` : "New conversation"}
        </p>
        <button onClick={newChat} className="text-sm text-indigo-600 hover:underline">
          + New chat
        </button>
      </div>

      {escalated && (
        <div className="mb-3 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-sm text-amber-800">
          This conversation has been escalated to a human agent.
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-3 bg-white rounded-xl border p-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className="max-w-[80%]">
              <div
                className={`rounded-2xl px-4 py-2 text-sm ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-sm whitespace-pre-wrap"
                    : m.error
                    ? "bg-red-50 text-red-700 rounded-bl-sm"
                    : "bg-gray-100 text-gray-800 rounded-bl-sm"
                }`}
              >
                {m.role === "agent" ? (
                  <ReactMarkdown components={MD}>{m.content}</ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
              {m.tools?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {[...new Set(m.tools)].map((t) => (
                    <span
                      key={t}
                      className="text-[11px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full"
                    >
                      {TOOL_LABELS[t] || t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-sm text-gray-400 animate-pulse">Assistant is typing…</div>}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-xs bg-white border rounded-full px-3 py-1.5 hover:bg-gray-100"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="mt-3 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 rounded-xl border px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-xl bg-indigo-600 px-5 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}