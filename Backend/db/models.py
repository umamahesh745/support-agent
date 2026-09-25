from datetime import datetime
from sqlalchemy import String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone: Mapped[str] = mapped_column(String(15))
    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    product: Mapped[str] = mapped_column(String(150))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))  # placed / shipped / delivered / cancelled
    order_date: Mapped[datetime] = mapped_column(DateTime)
    customer = relationship("Customer", back_populates="orders")


class Refund(Base):
    __tablename__ = "refunds"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))  # requested / approved / processed
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    sentiment: Mapped[str | None] = mapped_column(String(20))
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(10))  # user / agent
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id"))
    issue: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="medium")  # low / medium / high
    status: Mapped[str] = mapped_column(String(20), default="open")     # open / escalated / closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)