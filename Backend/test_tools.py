from db.database import SessionLocal
from db.models import Order
from agent.tools import (
    search_policies, get_customer_orders, get_order_status,
    get_refund_status, cancel_order, create_ticket,
)

with SessionLocal() as db:
    phone_1005 = db.get(Order, 1005).customer.phone
    placed = db.query(Order).filter(Order.status == "placed").first()
    placed_id = placed.id if placed else None

print("1. ", get_customer_orders.invoke({"phone": phone_1005}))
print("2. ", get_order_status.invoke({"order_id": 1005}))
print("3. ", get_order_status.invoke({"order_id": 9999}))
print("4. ", get_refund_status.invoke({"order_id": 1005}))
print("5. ", get_refund_status.invoke({"order_id": 1001}))
print("6. ", cancel_order.invoke({"order_id": 1005}))

if placed_id:
    print("7. ", cancel_order.invoke({"order_id": placed_id}))
    print("8. ", cancel_order.invoke({"order_id": placed_id, "confirmed": True}))
else:
    print("7-8. No 'placed' order in data to test cancellation")

print("9. ", create_ticket.invoke({"issue": "Test: customer wants a human agent", "priority": "high", "order_id": 1005}))
print("10.", search_policies.invoke({"query": "How long does a UPI refund take?"})[:120], "...")