from langchain_core.tools import tool

from db.database import SessionLocal
from db.models import Customer, Order, Refund, Ticket
from rag.qa import MAX_DISTANCE
from rag.retriever import retrieve


@tool
def search_policies(query: str) -> str:
    """Search ShopEasy policy documents about returns, refunds, shipping, cancellation,
    payments, warranty, account and FAQs. Use this for any general policy question."""
    chunks = [c for c in retrieve(query, k=3) if c["distance"] <= MAX_DISTANCE]
    if not chunks:
        return "No relevant policy information found."
    return "\n\n".join(f"[{c['source']} > {c['section']}]\n{c['content']}" for c in chunks)


@tool
def get_customer_orders(phone: str) -> str:
    """List the recent orders of a customer using their registered 10-digit phone number.
    Use when the customer does not remember their order ID."""
    digits = "".join(ch for ch in phone if ch.isdigit())[-10:]
    with SessionLocal() as db:
        customer = db.query(Customer).filter(Customer.phone == digits).first()
        if not customer:
            return "No ShopEasy account found with this phone number."

        orders = (
            db.query(Order)
            .filter(Order.customer_id == customer.id)
            .order_by(Order.order_date.desc())
            .limit(10)
            .all()
        )
        if not orders:
            return f"{customer.name} has no orders."

        lines = [
            f"- Order {o.id}: {o.product}, {o.amount:.0f} rupees, {o.status}, {o.order_date:%d %b %Y}"
            for o in orders
        ]
        return f"Orders of {customer.name}:\n" + "\n".join(lines)


@tool
def get_order_status(order_id: int) -> str:
    """Get the status, product, amount and order date of a ShopEasy order using its order ID (for example 1005)."""
    with SessionLocal() as db:
        order = db.get(Order, order_id)
        if not order:
            return f"No order found with ID {order_id}."
        return (
            f"Order {order.id}: {order.product}, amount {order.amount:.0f} rupees, "
            f"status {order.status}, ordered on {order.order_date:%d %b %Y}."
        )


@tool
def get_refund_status(order_id: int) -> str:
    """Get the refund status for a ShopEasy order using its order ID."""
    with SessionLocal() as db:
        order = db.get(Order, order_id)
        if not order:
            return f"No order found with ID {order_id}."

        refund = db.query(Refund).filter(Refund.order_id == order_id).first()
        if not refund:
            return f"There is no refund for order {order_id}. The order status is {order.status}."
        return (
            f"Refund for order {order_id}: amount {refund.amount:.0f} rupees, "
            f"status {refund.status}, requested on {refund.requested_at:%d %b %Y}."
        )


@tool
def cancel_order(order_id: int, confirmed: bool = False) -> str:
    """Cancel an order. Only orders with status 'placed' can be cancelled.
    First call with confirmed=false to check the order and ask the customer to confirm.
    Call again with confirmed=true ONLY after the customer clearly says yes."""
    with SessionLocal() as db:
        order = db.get(Order, order_id)
        if not order:
            return f"No order found with ID {order_id}."

        if order.status != "placed":
            return (
                f"Order {order_id} cannot be cancelled because its status is '{order.status}'. "
                "Only orders with status 'placed' can be cancelled."
            )

        if not confirmed:
            return (
                f"CONFIRMATION NEEDED: Order {order_id} ({order.product}, {order.amount:.0f} rupees) "
                "can be cancelled. Ask the customer to confirm before cancelling."
            )

        order.status = "cancelled"
        db.add(Refund(order_id=order.id, amount=order.amount, status="requested"))
        db.commit()
        return f"Order {order_id} has been cancelled. A refund of {order.amount:.0f} rupees has been requested."


@tool
def create_ticket(issue: str, priority: str = "medium", order_id: int | None = None) -> str:
    """Create a support ticket to escalate the issue to a human agent. Use when the customer
    asks for a human, is very unhappy, or the problem cannot be solved. Priority: low, medium or high."""
    if priority not in {"low", "medium", "high"}:
        priority = "medium"

    with SessionLocal() as db:
        customer_id = None
        if order_id:
            order = db.get(Order, order_id)
            customer_id = order.customer_id if order else None

        ticket = Ticket(customer_id=customer_id, issue=issue, priority=priority, status="escalated")
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        hours = 4 if priority == "high" else 24
        return f"Ticket #{ticket.id} created with {priority} priority. A human agent will contact the customer within {hours} hours."


TOOLS = [search_policies, get_customer_orders, get_order_status, get_refund_status, cancel_order, create_ticket]