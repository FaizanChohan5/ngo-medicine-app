# -*- coding: utf-8 -*-

from datetime import timedelta

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
    FieldPerson,
    Shop,
    Medicine,
    FieldStock,
    Sale,
    SaleItem,
    StockTransaction,
    ShopPayment
)


# ============================================================
# FIELD BLUEPRINT
# ============================================================

field = Blueprint(
    "field",
    __name__,
    url_prefix="/field"
)


# ============================================================
# UTC → PAKISTAN TIME
# ============================================================

def pakistan_time(dt):
    """
    Convert a UTC datetime to Pakistan Standard Time (UTC+5).

    Returns None if no datetime is provided.
    """

    if dt is None:
        return None

    return dt + timedelta(hours=5)


# ============================================================
# GET CURRENT FIELD PERSON
# ============================================================

def get_current_field_person():

    return FieldPerson.query.filter_by(
        user_id=current_user.id
    ).first()


# ============================================================
# FIELD PERSON DASHBOARD
# ============================================================

@field.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    return render_template(
        "field/dashboard.html",
        field_person=field_person,
        pakistan_time=pakistan_time
    )


# ============================================================
# MY STOCK
# ============================================================

@field.route("/stock")
@login_required
def my_stock():

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    stock = FieldStock.query.filter_by(
        field_person_id=field_person.id
    ).all()

    return render_template(
        "field/my_stock.html",
        field_person=field_person,
        stock=stock,
        pakistan_time=pakistan_time
    )


# ============================================================
# MY SHOPS
# ============================================================

@field.route("/shops")
@login_required
def my_shops():

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Shop.query.filter_by(
        field_person_id=field_person.id
    )

    if search:
        query = query.filter(
            Shop.name.ilike(
                f"%{search}%"
            )
        )

    shops = query.order_by(
        Shop.id.desc()
    ).all()

    return render_template(
        "field/my_shops.html",
        field_person=field_person,
        shops=shops,
        search=search,
        pakistan_time=pakistan_time
    )


# ============================================================
# SHOP DETAILS
# ============================================================

@field.route("/shops/<int:shop_id>")
@login_required
def shop_details(shop_id):

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    # --------------------------------------------------------
    # VERIFY SHOP OWNERSHIP
    # --------------------------------------------------------

    shop = Shop.query.filter_by(
        id=shop_id,
        field_person_id=field_person.id
    ).first()

    if shop is None:
        return "Shop not found or access denied", 404

    # --------------------------------------------------------
    # GET SALES
    # --------------------------------------------------------

    sales = Sale.query.filter_by(
        shop_id=shop.id
    ).order_by(
        Sale.id.desc()
    ).all()

    # --------------------------------------------------------
    # GET SALE ITEMS
    # --------------------------------------------------------

    sale_items = {}

    for sale in sales:

        sale_items[sale.id] = SaleItem.query.filter_by(
            sale_id=sale.id
        ).all()

    # --------------------------------------------------------
    # GET PAYMENTS
    # --------------------------------------------------------

    payments = ShopPayment.query.filter_by(
        shop_id=shop.id
    ).order_by(
        ShopPayment.id.desc()
    ).all()

    # --------------------------------------------------------
    # CALCULATE BALANCE
    # --------------------------------------------------------

    total_sales = sum(
        (sale.total_amount or 0)
        for sale in sales
    )

    total_payments = sum(
        (payment.amount or 0)
        for payment in payments
    )

    opening_balance = shop.opening_balance or 0

    outstanding_balance = (
        opening_balance
        + total_sales
        - total_payments
    )

    # Prevent negative display balance
    if outstanding_balance < 0:
        outstanding_balance = 0

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render_template(
        "field/shop_details.html",
        field_person=field_person,
        shop=shop,
        sales=sales,
        sale_items=sale_items,
        payments=payments,
        opening_balance=opening_balance,
        total_sales=total_sales,
        total_payments=total_payments,
        outstanding_balance=outstanding_balance,
        pakistan_time=pakistan_time
    )


# ============================================================
# ADD SHOP
# ============================================================

@field.route(
    "/shops/add",
    methods=["GET", "POST"]
)
@login_required
def add_shop():

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    # --------------------------------------------------------
    # PROCESS FORM
    # --------------------------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        owner_name = request.form.get(
            "owner_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:

            flash(
                "Shop name is required"
            )

            return redirect(
                url_for(
                    "field.add_shop"
                )
            )

        try:

            shop = Shop(
                name=name,
                owner_name=owner_name,
                phone=phone,
                address=address,
                field_person_id=field_person.id
            )

            db.session.add(shop)
            db.session.commit()

            flash(
                f"Shop '{name}' added successfully"
            )

            return redirect(
                url_for(
                    "field.my_shops"
                )
            )

        except Exception as e:

            db.session.rollback()

            print(
                "SHOP CREATION ERROR:",
                e
            )

            flash(
                "Error adding shop"
            )

            return redirect(
                url_for(
                    "field.add_shop"
                )
            )

    # --------------------------------------------------------
    # SHOW PAGE
    # --------------------------------------------------------

    return render_template(
        "field/add_shop.html",
        field_person=field_person,
        pakistan_time=pakistan_time
    )


