from flask import Blueprint, request, jsonify
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from app.models import (
    db,
    User,
    Medicine,
    Stock,
    StockTransaction
)


# ============================================================
# API BLUEPRINT
# ============================================================

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# ============================================================
# HELPER
# ============================================================

def medicine_to_dict(medicine):

    stock_quantity = 0

    if medicine.stock:
        stock_quantity = medicine.stock.quantity

    return {
        "id": medicine.id,
        "name": medicine.name,
        "category": medicine.category,
        "unit": medicine.unit,
        "price": medicine.price,
        "is_active": medicine.is_active,
        "stock_quantity": stock_quantity
    }


# ============================================================
# API LOGIN
# ============================================================

@api.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:

        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    if not user.is_active:

        return jsonify({
            "success": False,
            "message": "This account is inactive."
        }), 403

    if not user.check_password(password):

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    login_user(user)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }), 200


# ============================================================
# API LOGOUT
# ============================================================

@api.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    return jsonify({
        "success": True,
        "message": "Logout successful."
    }), 200


# ============================================================
# CURRENT USER
# ============================================================

@api.route("/me", methods=["GET"])
@login_required
def me():

    return jsonify({
        "success": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role
        }
    }), 200


# ============================================================
# GET ALL MEDICINES
# ============================================================

@api.route("/medicines", methods=["GET"])
@login_required
def get_medicines():

    medicines = Medicine.query.order_by(
        Medicine.id.asc()
    ).all()

    medicine_list = [
        medicine_to_dict(medicine)
        for medicine in medicines
    ]

    return jsonify({
        "success": True,
        "count": len(medicine_list),
        "medicines": medicine_list
    }), 200


# ============================================================
# GET SINGLE MEDICINE
# ============================================================

@api.route("/medicines/<int:medicine_id>", methods=["GET"])
@login_required
def get_medicine(medicine_id):

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    return jsonify({
        "success": True,
        "medicine": medicine_to_dict(medicine)
    }), 200


# ============================================================
# ADD MEDICINE
# ADMIN ONLY
# ============================================================

@api.route("/medicines", methods=["POST"])
@login_required
def add_medicine():

    if current_user.role != "admin":

        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    unit = str(data.get("unit", "")).strip()

    price = data.get("price", 0)

    if not name:

        return jsonify({
            "success": False,
            "message": "Medicine name is required."
        }), 400

    if not unit:

        return jsonify({
            "success": False,
            "message": "Medicine unit is required."
        }), 400

    try:

        price = float(price)

        if price < 0:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Price must be a valid non-negative number."
        }), 400

    medicine = Medicine(
        name=name,
        category=category or None,
        unit=unit,
        price=price,
        is_active=True
    )

    db.session.add(medicine)

    db.session.flush()

    stock = Stock(
        medicine_id=medicine.id,
        quantity=0
    )

    db.session.add(stock)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Medicine added successfully.",
        "medicine": medicine_to_dict(medicine)
    }), 201


# ============================================================
# UPDATE MEDICINE
# ADMIN ONLY
# ============================================================

@api.route("/medicines/<int:medicine_id>", methods=["PUT"])
@login_required
def update_medicine(medicine_id):

    if current_user.role != "admin":

        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    if "name" in data:

        name = str(data["name"]).strip()

        if not name:

            return jsonify({
                "success": False,
                "message": "Medicine name cannot be empty."
            }), 400

        medicine.name = name

    if "category" in data:

        category = str(data["category"]).strip()

        medicine.category = category or None

    if "unit" in data:

        unit = str(data["unit"]).strip()

        if not unit:

            return jsonify({
                "success": False,
                "message": "Medicine unit cannot be empty."
            }), 400

        medicine.unit = unit

    if "price" in data:

        try:

            price = float(data["price"])

            if price < 0:
                raise ValueError

            medicine.price = price

        except (TypeError, ValueError):

            return jsonify({
                "success": False,
                "message": "Price must be a valid non-negative number."
            }), 400

    if "is_active" in data:

        medicine.is_active = bool(
            data["is_active"]
        )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Medicine updated successfully.",
        "medicine": medicine_to_dict(medicine)
    }), 200


# ============================================================
# GET ALL MAIN STORE STOCK
# ============================================================

