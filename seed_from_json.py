"""
One-shot importer: seeds an empty database from data/*.json (and a hardcoded
vendor list, since vendors were never persisted to JSON).

Idempotent — only inserts into tables that are currently empty. Safe to run
on every deploy via the render.yaml pre-deploy hook.

Usage:
    DATABASE_URL=... python seed_from_json.py
"""
import json
import os
from sqlalchemy import select, func

from app import app
from db import db
from models import (
    Todo,
    Vendor,
    BudgetItem,
    SeatingTable,
    SeatingGuest,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


VENDORS_SEED = [
    {"name": "Le Papillon", "type": "Catering", "time": "2:00 PM", "email": "tamera@lepapillon.com", "phone": "408.296.3730", "note": "", "include_tip": False},
    {"name": "Danny Dong", "type": "Photography", "time": "2:00 PM", "email": "dannydongliang@hotmail.com", "phone": "408.429.0158", "note": "", "include_tip": False},
    {"name": "AVR Films", "type": "Videography", "time": "2:00 PM", "email": "events@avrfilms.com", "phone": "408-836-9440", "note": "", "include_tip": False},
    {"name": "Bloomsters", "type": "Floral", "time": "2:00 PM", "email": "", "phone": "408.268.5518", "note": "", "include_tip": False},
    {"name": "AVL Entertainment", "type": "DJ", "time": "2:15 PM", "email": "aaron@avlentertainment.com", "phone": "(323) 203-6707", "note": "", "include_tip": False},
    {"name": "Foxy Faces by Jen", "type": "Hair & Makeup", "time": "2:15 PM", "email": "foxyfacesbyjen@gmail.com", "phone": "951.454.0431", "note": "", "include_tip": False},
    {"name": "Howard Steiermann", "type": "Officiant", "time": "2:30 PM", "email": "HSteiermann@gmail.com", "phone": "415-695-9155", "note": "", "include_tip": False},
    {"name": "Natasha's Treats", "type": "Cake & Desserts", "time": "2:30 PM", "email": "natashastreatssj@gmail.com", "phone": "408-646-5796", "note": "", "include_tip": False},
    {"name": "Sal's", "type": "Shuttles", "time": "3:30 PM", "email": "", "phone": "(408) 733-1275", "note": "", "include_tip": False},
    {"name": "Danny Thomas", "type": "Tabletop Rental", "time": "10:00 AM (Pre-event)", "email": "", "phone": "(408) 747-1000", "note": "", "include_tip": False},
]


def _load(name: str, default):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def _is_empty(model) -> bool:
    return db.session.scalar(select(func.count()).select_from(model)) == 0


def seed_vendors():
    if not _is_empty(Vendor):
        print("vendors: skip (already populated)")
        return
    for v in VENDORS_SEED:
        db.session.add(Vendor(**v))
    db.session.commit()
    print(f"vendors: seeded {len(VENDORS_SEED)}")


def seed_todos():
    if not _is_empty(Todo):
        print("todos: skip (already populated)")
        return
    todos = _load("todos.json", [])
    for t in todos:
        db.session.add(Todo(
            id=t.get("id"),
            task=t.get("task", ""),
            category=t.get("category", ""),
            archived=t.get("archived", False),
            done=t.get("done", False),
            due=t.get("due", ""),
        ))
    db.session.commit()
    print(f"todos: seeded {len(todos)}")


def seed_budget():
    if not _is_empty(BudgetItem):
        print("budget_items: skip (already populated)")
        return
    budget = _load("budget.json", {"items": []})
    items = budget.get("items", [])
    for it in items:
        db.session.add(BudgetItem(
            id=it.get("id"),
            category=it.get("category", ""),
            description=it.get("description", ""),
            is_tip=it.get("is_tip", False),
            payments=it.get("payments", []),
        ))
    db.session.commit()
    print(f"budget_items: seeded {len(items)}")


def seed_seating():
    seating = _load("seating.json", {"tables": [], "guests": []})

    if _is_empty(SeatingTable):
        tables = seating.get("tables", [])
        for t in tables:
            db.session.add(SeatingTable(
                id=t.get("id"),
                number=t.get("number", 0),
                capacity=t.get("capacity", 8),
                shape=t.get("shape", "rect"),
                x=t.get("x", 0),
                y=t.get("y", 0),
            ))
        db.session.commit()
        print(f"seating_tables: seeded {len(tables)}")
    else:
        print("seating_tables: skip (already populated)")

    if _is_empty(SeatingGuest):
        guests = seating.get("guests", [])
        for g in guests:
            db.session.add(SeatingGuest(
                id=g.get("id"),
                name=g.get("name", ""),
                table_id=g.get("tableId"),
                seat=g.get("seat", 0),
                diet=g.get("diet", ""),
            ))
        db.session.commit()
        print(f"seating_guests: seeded {len(guests)}")
    else:
        print("seating_guests: skip (already populated)")


def main():
    with app.app_context():
        seed_vendors()
        seed_todos()
        seed_budget()
        seed_seating()


if __name__ == "__main__":
    main()
