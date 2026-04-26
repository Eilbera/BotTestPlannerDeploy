from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class Todo(db.Model):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, default="")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    due: Mapped[str] = mapped_column(String, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task": self.task,
            "category": self.category,
            "archived": self.archived,
            "done": self.done,
            "due": self.due,
        }


class Vendor(db.Model):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    type: Mapped[str] = mapped_column(String, default="")
    time: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String, default="")
    phone: Mapped[str] = mapped_column(String, default="")
    note: Mapped[str] = mapped_column(String, default="")
    include_tip: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "time": self.time,
            "email": self.email,
            "phone": self.phone,
            "note": self.note,
            "include_tip": self.include_tip,
        }


class BudgetItem(db.Model):
    __tablename__ = "budget_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(String, default="")
    is_tip: Mapped[bool] = mapped_column(Boolean, default=False)
    payments: Mapped[list] = mapped_column(JSON, default=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "is_tip": self.is_tip,
            "payments": self.payments or [],
        }


class SeatingTable(db.Model):
    __tablename__ = "seating_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=8)
    shape: Mapped[str] = mapped_column(String, default="rect")
    x: Mapped[int] = mapped_column(Integer, default=0)
    y: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "number": self.number,
            "capacity": self.capacity,
            "shape": self.shape,
            "x": self.x,
            "y": self.y,
        }


class SeatingGuest(db.Model):
    __tablename__ = "seating_guests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    table_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("seating_tables.id", ondelete="SET NULL"), nullable=True
    )
    seat: Mapped[int] = mapped_column(Integer, default=0)
    diet: Mapped[str] = mapped_column(String, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "tableId": self.table_id,
            "seat": self.seat,
            "diet": self.diet,
        }


class Guest(db.Model):
    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    side: Mapped[str] = mapped_column(String, default="")
    group_name: Mapped[str] = mapped_column("group_name", String, default="")
    diet: Mapped[str] = mapped_column(String, default="")
    rsvp: Mapped[str] = mapped_column(String, default="pending")
    plus_ones: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(String, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side,
            "group": self.group_name,
            "diet": self.diet,
            "rsvp": self.rsvp,
            "plus_ones": self.plus_ones,
            "notes": self.notes,
        }


class Rsvp(db.Model):
    __tablename__ = "rsvps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String, default="")
    attending: Mapped[str] = mapped_column(String, default="")
    dietary: Mapped[str] = mapped_column(String, default="")
    song: Mapped[str] = mapped_column(String, default="")
    message: Mapped[str] = mapped_column(String, default="")
    submitted_at: Mapped[str] = mapped_column(String, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "attending": self.attending,
            "dietary": self.dietary,
            "song": self.song,
            "message": self.message,
            "submitted_at": self.submitted_at,
        }


class Message(db.Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    text: Mapped[str] = mapped_column(String, default="")
    submitted_at: Mapped[str] = mapped_column(String, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text,
            "submitted_at": self.submitted_at,
        }