@api.route("/stock", methods=["GET"])
@login_required
def get_stock():

    stocks = Stock.query.join(
        Medicine
    ).order_by(
        Medicine.name.asc()
    ).all()

    stock_list = []

    for stock in stocks:

        stock_list.append({
            "stock_id": stock.id,
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine.name,
            "category": stock.medicine.category,
            "unit": stock.medicine.unit,
            "quantity": stock.quantity,
            "is_active": stock.medicine.is_active
        })

    return jsonify({
        "success": True,
        "count": len(stock_list),
        "stock": stock_list
    }), 200


# ============================================================
# GET STOCK FOR ONE MEDICINE
# ============================================================

@api.route("/stock/<int:medicine_id>", methods=["GET"])
@login_required
def get_medicine_stock(medicine_id):

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    quantity = 0

    if medicine.stock:
        quantity = medicine.stock.quantity

    return jsonify({
        "success": True,
        "stock": {
            "medicine_id": medicine.id,
            "medicine_name": medicine.name,
            "unit": medicine.unit,
            "quantity": quantity
        }
    }), 200


# ============================================================
# RECEIVE STOCK
# ADMIN / STORE
# ============================================================

@api.route("/stock/receive", methods=["POST"])
@login_required
def receive_stock():

    if current_user.role not in ["admin", "store"]:

        return jsonify({
            "success": False,
            "message": "Admin or store access required."
        }), 403

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if medicine_id is None or quantity is None:

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity are required."
        }), 400

    try:

        medicine_id = int(medicine_id)
        quantity = int(quantity)

        if medicine_id <= 0 or quantity <= 0:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Medicine ID and quantity must be valid positive numbers."
        }), 400

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    if not medicine.is_active:

        return jsonify({
            "success": False,
            "message": "Cannot receive stock for an inactive medicine."
        }), 400

    stock = Stock.query.filter_by(
        medicine_id=medicine_id
    ).first()

    if not stock:

        stock = Stock(
            medicine_id=medicine_id,
            quantity=0
        )

        db.session.add(stock)

    stock.quantity += quantity

    transaction = StockTransaction(
        medicine_id=medicine_id,
        transaction_type="RECEIVE",
        quantity=quantity,
        user_id=current_user.id
    )

    db.session.add(transaction)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock received successfully.",
        "stock": {
            "medicine_id": medicine.id,
            "medicine_name": medicine.name,
            "quantity_added": quantity,
            "new_quantity": stock.quantity,
            "unit": medicine.unit
        }
    }), 200


# ============================================================
# ADD STOCK
# ADMIN ONLY
# ============================================================

@api.route("/stock/add", methods=["POST"])
@login_required
def add_stock():

    if current_user.role != "admin":

        return jsonify({
            "success": False,
            "message": "Only admin can add stock."
        }), 403

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if medicine_id is None or quantity is None:

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity are required."
        }), 400

    try:

        medicine_id = int(medicine_id)
        quantity = int(quantity)

        if medicine_id <= 0 or quantity <= 0:
            raise ValueError

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity must be valid positive numbers."
        }), 400

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    if not medicine.is_active:

        return jsonify({
            "success": False,
            "message": "This medicine is inactive."
        }), 400

    stock = Stock.query.filter_by(
        medicine_id=medicine_id
    ).first()

    if stock:

        stock.quantity += quantity

    else:

        stock = Stock(
            medicine_id=medicine_id,
            quantity=quantity
        )

        db.session.add(stock)

    transaction = StockTransaction(
        medicine_id=medicine_id,
        transaction_type="STOCK_IN",
        quantity=quantity,
        user_id=current_user.id
    )

    db.session.add(transaction)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock added successfully.",
        "stock": {
            "stock_id": stock.id,
            "medicine_id": medicine.id,
            "medicine_name": medicine.name,
            "quantity": stock.quantity,
            "unit": medicine.unit
        }
    }), 200


# ============================================================
# REMOVE STOCK
# ADMIN ONLY
# ============================================================

