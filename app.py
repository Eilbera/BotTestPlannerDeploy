"""
Ellie & David Wedding Website - Flask App
Run: python app.py
"""
import json
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def get_file(path):
    return os.path.join(DATA_DIR, path)

# ─── DATA FILES ───────────────────────────────────────────
GUESTS_FILE  = get_file('guests.json')
RSVP_FILE    = get_file('rsvps.json')
TODO_FILE    = get_file('todos.json')
MESSAGES_FILE = get_file('messages.json')
BUDGET_FILE  = get_file('budget.json')

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ─── WEDDING DATA ─────────────────────────────────────────
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

VENDORS = [
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

SEATING_FILE = get_file('seating.json')

def default_seating():
    return {
        "tables": [
            {"id": 1, "number": 1, "capacity": 8, "shape": "rect", "x": 0, "y": 0},
            {"id": 2, "number": 2, "capacity": 8, "shape": "rect", "x": 1, "y": 0},
            {"id": 3, "number": 3, "capacity": 8, "shape": "rect", "x": 2, "y": 0},
            {"id": 4, "number": 4, "capacity": 10, "shape": "rect", "x": 0, "y": 1},
            {"id": 5, "number": 5, "capacity": 10, "shape": "rect", "x": 1, "y": 1},
            {"id": 6, "number": 6, "capacity": 10, "shape": "rect", "x": 2, "y": 1},
            {"id": 7, "number": 7, "capacity": 8, "shape": "round", "x": 0, "y": 2},
            {"id": 8, "number": 8, "capacity": 8, "shape": "round", "x": 1, "y": 2},
            {"id": 9, "number": 9, "capacity": 8, "shape": "round", "x": 2, "y": 2},
        ],
        "guests": []
    }

SEATING = load_json(SEATING_FILE, default_seating())

def default_todos():
    return [
        {"id": 1, "task": "Final venue walkthrough", "archived": False, "done": False, "due": "2026-04-30"},
        {"id": 2, "task": "Confirm all vendors hired", "archived": False, "done": False, "due": "2026-03-13"},
        {"id": 3, "task": "Send timeline to vendors", "archived": False, "done": False, "due": "2026-05-14"},
        {"id": 4, "task": "Final payment to Nestldown", "archived": False, "done": False, "due": "2026-02-14"},
        {"id": 5, "task": "Insurance submitted", "archived": False, "done": False, "due": "2026-02-14"},
        {"id": 6, "task": "Create seating chart", "archived": False, "done": False, "due": "2026-05-14"},
        {"id": 7, "task": "Confirm dietary restrictions with caterer", "archived": False, "done": False, "due": "2026-05-01"},
        {"id": 8, "task": "Order additional rentals (if needed)", "archived": False, "done": False, "due": "2026-04-01"},
        {"id": 9, "task": "Final dress fitting", "archived": False, "done": False, "due": "2026-05-15"},
        {"id": 10, "task": "Pick up wedding bands", "archived": False, "done": False, "due": "2026-05-20"},
        {"id": 11, "task": "Hair & makeup trial", "archived": False, "done": False, "due": "2026-04-15"},
        {"id": 12, "task": "Marriage license", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 13, "task": "Guest hotel block confirmations", "archived": False, "done": False, "due": "2026-04-01"},
        {"id": 14, "task": "Coordinate grand exit vehicles", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 15, "task": "Breakdown plan with vendors", "archived": False, "done": False, "due": "2026-06-13"},
        {"id": 16, "task": "Rehearsal & rehearsal dinner", "archived": False, "done": False, "due": "2026-06-13"},
        {"id": 17, "task": "Pack personal items (5 boxes)", "archived": False, "done": False, "due": "2026-06-13"},
        {"id": 18, "task": "Finalize toasts & speeches", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 19, "task": "Confirm shuttle schedule with Sal's", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 20, "task": "ADA car arranged for grandma", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 21, "task": "Dance practice with friends — every Friday until wedding", "archived": False, "done": False, "due": "2026-04-24"},
        {"id": 22, "task": "Talk to florist (Bloomsters) & schedule prototype meeting", "archived": False, "done": False, "due": "2026-04-25"},
        {"id": 23, "task": "Figure out vendor tipping situation", "archived": False, "done": False, "due": "2026-05-01"},
        {"id": 24, "task": "Buy exit items (bubbles, foam light sticks, or other)", "archived": False, "done": False, "due": "2026-05-15"},
        {"id": 25, "task": "Finalize seating chart", "archived": False, "done": False, "due": "2026-05-20"},
        {"id": 26, "task": "Plan rehearsal dinner / book venue", "archived": False, "done": False, "due": "2026-05-01"},
        {"id": 27, "task": "Write love letter to David", "archived": False, "done": False, "due": "2026-05-30"},
        {"id": 28, "task": "Pack wedding day items: rings, license, cups, knife, card box, 'After the T', khigga cotton", "archived": False, "done": False, "due": "2026-06-13"},
        {"id": 29, "task": "First dance lessons with David", "archived": False, "done": False, "due": "2026-05-01"},
        {"id": 30, "task": "Buy rehearsal dinner outfits (Ellie & David)", "archived": False, "done": False, "due": "2026-05-15"},
        {"id": 31, "task": "Buy getting ready pajamas", "archived": False, "done": False, "due": "2026-05-20"},
        {"id": 32, "task": "Honeymoon: packing & buying outfits", "archived": False, "done": False, "due": "2026-06-01"},
        {"id": 33, "task": "Buy/order Ellie wedding band", "archived": False, "done": False, "due": "2026-05-10"},
        {"id": 34, "task": "Figure out music (playlist, ceremony, reception)", "archived": False, "done": False, "due": "2026-05-15"},
    ]

def default_budget():
    return {
        "total": 0,
        "items": [
            {"id": 1, "category": "venue", "description": "Nestldown venue deposit", "amount": 0, "paid": False, "due": "2026-02-14", "is_tip": False},
            {"id": 2, "category": "venue", "description": "Nestldown final balance", "amount": 0, "paid": False, "due": "2026-06-01", "is_tip": False},
            {"id": 3, "category": "catering", "description": "Catering", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 4, "category": "catering", "description": "Catering tip (optional)", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 5, "category": "photography", "description": "Danny Dong Photography", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 6, "category": "photography", "description": "Photography tip", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 7, "category": "videography", "description": "AVR Films", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 8, "category": "videography", "description": "Videography tip", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 9, "category": "floral", "description": "Bloomsters Floral", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 10, "category": "floral", "description": "Floral tip", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 11, "category": "dj", "description": "AVL Entertainment DJ", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 12, "category": "dj", "description": "DJ tip (optional)", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 13, "category": "beauty", "description": "Foxy Faces (Hair & Makeup)", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 14, "category": "beauty", "description": "Hair & Makeup tip — $150 × 3 stylists = $450", "amount": 450, "paid": False, "due": "", "is_tip": True},
            {"id": 15, "category": "officiant", "description": "Howard Steiermann (Officiant)", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 16, "category": "officiant", "description": "Officiant tip (optional)", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 17, "category": "cake", "description": "Natasha's Treats (Cake & Desserts)", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 18, "category": "cake", "description": "Cake & Desserts tip (optional)", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 19, "category": "transportation", "description": "Sal's Shuttles", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 20, "category": "transportation", "description": "Shuttle tip — $50 (15% gratuity already included in contract)", "amount": 50, "paid": False, "due": "", "is_tip": True},
            {"id": 21, "category": "rental", "description": "Danny Thomas Tabletop Rental", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 22, "category": "rental", "description": "Rental tip (optional)", "amount": 0, "paid": False, "due": "", "is_tip": True},
            {"id": 23, "category": "attire", "description": "Ellie's dress", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 24, "category": "attire", "description": "David's suit/outfit", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 25, "category": "attire", "description": "Wedding bands", "amount": 0, "paid": False, "due": "2026-05-20", "is_tip": False},
            {"id": 26, "category": "attire", "description": "Rehearsal dinner outfits", "amount": 0, "paid": False, "due": "2026-05-15", "is_tip": False},
            {"id": 27, "category": "attire", "description": "Getting ready pajamas", "amount": 0, "paid": False, "due": "2026-05-20", "is_tip": False},
            {"id": 28, "category": "decor", "description": "Exit items (bubbles, lights)", "amount": 0, "paid": False, "due": "2026-05-15", "is_tip": False},
            {"id": 29, "category": "flowers", "description": "Bridal bouquet / Flowers", "amount": 0, "paid": False, "due": "", "is_tip": False},
            {"id": 30, "category": "other", "description": "Marriage license", "amount": 0, "paid": False, "due": "2026-06-01", "is_tip": False},
            {"id": 31, "category": "other", "description": "Wedding insurance", "amount": 0, "paid": False, "due": "2026-02-14", "is_tip": False},
            {"id": 32, "category": "other", "description": "Honeymoon", "amount": 0, "paid": False, "due": "2026-06-01", "is_tip": False},
        ]
    }

TODOS = load_json(TODO_FILE, default_todos())
BUDGET = load_json(BUDGET_FILE, default_budget())

# ─── API ROUTES ───────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'public'), 'index.html')

@app.route('/api/wedding')
def get_wedding():
    return jsonify(WEDDING)

@app.route('/api/timeline')
def get_timeline():
    return jsonify(TIMELINE)

@app.route('/api/vendors')
def get_vendors():
    return jsonify(VENDORS)

@app.route('/api/vendors/<int:vendor_idx>', methods=['PUT'])
def update_vendor(vendor_idx):
    if 0 <= vendor_idx < len(VENDORS):
        VENDORS[vendor_idx].update(request.json)
        return jsonify(VENDORS[vendor_idx])
    return jsonify({"error": "Not found"}), 404

# ─── TODOS ────────────────────────────────────────────────
@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(load_json(TODO_FILE, default_todos()))

@app.route('/api/todos', methods=['POST'])
def create_todo():
    todos = load_json(TODO_FILE, TODOS)
    data = request.json
    todo = {
        "id": len(todos) + 1,
        "task": data.get('task', ''),
        "archived": False,
        "done": False,
        "due": data.get('due', ''),
    }
    todos.append(todo)
    save_json(TODO_FILE, todos)
    return jsonify(todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo (e.g., toggle done status)"""
    global TODOS
    todos = load_json(TODO_FILE, [])
    for t in todos:
        if t['id'] == todo_id:
            t.update(request.json)
            save_json(TODO_FILE, todos)
            TODOS = todos
            return jsonify(t)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/todos/<int:todo_id>/archive', methods=['PUT'])
def archive_todo(todo_id):
    """Archive a todo (soft delete)"""
    global TODOS
    todos = load_json(TODO_FILE, [])
    for t in todos:
        if t['id'] == todo_id:
            t['archived'] = True
            save_json(TODO_FILE, todos)
            TODOS = todos
            return jsonify(t)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/todos/<int:todo_id>/restore', methods=['PUT'])
def restore_todo(todo_id):
    """Restore an archived todo"""
    global TODOS
    todos = load_json(TODO_FILE, [])
    for t in todos:
        if t['id'] == todo_id:
            t['archived'] = False
            save_json(TODO_FILE, todos)
            TODOS = todos
            return jsonify(t)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Permanently delete a todo"""
    global TODOS
    todos = load_json(TODO_FILE, [])
    todos = [t for t in todos if t['id'] != todo_id]
    save_json(TODO_FILE, todos)
    TODOS = todos
    return jsonify({"ok": True})
 # ─── BUDGET ───────────────────────────────────────────────
@app.route('/api/budget', methods=['GET'])
def get_budget():
    return jsonify(load_json(BUDGET_FILE, default_budget()))

@app.route('/api/budget', methods=['POST'])
def update_budget():
    global BUDGET
    data = request.json
    BUDGET = data
    save_json(BUDGET_FILE, BUDGET)
    return jsonify(BUDGET)

@app.route('/api/budget/items/<int:item_id>', methods=['PUT'])
def update_budget_item(item_id):
    for item in BUDGET['items']:
        if item['id'] == item_id:
            item.update(request.json)
            save_json(BUDGET_FILE, BUDGET)
            return jsonify(item)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/budget/items/<int:item_id>/payments', methods=['POST'])
def add_budget_payment(item_id):
    """Add a new payment installment to a budget item."""
    for item in BUDGET['items']:
        if item['id'] == item_id:
            data = request.json
            payment = {
                'id': f'p{len(item["payments"]) + 1}',
                'amount': data.get('amount', 0),
                'paid': data.get('paid', False),
                'due': data.get('due', '')
            }
            item['payments'].append(payment)
            save_json(BUDGET_FILE, BUDGET)
            return jsonify(payment), 201
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/budget/items/<int:item_id>/payments/<payment_id>', methods=['PUT'])
def update_budget_payment(item_id, payment_id):
    """Update a specific payment installment."""
    for item in BUDGET['items']:
        if item['id'] == item_id:
            for p in item['payments']:
                if p['id'] == payment_id:
                    p.update(request.json)
                    save_json(BUDGET_FILE, BUDGET)
                    return jsonify(p)
            return jsonify({"error": "Payment not found"}), 404
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/budget/items/<int:item_id>/payments/<payment_id>', methods=['DELETE'])
def delete_budget_payment(item_id, payment_id):
    """Delete a payment installment from a budget item."""
    for item in BUDGET['items']:
        if item['id'] == item_id:
            item['payments'] = [p for p in item['payments'] if p['id'] != payment_id]
            save_json(BUDGET_FILE, BUDGET)
            return jsonify({"ok": True})
    return jsonify({"error": "Item not found"}), 404

# ─── SEATING ──────────────────────────────────────────────
@app.route('/api/seating', methods=['GET'])
def get_seating():
    return jsonify(load_json(SEATING_FILE, default_seating()))

@app.route('/api/seating', methods=['POST'])
def update_seating():
    global SEATING
    SEATING = request.json
    save_json(SEATING_FILE, SEATING)
    return jsonify(SEATING)

@app.route('/api/seating/guest', methods=['POST'])
def add_seating_guest():
    global SEATING
    data = request.json
    guest = {
        "id": len(SEATING['guests']) + 1,
        "name": data.get('name', ''),
        "tableId": data.get('tableId', None),
        "seat": data.get('seat', 0),
        "diet": data.get('diet', ''),
    }
    SEATING['guests'].append(guest)
    save_json(SEATING_FILE, SEATING)
    return jsonify(guest), 201

@app.route('/api/seating/guest/<int:guest_id>', methods=['PUT'])
def update_seating_guest(guest_id):
    global SEATING
    for g in SEATING['guests']:
        if g['id'] == guest_id:
            g.update(request.json)
            save_json(SEATING_FILE, SEATING)
            return jsonify(g)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/seating/guest/<int:guest_id>', methods=['DELETE'])
def delete_seating_guest(guest_id):
    global SEATING
    SEATING['guests'] = [g for g in SEATING['guests'] if g['id'] != guest_id]
    save_json(SEATING_FILE, SEATING)
    return jsonify({"ok": True})

# ─── LEGACY ROUTES (kept for compatibility) ──────────────
@app.route('/api/guests', methods=['GET'])
def get_guests():
    return jsonify(load_json(GUESTS_FILE, []))

@app.route('/api/guests', methods=['POST'])
def add_guest():
    guests = load_json(GUESTS_FILE, [])
    data = request.json
    guest = {
        "id": len(guests) + 1,
        "name": data.get('name', ''),
        "side": data.get('side', ''),
        "group": data.get('group', ''),
        "diet": data.get('diet', ''),
        "rsvp": "pending",
        "plus_ones": data.get('plus_ones', 0),
        "notes": data.get('notes', ''),
    }
    guests.append(guest)
    save_json(GUESTS_FILE, guests)
    return jsonify(guest), 201

@app.route('/api/guests/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    guests = load_json(GUESTS_FILE, [])
    for g in guests:
        if g['id'] == guest_id:
            g.update(request.json)
            save_json(GUESTS_FILE, guests)
            return jsonify(g)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/guests/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    guests = load_json(GUESTS_FILE, [])
    guests = [g for g in guests if g['id'] != guest_id]
    save_json(GUESTS_FILE, guests)
    return jsonify({"ok": True})

@app.route('/api/rsvps', methods=['GET'])
def get_rsvps():
    return jsonify(load_json(RSVP_FILE, []))

@app.route('/api/rsvps', methods=['POST'])
def submit_rsvp():
    rsvps = load_json(RSVP_FILE, [])
    data = request.json
    for r in rsvps:
        if r.get('name', '').lower() == data.get('name', '').lower():
            r.update(data)
            save_json(RSVP_FILE, rsvps)
            return jsonify(r)
    rsvp = {
        "id": len(rsvps) + 1,
        "name": data.get('name', ''),
        "email": data.get('email', ''),
        "attending": data.get('attending', ''),
        "dietary": data.get('dietary', ''),
        "song": data.get('song', ''),
        "message": data.get('message', ''),
        "submitted_at": datetime.now().isoformat(),
    }
    rsvps.append(rsvp)
    save_json(RSVP_FILE, rsvps)
    return jsonify(rsvp), 201

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(load_json(MESSAGES_FILE, []))

@app.route('/api/messages', methods=['POST'])
def post_message():
    messages = load_json(MESSAGES_FILE, [])
    data = request.json
    msg = {
        "id": len(messages) + 1,
        "name": data.get('name', ''),
        "text": data.get('text', ''),
        "submitted_at": datetime.now().isoformat(),
    }
    messages.append(msg)
    save_json(MESSAGES_FILE, messages)
    return jsonify(msg), 201

@app.route('/api/stats')
def get_stats():
    guests = load_json(GUESTS_FILE, [])
    rsvps = load_json(RSVP_FILE, [])
    todos = load_json(TODO_FILE, default_todos())
    attending = sum(1 for r in rsvps if r.get('attending') == 'yes')
    not_attending = sum(1 for r in rsvps if r.get('attending') == 'no')
    pending = len(guests) - len(rsvps)
    today = datetime.now().strftime('%Y-%m-%d')
    week_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    overdue = [t for t in todos if not t.get('archived') and not t.get('done') and t.get('due','') and t['due'] < today]
    this_week = [t for t in todos if not t.get('archived') and not t.get('done') and t.get('due','') and today <= t['due'] <= week_end]
    return jsonify({
        "total_guests": len(guests),
        "attending": attending,
        "not_attending": not_attending,
        "pending": pending,
        "todos_total": len(todos),
        "todos_done": sum(1 for t in todos if t.get('done')),
        "overdue_count": len(overdue),
        "overdue_tasks": overdue[:5],
        "this_week_count": len(this_week),
        "this_week_tasks": this_week[:5],
    })

if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), 'public'), exist_ok=True)
    print("Starting Ellie & David Wedding Site on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)