# ============================================================
# NEW MULTI-MEDICINE SALE
# ============================================================

@field.route(
    "/shops/<int:shop_id>/sale",
    methods=["GET", "POST"]
)
@login_required
def new_sale(shop_id):

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    # --------------------------------------------------------
    # VERIFY SHOP
    # --------------------------------------------------------

    shop = Shop.query.filter_by(
        id=shop_id,
        field_person_id=field_person.id
    ).first()

    if shop is None:
        return "Shop not found or access denied", 404

    # --------------------------------------------------------
    # GET FIELD STOCK
    # --------------------------------------------------------

    field_stock = FieldStock.query.filter(
        FieldStock.field_person_id == field_person.id,
        FieldStock.quantity > 0
    ).all()

    # --------------------------------------------------------
    # PROCESS SALE
    # --------------------------------------------------------

    if request.method == "POST":

        medicine_ids = request.form.getlist(
            "medicine_id"
        )

        quantities = request.form.getlist(
            "quantity"
        )

        rates = request.form.getlist(
            "rate"
        )

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not medicine_ids:

            flash(
                "Please add at least one medicine"
            )

            return redirect(
                url_for(
                    "field.new_sale",
                    shop_id=shop.id
                )
            )

        if not (
            len(medicine_ids)
            == len(quantities)
            == len(rates)
        ):

            flash(
                "Invalid sale data"
            )

            return redirect(
                url_for(
                    "field.new_sale",
                    shop_id=shop.id
                )
            )

        sale_items_data = []
        grand_total = 0.0

        try:

            # =================================================
            # VALIDATE ALL ITEMS FIRST
            # =================================================

            for index in range(
                len(medicine_ids)
            ):

                try:

                    medicine_id = int(
                        medicine_ids[index]
                    )

                    quantity = int(
                        quantities[index]
                    )

                    rate = float(
                        rates[index]
                    )

                except (TypeError, ValueError):

                    raise ValueError(
                        "Invalid medicine, quantity or rate"
                    )

                # ---------------------------------------------
                # VALIDATE QUANTITY
                # ---------------------------------------------

                if quantity <= 0:

                    raise ValueError(
                        "Quantity must be greater than zero"
                    )

                # ---------------------------------------------
                # VALIDATE RATE
                # ---------------------------------------------

                if rate < 0:

                    raise ValueError(
                        "Rate cannot be negative"
                    )

                # ---------------------------------------------
                # GET MEDICINE
                # ---------------------------------------------

                medicine = db.session.get(
                    Medicine,
                    medicine_id
                )

                if medicine is None:

                    raise ValueError(
                        "Medicine not found"
                    )

                # ---------------------------------------------
                # GET FIELD STOCK
                # ---------------------------------------------

                stock = FieldStock.query.filter_by(
                    field_person_id=field_person.id,
                    medicine_id=medicine_id
                ).first()

                if stock is None:

                    raise ValueError(
                        f"{medicine.name} is not available "
                        "in field stock"
                    )

                # ---------------------------------------------
                # CHECK STOCK
                # ---------------------------------------------

                if stock.quantity < quantity:

                    raise ValueError(
                        f"Insufficient stock for "
                        f"{medicine.name}. "
                        f"Available: {stock.quantity}"
                    )

                # ---------------------------------------------
                # CALCULATE ITEM TOTAL
                # ---------------------------------------------

                item_total = quantity * rate

                sale_items_data.append({
                    "medicine_id": medicine.id,
                    "stock": stock,
                    "quantity": quantity,
                    "rate": rate,
                    "total": item_total
                })

                grand_total += item_total

            # =================================================
            # CREATE SALE
            # =================================================

            sale = Sale(
                shop_id=shop.id,
                field_person_id=field_person.id,
                total_amount=grand_total
            )

            db.session.add(sale)

            # Get generated sale ID
            db.session.flush()

            # =================================================
            # CREATE SALE ITEMS
            # DEDUCT STOCK
            # CREATE TRANSACTIONS
            # =================================================

            for item in sale_items_data:

                sale_item = SaleItem(
                    sale_id=sale.id,
                    medicine_id=item["medicine_id"],
                    quantity=item["quantity"],
                    rate=item["rate"],
                    total=item["total"]
                )

                db.session.add(
                    sale_item
                )

                # Deduct field stock
                item["stock"].quantity -= (
                    item["quantity"]
                )

                # Create stock transaction
                transaction = StockTransaction(
                    medicine_id=item["medicine_id"],
                    transaction_type="SALE",
                    quantity=item["quantity"],
                    user_id=current_user.id
                )

                db.session.add(
                    transaction
                )

            # -------------------------------------------------
            # COMMIT
            # -------------------------------------------------

            db.session.commit()

            flash(
                f"Sale completed successfully. "
                f"Total: Rs {grand_total:,.2f}"
            )

            return redirect(
                url_for(
                    "field.shop_details",
                    shop_id=shop.id
                )
            )

        except ValueError as e:

            db.session.rollback()

            flash(
                str(e)
            )

            return redirect(
                url_for(
                    "field.new_sale",
                    shop_id=shop.id
                )
            )

        except Exception as e:

            db.session.rollback()

            print(
                "MULTI SALE ERROR:",
                e
            )

            flash(
                "Sale could not be completed"
            )

            return redirect(
                url_for(
                    "field.new_sale",
                    shop_id=shop.id
                )
            )

    # --------------------------------------------------------
    # SHOW SALE PAGE
    # --------------------------------------------------------

    return render_template(
        "field/new_sale.html",
        field_person=field_person,
        shop=shop,
        field_stock=field_stock,
        pakistan_time=pakistan_time
    )