@api.route("/stock/remove", methods=["POST"])
@login_required
def remove_stock():

    if current_user.role != "admin":

        return jsonify({
            "success": False,
            "message": "Only admin can remove stock."
        }), 403

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if medicine_id is None or quantity is None:

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity are required."
        }), 400

    try:

        medicine_id = int(medicine_id)
        quantity = int(quantity)

        if medicine_id <= 0 or quantity <= 0:
            raise ValueError

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity must be valid positive numbers."
        }), 400

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    stock = Stock.query.filter_by(
        medicine_id=medicine_id
    ).first()

    if not stock:

        return jsonify({
            "success": False,
            "message": "Stock record not found."
        }), 404

    if stock.quantity < quantity:

        return jsonify({
            "success": False,
            "message": "Insufficient stock.",
            "available_quantity": stock.quantity
        }), 400

    stock.quantity -= quantity

    transaction = StockTransaction(
        medicine_id=medicine_id,
        transaction_type="STOCK_OUT",
        quantity=quantity,
        user_id=current_user.id
    )

    db.session.add(transaction)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock removed successfully.",
        "stock": {
            "stock_id": stock.id,
            "medicine_id": medicine.id,
            "medicine_name": medicine.name,
            "quantity": stock.quantity,
            "unit": medicine.unit
        }
    }), 200


# ============================================================
# ADJUST STOCK
# ADMIN ONLY
# ============================================================

@api.route("/stock/adjust", methods=["POST"])
@login_required
def adjust_stock():

    if current_user.role != "admin":

        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if medicine_id is None or quantity is None:

        return jsonify({
            "success": False,
            "message": "medicine_id and quantity are required."
        }), 400

    try:

        medicine_id = int(medicine_id)
        quantity = int(quantity)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Medicine ID and quantity must be valid integers."
        }), 400

    if medicine_id <= 0:

        return jsonify({
            "success": False,
            "message": "Medicine ID must be positive."
        }), 400

    if quantity < 0:

        return jsonify({
            "success": False,
            "message": "Stock quantity cannot be negative."
        }), 400

    medicine = Medicine.query.get(medicine_id)

    if not medicine:

        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    stock = Stock.query.filter_by(
        medicine_id=medicine_id
    ).first()

    if not stock:

        stock = Stock(
            medicine_id=medicine_id,
            quantity=0
        )

        db.session.add(stock)

    old_quantity = stock.quantity

    stock.quantity = quantity

    difference = quantity - old_quantity

    transaction = StockTransaction(
        medicine_id=medicine_id,
        transaction_type="ADJUST",
        quantity=difference,
        user_id=current_user.id
    )

    db.session.add(transaction)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock adjusted successfully.",
        "stock": {
            "medicine_id": medicine.id,
            "medicine_name": medicine.name,
            "old_quantity": old_quantity,
            "new_quantity": stock.quantity,
            "difference": difference,
            "unit": medicine.unit
        }
    }), 200


# ============================================================
# STOCK TRANSACTION HISTORY
# ============================================================

@api.route("/stock/transactions", methods=["GET"])
@login_required
def stock_transactions():

    transactions = (
        StockTransaction.query
        .order_by(
            StockTransaction.created_at.desc()
        )
        .all()
    )

    result = []

    for transaction in transactions:

        result.append({
            "id": transaction.id,
            "medicine_id": transaction.medicine_id,
            "medicine_name": (
                transaction.medicine.name
                if transaction.medicine
                else None
            ),
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "user_id": transaction.user_id,
            "username": (
                transaction.user.username
                if transaction.user
                else None
            ),
            "created_at": (
                transaction.created_at.isoformat()
                if transaction.created_at
                else None
            )
        })

    return jsonify({
        "success": True,
        "count": len(result),
        "transactions": result
    }), 200

# ============================================================
# DISPATCH STOCK TO FIELD PERSON
# ADMIN / STORE
# ============================================================

