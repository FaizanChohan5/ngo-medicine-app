from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.models import (
    db,
    Medicine,
    Stock,
    StockTransaction,
    FieldPerson,
    FieldStock,
    StockDispatch
)


# ============================================================
# INVENTORY BLUEPRINT
# ============================================================

inventory = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)


# ============================================================
# MAIN INVENTORY DASHBOARD
# ============================================================

@inventory.route("/")
@login_required
def dashboard():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    stocks = Stock.query.order_by(
        Stock.id.desc()
    ).all()

    return render_template(
        "inventory/dashboard.html",
        stocks=stocks
    )

# ============================================================
# FIELD PERSON STOCK
# ============================================================

@inventory.route("/field-stock")
@login_required
def field_stock():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    field_stocks = FieldStock.query.order_by(
        FieldStock.field_person_id.asc(),
        FieldStock.medicine_id.asc()
    ).all()

    return render_template(
        "inventory/field_stock.html",
        field_stocks=field_stocks
    )

# ============================================================
# RECEIVE STOCK
# ============================================================

@inventory.route(
    "/receive",
    methods=["GET", "POST"]
)
@login_required
def receive_stock():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    medicines = Medicine.query.filter_by(
        is_active=True
    ).order_by(
        Medicine.name.asc()
    ).all()

    if request.method == "POST":

        medicine_id = request.form.get(
            "medicine_id"
        )

        quantity = request.form.get(
            "quantity"
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not medicine_id or not quantity:

            flash(
                "Medicine and quantity are required"
            )

            return redirect(
                url_for(
                    "inventory.receive_stock"
                )
            )

        try:

            medicine_id = int(
                medicine_id
            )

            quantity = int(
                quantity
            )

        except ValueError:

            flash(
                "Invalid medicine or quantity"
            )

            return redirect(
                url_for(
                    "inventory.receive_stock"
                )
            )

        if quantity <= 0:

            flash(
                "Quantity must be greater than zero"
            )

            return redirect(
                url_for(
                    "inventory.receive_stock"
                )
            )

        # ----------------------------------------------------
        # FIND MEDICINE
        # ----------------------------------------------------

        medicine = db.session.get(
            Medicine,
            medicine_id
        )

        if not medicine:

            flash(
                "Medicine not found"
            )

            return redirect(
                url_for(
                    "inventory.receive_stock"
                )
            )

        # ----------------------------------------------------
        # FIND EXISTING MAIN STOCK
        # ----------------------------------------------------

        stock = Stock.query.filter_by(
            medicine_id=medicine_id
        ).first()

        # ----------------------------------------------------
        # CREATE STOCK IF IT DOES NOT EXIST
        # ----------------------------------------------------

        if not stock:

            stock = Stock(
                medicine_id=medicine_id,
                quantity=0
            )

            db.session.add(
                stock
            )

        # ----------------------------------------------------
        # ADD RECEIVED QUANTITY
        # ----------------------------------------------------

        stock.quantity += quantity

        # ----------------------------------------------------
        # RECORD TRANSACTION
        # ----------------------------------------------------

        transaction = StockTransaction(
            medicine_id=medicine_id,
            user_id=current_user.id,
            transaction_type="RECEIVED",
            quantity=quantity
        )

        db.session.add(
            transaction
        )

        db.session.commit()

        flash(
            f"{quantity} {medicine.unit}(s) of "
            f"{medicine.name} received successfully"
        )

        return redirect(
            url_for(
                "inventory.dashboard"
            )
        )

    return render_template(
        "inventory/receive.html",
        medicines=medicines
    )


# ============================================================
# STOCK HISTORY
# ============================================================

@inventory.route("/history")
@login_required
def history():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    transactions = StockTransaction.query.order_by(
        StockTransaction.created_at.desc()
    ).all()

    return render_template(
        "inventory/history.html",
        transactions=transactions
    )


# ============================================================
# DISPATCH STOCK TO FIELD PERSON
# ============================================================

@inventory.route(
    "/dispatch",
    methods=["GET", "POST"]
)
@login_required
def dispatch_stock():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    medicines = Medicine.query.filter_by(
        is_active=True
    ).order_by(
        Medicine.name.asc()
    ).all()

    field_persons = FieldPerson.query.all()

    if request.method == "POST":

        medicine_id = request.form.get(
            "medicine_id"
        )

        field_person_id = request.form.get(
            "field_person_id"
        )

        quantity = request.form.get(
            "quantity"
        )

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if (
            not medicine_id
            or not field_person_id
            or not quantity
        ):

            flash(
                "All fields are required"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        try:

            medicine_id = int(
                medicine_id
            )

            field_person_id = int(
                field_person_id
            )

            quantity = int(
                quantity
            )

        except ValueError:

            flash(
                "Invalid input"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        if quantity <= 0:

            flash(
                "Quantity must be greater than zero"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        # ----------------------------------------------------
        # FIND MEDICINE
        # ----------------------------------------------------

        medicine = db.session.get(
            Medicine,
            medicine_id
        )

        if not medicine:

            flash(
                "Medicine not found"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        # ----------------------------------------------------
        # FIND FIELD PERSON
        # ----------------------------------------------------

        field_person = db.session.get(
            FieldPerson,
            field_person_id
        )

        if not field_person:

            flash(
                "Field person not found"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        # ----------------------------------------------------
        # GET MAIN STOCK
        # ----------------------------------------------------

        stock = Stock.query.filter_by(
            medicine_id=medicine_id
        ).first()

        available = (
            stock.quantity
            if stock
            else 0
        )

        # ----------------------------------------------------
        # CHECK AVAILABLE STOCK
        # ----------------------------------------------------

        if available < quantity:

            flash(
                f"Insufficient stock. "
                f"Available: {available}"
            )

            return redirect(
                url_for(
                    "inventory.dispatch_stock"
                )
            )

        # ----------------------------------------------------
        # DEDUCT FROM MAIN STOCK
        # ----------------------------------------------------

        stock.quantity -= quantity

        # ----------------------------------------------------
        # FIND FIELD PERSON'S STOCK
        # ----------------------------------------------------

        field_stock = FieldStock.query.filter_by(
            field_person_id=field_person_id,
            medicine_id=medicine_id
        ).first()

        # ----------------------------------------------------
        # CREATE FIELD STOCK IF NEEDED
        # ----------------------------------------------------

        if not field_stock:

            field_stock = FieldStock(
                field_person_id=field_person_id,
                medicine_id=medicine_id,
                quantity=0
            )

            db.session.add(
                field_stock
            )

        # ----------------------------------------------------
        # ADD MEDICINE TO FIELD STOCK
        # ----------------------------------------------------

        field_stock.quantity += quantity

        # ----------------------------------------------------
        # RECORD DISPATCH
        # ----------------------------------------------------

        dispatch = StockDispatch(
            medicine_id=medicine_id,
            field_person_id=field_person_id,
            quantity=quantity
        )

        db.session.add(
            dispatch
        )

        # ----------------------------------------------------
        # RECORD STOCK TRANSACTION
        # ----------------------------------------------------

        transaction = StockTransaction(
            medicine_id=medicine_id,
            user_id=current_user.id,
            transaction_type="DISPATCHED",
            quantity=quantity
        )

        db.session.add(
            transaction
        )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.session.commit()

        flash(
            f"{quantity} {medicine.unit}(s) of "
            f"{medicine.name} dispatched successfully"
        )

        return redirect(
            url_for(
                "inventory.dashboard"
            )
        )

    return render_template(
        "inventory/dispatch.html",
        medicines=medicines,
        field_persons=field_persons
    )