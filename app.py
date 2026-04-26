"""
Ellie & David Wedding Website - Flask App
Run: python app.py  (dev)  |  gunicorn app:app  (prod)
"""
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import select

from db import db
from models import (
    Todo,
    Vendor,
    BudgetItem,
    SeatingTable,
    SeatingGuest,
    Guest,
    Rsvp,
    Message,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

database_url = os.environ.get("DATABASE_URL", "")
# Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)


# ─── STATIC WEDDING DATA (read-only, no edit endpoints) ───
WEDDING = {
    "names": "Ellie & David",
    "date": "June 14th, 2026",
    "venue": "Nestldown",
    "venue_contact": "Ashley | ashley@nestldown.com",
    "guest_count": "~100",
    "civil_twilight": "9:01 PM",
}

TIMELINE = [
    {"time": "2:00 PM", "event": "Rental Begins", "location": "—", "note": "Couple, Wedding Party & Vendor Access"},
    {"time": "2:00 PM", "event": "Changing Room", "location": "Changing Room", "note": "Ellie & Party arrive; Ellie changes"},
    {"time": "2:15 PM", "event": "David & Party Arrive", "location": "Barn", "note": "Wedding Party & Immediate Family"},
    {"time": "2:30 PM", "event": "First Look", "location": "Fantasy Cottage", "note": "50 mins + Wedding Party Photos"},
    {"time": "3:30 PM", "event": "Guests Arrival Begins", "location": "—", "note": "1 Shuttle"},
    {"time": "3:40 PM", "event": "Positions for Ceremony", "location": "—", "note": "Nestldown team golf carts wedding party & parents"},
    {"time": "4:00 PM", "event": "Ceremony", "location": "Pond", "note": "Fountain: On"},
    {"time": "4:30 PM", "event": "Cocktail Hour", "location": "Apple Knoll", "note": "Train immediately | Non-Net Games @ Foxglove"},
    {"time": "4:30 PM", "event": "Family Portraits", "location": "Chapel", "note": "Meanwhile"},
    {"time": "5:30 PM", "event": "Grand Entrance into Cocktail Hour", "location": "Apple Knoll", "note": "Method: Train (Couple Only)"},
    {"time": "6:00 PM", "event": "Invitation to Dinner", "location": "Main Lawn", "note": "15 min transition | Newlyweds & Wedding Party entrance | Welcome Toast"},
    {"time": "6:20 PM", "event": "Dinner Service", "location": "Main Lawn", "note": "Plated — Salad as 1st Course"},
    {"time": "7:00 PM", "event": "Toasts", "location": "Main Lawn", "note": "2-5 mins max per person"},
    {"time": "7:30 PM", "event": "Invitation to Reception", "location": "Barn", "note": "First Dance → Special Dance → Open Dancing"},
    {"time": "8:15 PM", "event": "Reception Events", "location": "Barn", "note": "Knife Dance, Cake Cutting, Bouquet Toss"},
    {"time": "9:05 PM", "event": "Bar Closes", "location": "Barn", "note": "30 mins prior to last dance | No Last Call"},
    {"time": "9:35 PM", "event": "Last Dance", "location": "Barn", "note": ""},
    {"time": "9:40 PM", "event": "Grand Exit", "location": "—", "note": "Bubbles | Foam Light Sticks | Tunnel | No Sparklers/Confetti"},
    {"time": "10:00 PM", "event": "Guests Exited", "location": "—", "note": "Shuttles depart"},
    {"time": "10:00 PM", "event": "Vendor Load Out & Clean Up", "location": "—", "note": "50 mins"},
    {"time": "11:00 PM", "event": "Rental Ends", "location": "—", "note": "Nestldown Off-Site"},
]


# ─── ROUTES ───────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'public'), 'index.html')


@app.route('/api/wedding')
def get_wedding():
    return jsonify(WEDDING)


@app.route('/api/timeline')
def get_timeline():
    return jsonify(TIMELINE)


# ─── VENDORS ──────────────────────────────────────────────
def _vendors_ordered() -> list[Vendor]:
    return list(db.session.scalars(select(Vendor).order_by(Vendor.id)))


@app.route('/api/vendors')
def get_vendors():
    return jsonify([v.to_dict() for v in _vendors_ordered()])


@app.route('/api/vendors/<int:vendor_idx>', methods=['PUT'])
def update_vendor(vendor_idx):
    vendors = _vendors_ordered()
    if 0 <= vendor_idx < len(vendors):
        v = vendors[vendor_idx]
        for key, value in (request.json or {}).items():
            if hasattr(v, key):
                setattr(v, key, value)
        db.session.commit()
        return jsonify(v.to_dict())
    return jsonify({"error": "Not found"}), 404


# ─── TODOS ────────────────────────────────────────────────
@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify([t.to_dict() for t in db.session.scalars(select(Todo).order_by(Todo.id))])


@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json or {}
    todo = Todo(
        task=data.get('task', ''),
        category=data.get('category', ''),
        archived=False,
        done=False,
        due=data.get('due', ''),
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Not found"}), 404
    for key, value in (request.json or {}).items():
        if hasattr(todo, key):
            setattr(todo, key, value)
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>/archive', methods=['PUT'])
def archive_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Not found"}), 404
    todo.archived = True
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>/restore', methods=['PUT'])
def restore_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Not found"}), 404
    todo.archived = False
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is not None:
        db.session.delete(todo)
        db.session.commit()
    return jsonify({"ok": True})


# ─── BUDGET ───────────────────────────────────────────────
def _budget_payload() -> dict:
    items = list(db.session.scalars(select(BudgetItem).order_by(BudgetItem.id)))
    return {"total": 0, "items": [i.to_dict() for i in items]}


@app.route('/api/budget', methods=['GET'])
def get_budget():
    return jsonify(_budget_payload())


@app.route('/api/budget', methods=['POST'])
def update_budget():
    """Replace all budget items with the posted set. Preserves prior bulk-overwrite semantics."""
    data = request.json or {}
    posted_items = data.get('items', [])
    db.session.execute(BudgetItem.__table__.delete())
    for it in posted_items:
        db.session.add(BudgetItem(
            id=it.get('id'),
            category=it.get('category', ''),
            description=it.get('description', ''),
            is_tip=it.get('is_tip', False),
            payments=it.get('payments', []),
        ))
    db.session.commit()
    return jsonify(_budget_payload())


@app.route('/api/budget/items/<int:item_id>', methods=['PUT'])
def update_budget_item(item_id):
    item = db.session.get(BudgetItem, item_id)
    if item is None:
        return jsonify({"error": "Not found"}), 404
    for key, value in (request.json or {}).items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.session.commit()
    return jsonify(item.to_dict())


@app.route('/api/budget/items/<int:item_id>/payments', methods=['POST'])
def add_budget_payment(item_id):
    item = db.session.get(BudgetItem, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data = request.json or {}
    payments = list(item.payments or [])
    payment = {
        'id': f'p{len(payments) + 1}',
        'amount': data.get('amount', 0),
        'paid': data.get('paid', False),
        'due': data.get('due', ''),
    }
    payments.append(payment)
    item.payments = payments
    db.session.commit()
    return jsonify(payment), 201


@app.route('/api/budget/items/<int:item_id>/payments/<payment_id>', methods=['PUT'])
def update_budget_payment(item_id, payment_id):
    item = db.session.get(BudgetItem, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    payments = list(item.payments or [])
    for p in payments:
        if p.get('id') == payment_id:
            p.update(request.json or {})
            item.payments = payments
            db.session.commit()
            return jsonify(p)
    return jsonify({"error": "Payment not found"}), 404


@app.route('/api/budget/items/<int:item_id>/payments/<payment_id>', methods=['DELETE'])
def delete_budget_payment(item_id, payment_id):
    item = db.session.get(BudgetItem, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    item.payments = [p for p in (item.payments or []) if p.get('id') != payment_id]
    db.session.commit()
    return jsonify({"ok": True})


# ─── SEATING ──────────────────────────────────────────────
def _seating_payload() -> dict:
    tables = list(db.session.scalars(select(SeatingTable).order_by(SeatingTable.id)))
    guests = list(db.session.scalars(select(SeatingGuest).order_by(SeatingGuest.id)))
    return {
        "tables": [t.to_dict() for t in tables],
        "guests": [g.to_dict() for g in guests],
    }


@app.route('/api/seating', methods=['GET'])
def get_seating():
    return jsonify(_seating_payload())


@app.route('/api/seating', methods=['POST'])
def update_seating():
    """Replace the entire seating layout (tables + guests). Preserves prior bulk-overwrite semantics."""
    data = request.json or {}
    db.session.execute(SeatingGuest.__table__.delete())
    db.session.execute(SeatingTable.__table__.delete())
    for t in data.get('tables', []):
        db.session.add(SeatingTable(
            id=t.get('id'),
            number=t.get('number', 0),
            capacity=t.get('capacity', 8),
            shape=t.get('shape', 'rect'),
            x=t.get('x', 0),
            y=t.get('y', 0),
        ))
    db.session.flush()
    for g in data.get('guests', []):
        db.session.add(SeatingGuest(
            id=g.get('id'),
            name=g.get('name', ''),
            table_id=g.get('tableId'),
            seat=g.get('seat', 0),
            diet=g.get('diet', ''),
        ))
    db.session.commit()
    return jsonify(_seating_payload())


@app.route('/api/seating/guest', methods=['POST'])
def add_seating_guest():
    data = request.json or {}
    g = SeatingGuest(
        name=data.get('name', ''),
        table_id=data.get('tableId'),
        seat=data.get('seat', 0),
        diet=data.get('diet', ''),
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(g.to_dict()), 201


@app.route('/api/seating/guest/<int:guest_id>', methods=['PUT'])
def update_seating_guest(guest_id):
    g = db.session.get(SeatingGuest, guest_id)
    if g is None:
        return jsonify({"error": "Not found"}), 404
    payload = request.json or {}
    for key, value in payload.items():
        if key == 'tableId':
            g.table_id = value
        elif hasattr(g, key):
            setattr(g, key, value)
    db.session.commit()
    return jsonify(g.to_dict())


@app.route('/api/seating/guest/<int:guest_id>', methods=['DELETE'])
def delete_seating_guest(guest_id):
    g = db.session.get(SeatingGuest, guest_id)
    if g is not None:
        db.session.delete(g)
        db.session.commit()
    return jsonify({"ok": True})


# ─── GUESTS ───────────────────────────────────────────────
@app.route('/api/guests', methods=['GET'])
def get_guests():
    return jsonify([g.to_dict() for g in db.session.scalars(select(Guest).order_by(Guest.id))])


@app.route('/api/guests', methods=['POST'])
def add_guest():
    data = request.json or {}
    g = Guest(
        name=data.get('name', ''),
        side=data.get('side', ''),
        group_name=data.get('group', ''),
        diet=data.get('diet', ''),
        rsvp='pending',
        plus_ones=data.get('plus_ones', 0),
        notes=data.get('notes', ''),
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(g.to_dict()), 201


@app.route('/api/guests/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    g = db.session.get(Guest, guest_id)
    if g is None:
        return jsonify({"error": "Not found"}), 404
    payload = request.json or {}
    for key, value in payload.items():
        if key == 'group':
            g.group_name = value
        elif hasattr(g, key):
            setattr(g, key, value)
    db.session.commit()
    return jsonify(g.to_dict())


@app.route('/api/guests/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    g = db.session.get(Guest, guest_id)
    if g is not None:
        db.session.delete(g)
        db.session.commit()
    return jsonify({"ok": True})


# ─── RSVPS ────────────────────────────────────────────────
@app.route('/api/rsvps', methods=['GET'])
def get_rsvps():
    return jsonify([r.to_dict() for r in db.session.scalars(select(Rsvp).order_by(Rsvp.id))])


@app.route('/api/rsvps', methods=['POST'])
def submit_rsvp():
    data = request.json or {}
    name_lower = data.get('name', '').lower()
    existing = None
    for r in db.session.scalars(select(Rsvp)):
        if r.name.lower() == name_lower:
            existing = r
            break
    if existing is not None:
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        db.session.commit()
        return jsonify(existing.to_dict())
    rsvp = Rsvp(
        name=data.get('name', ''),
        email=data.get('email', ''),
        attending=data.get('attending', ''),
        dietary=data.get('dietary', ''),
        song=data.get('song', ''),
        message=data.get('message', ''),
        submitted_at=datetime.now().isoformat(),
    )
    db.session.add(rsvp)
    db.session.commit()
    return jsonify(rsvp.to_dict()), 201


# ─── MESSAGES ─────────────────────────────────────────────
@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify([m.to_dict() for m in db.session.scalars(select(Message).order_by(Message.id))])


@app.route('/api/messages', methods=['POST'])
def post_message():
    data = request.json or {}
    msg = Message(
        name=data.get('name', ''),
        text=data.get('text', ''),
        submitted_at=datetime.now().isoformat(),
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_dict()), 201


# ─── STATS ────────────────────────────────────────────────
@app.route('/api/stats')
def get_stats():
    guests = list(db.session.scalars(select(Guest)))
    rsvps = list(db.session.scalars(select(Rsvp)))
    todos = list(db.session.scalars(select(Todo)))
    attending = sum(1 for r in rsvps if r.attending == 'yes')
    not_attending = sum(1 for r in rsvps if r.attending == 'no')
    pending = len(guests) - len(rsvps)
    today = datetime.now().strftime('%Y-%m-%d')
    week_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    overdue = [t.to_dict() for t in todos if not t.archived and not t.done and t.due and t.due < today]
    this_week = [t.to_dict() for t in todos if not t.archived and not t.done and t.due and today <= t.due <= week_end]
    return jsonify({
        "total_guests": len(guests),
        "attending": attending,
        "not_attending": not_attending,
        "pending": pending,
        "todos_total": len(todos),
        "todos_done": sum(1 for t in todos if t.done),
        "overdue_count": len(overdue),
        "overdue_tasks": overdue[:5],
        "this_week_count": len(this_week),
        "this_week_tasks": this_week[:5],
    })


if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), 'public'), exist_ok=True)
    print("Starting Ellie & David Wedding Site on http://localhost:5000")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')