@api.route("/stock/dispatch", methods=["POST"])
@login_required
def dispatch_stock():

    if current_user.role not in ["admin", "store"]:
        return jsonify({
            "success": False,
            "message": "Admin or store access required."
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required."
        }), 400

    field_person_id = data.get("field_person_id")
    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if (
        field_person_id is None
        or medicine_id is None
        or quantity is None
    ):
        return jsonify({
            "success": False,
            "message": (
                "field_person_id, medicine_id and "
                "quantity are required."
            )
        }), 400

    try:
        field_person_id = int(field_person_id)
        medicine_id = int(medicine_id)
        quantity = int(quantity)

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": (
                "field_person_id, medicine_id and "
                "quantity must be valid integers."
            )
        }), 400

    if field_person_id <= 0 or medicine_id <= 0 or quantity <= 0:
        return jsonify({
            "success": False,
            "message": (
                "field_person_id, medicine_id and "
                "quantity must be greater than zero."
            )
        }), 400

    # --------------------------------------------------------
    # FIND FIELD PERSON
    # --------------------------------------------------------

    from app.models import FieldPerson, FieldStock, StockDispatch

    field_person = FieldPerson.query.get(field_person_id)

    if not field_person:
        return jsonify({
            "success": False,
            "message": "Field person not found."
        }), 404

    # --------------------------------------------------------
    # FIND MEDICINE
    # --------------------------------------------------------

    medicine = Medicine.query.get(medicine_id)

    if not medicine:
        return jsonify({
            "success": False,
            "message": "Medicine not found."
        }), 404

    if not medicine.is_active:
        return jsonify({
            "success": False,
            "message": "Cannot dispatch an inactive medicine."
        }), 400

    # --------------------------------------------------------
    # FIND MAIN STORE STOCK
    # --------------------------------------------------------

    stock = Stock.query.filter_by(
        medicine_id=medicine_id
    ).first()

    if not stock:
        return jsonify({
            "success": False,
            "message": "Main store stock record not found."
        }), 404

    # --------------------------------------------------------
    # CHECK AVAILABLE STOCK
    # --------------------------------------------------------

    if stock.quantity < quantity:
        return jsonify({
            "success": False,
            "message": "Insufficient main store stock.",
            "available_quantity": stock.quantity,
            "requested_quantity": quantity
        }), 400

    # --------------------------------------------------------
    # FIND / CREATE FIELD STOCK
    # --------------------------------------------------------

    field_stock = FieldStock.query.filter_by(
        field_person_id=field_person_id,
        medicine_id=medicine_id
    ).first()

    if field_stock:

        field_stock.quantity += quantity

    else:

        field_stock = FieldStock(
            field_person_id=field_person_id,
            medicine_id=medicine_id,
            quantity=quantity
        )

        db.session.add(field_stock)

    # --------------------------------------------------------
    # REMOVE FROM MAIN STORE
    # --------------------------------------------------------

    stock.quantity -= quantity

    # --------------------------------------------------------
    # CREATE DISPATCH RECORD
    # --------------------------------------------------------

    dispatch = StockDispatch(
        field_person_id=field_person_id,
        medicine_id=medicine_id,
        quantity=quantity
    )

    db.session.add(dispatch)

    # --------------------------------------------------------
    # CREATE TRANSACTION
    # --------------------------------------------------------

    transaction = StockTransaction(
        medicine_id=medicine_id,
        transaction_type="DISPATCHED",
        quantity=quantity,
        user_id=current_user.id
    )

    db.session.add(transaction)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Stock dispatched successfully.",
        "dispatch": {
            "dispatch_id": dispatch.id,
            "field_person_id": field_person_id,
            "medicine_id": medicine_id,
            "medicine_name": medicine.name,
            "quantity_dispatched": quantity,
            "main_store_quantity": stock.quantity,
            "field_person_quantity": field_stock.quantity,
            "unit": medicine.unit
        }
    }), 200

# ============================================================
# GET FIELD PERSON STOCK
# ============================================================

@api.route("/field-stock/<int:field_person_id>", methods=["GET"])
@login_required
def get_field_stock(field_person_id):

    from app.models import FieldPerson, FieldStock

    # --------------------------------------------------------
    # FIND FIELD PERSON
    # --------------------------------------------------------

    field_person = FieldPerson.query.get(field_person_id)

    if not field_person:
        return jsonify({
            "success": False,
            "message": "Field person not found."
        }), 404

    # --------------------------------------------------------
    # GET FIELD STOCK
    # --------------------------------------------------------

    stocks = (
        FieldStock.query
        .filter_by(field_person_id=field_person_id)
        .join(Medicine)
        .order_by(Medicine.name.asc())
        .all()
    )

    stock_list = []

    for stock in stocks:

        stock_list.append({
            "field_stock_id": stock.id,
            "field_person_id": stock.field_person_id,
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine.name,
            "category": stock.medicine.category,
            "unit": stock.medicine.unit,
            "quantity": stock.quantity,
            "is_active": stock.medicine.is_active
        })

    return jsonify({
        "success": True,
        "field_person_id": field_person_id,
        "field_person_name": field_person.user.full_name,
        "count": len(stock_list),
        "field_stock": stock_list
    }), 200