# ============================================================
# ADD SHOP PAYMENT
# ============================================================

@field.route(
    "/shops/<int:shop_id>/payment",
    methods=["POST"]
)
@login_required
def add_payment(shop_id):

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    # --------------------------------------------------------
    # VERIFY SHOP
    # --------------------------------------------------------

    shop = Shop.query.filter_by(
        id=shop_id,
        field_person_id=field_person.id
    ).first()

    if shop is None:
        return "Shop not found or access denied", 404

    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    amount_raw = request.form.get(
        "amount",
        ""
    ).strip()

    notes = request.form.get(
        "notes",
        ""
    ).strip()

    # --------------------------------------------------------
    # VALIDATE AMOUNT
    # --------------------------------------------------------

    try:

        amount = float(
            amount_raw
        )

    except (TypeError, ValueError):

        flash(
            "Please enter a valid payment amount"
        )

        return redirect(
            url_for(
                "field.shop_details",
                shop_id=shop.id
            )
        )

    if amount <= 0:

        flash(
            "Payment amount must be greater than zero"
        )

        return redirect(
            url_for(
                "field.shop_details",
                shop_id=shop.id
            )
        )

    # --------------------------------------------------------
    # CALCULATE CURRENT BALANCE
    # --------------------------------------------------------

    total_sales = db.session.query(
        db.func.coalesce(
            db.func.sum(
                Sale.total_amount
            ),
            0
        )
    ).filter(
        Sale.shop_id == shop.id
    ).scalar() or 0

    total_payments = db.session.query(
        db.func.coalesce(
            db.func.sum(
                ShopPayment.amount
            ),
            0
        )
    ).filter(
        ShopPayment.shop_id == shop.id
    ).scalar() or 0

    opening_balance = shop.opening_balance or 0

    outstanding_balance = (
        opening_balance
        + total_sales
        - total_payments
    )

    # --------------------------------------------------------
    # NO OUTSTANDING BALANCE
    # --------------------------------------------------------

    if outstanding_balance <= 0:

        flash(
            "This shop has no outstanding balance"
        )

        return redirect(
            url_for(
                "field.shop_details",
                shop_id=shop.id
            )
        )

    # --------------------------------------------------------
    # PREVENT OVERPAYMENT
    # --------------------------------------------------------

    if amount > outstanding_balance:

        flash(
            f"Payment cannot exceed outstanding balance "
            f"of Rs {outstanding_balance:,.2f}"
        )

        return redirect(
            url_for(
                "field.shop_details",
                shop_id=shop.id
            )
        )

    # --------------------------------------------------------
    # CREATE PAYMENT
    # --------------------------------------------------------

    try:

        payment = ShopPayment(
            shop_id=shop.id,
            amount=amount,
            notes=notes
        )

        db.session.add(
            payment
        )

        db.session.commit()

        flash(
            f"Payment of Rs {amount:,.2f} "
            f"recorded successfully"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "SHOP PAYMENT ERROR:",
            e
        )

        flash(
            "Payment could not be recorded"
        )

    return redirect(
        url_for(
            "field.shop_details",
            shop_id=shop.id
        )
    )


# ============================================================
# SALES HISTORY
# ============================================================

@field.route("/sales")
@login_required
def sales_history():

    if current_user.role != "field":
        return "Access Denied", 403

    field_person = get_current_field_person()

    if field_person is None:
        return "Field Person profile not found", 404

    # --------------------------------------------------------
    # GET SALES
    # --------------------------------------------------------

    sales = Sale.query.filter_by(
        field_person_id=field_person.id
    ).order_by(
        Sale.id.desc()
    ).all()

    # --------------------------------------------------------
    # GET SALE ITEMS
    # --------------------------------------------------------

    sale_items = {}

    for sale in sales:

        sale_items[sale.id] = SaleItem.query.filter_by(
            sale_id=sale.id
        ).all()

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render_template(
        "field/sales.html",
        sales=sales,
        sale_items=sale_items,
        field_person=field_person,
        pakistan_time=pakistan_time
    )