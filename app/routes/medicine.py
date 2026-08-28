from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.models import db, Medicine


# ============================================================
# MEDICINE BLUEPRINT
# ============================================================

medicine = Blueprint(
    "medicine",
    __name__,
    url_prefix="/medicine"
)


# ============================================================
# MEDICINE LIST
# ============================================================

@medicine.route("/")
@login_required
def list_medicines():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    medicines = Medicine.query.order_by(
        Medicine.name.asc()
    ).all()

    return render_template(
        "medicines/list.html",
        medicines=medicines
    )


# ============================================================
# ADD MEDICINE
# ============================================================

@medicine.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_medicine():

    if current_user.role != "admin":
        return "Access Denied", 403

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        unit = request.form.get(
            "unit",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        ).strip()

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if not name or not unit:

            flash(
                "Medicine name and unit are required"
            )

            return redirect(
                url_for(
                    "medicine.add_medicine"
                )
            )

        # ----------------------------------------------------
        # CHECK DUPLICATE MEDICINE
        # ----------------------------------------------------

        existing = Medicine.query.filter_by(
            name=name
        ).first()

        if existing:

            flash(
                "Medicine already exists"
            )

            return redirect(
                url_for(
                    "medicine.add_medicine"
                )
            )

        # ----------------------------------------------------
        # VALIDATE PRICE
        # ----------------------------------------------------

        try:

            price_value = float(
                price or 0
            )

        except ValueError:

            flash(
                "Price must be a valid number"
            )

            return redirect(
                url_for(
                    "medicine.add_medicine"
                )
            )

        if price_value < 0:

            flash(
                "Price cannot be negative"
            )

            return redirect(
                url_for(
                    "medicine.add_medicine"
                )
            )

        # ----------------------------------------------------
        # CREATE MEDICINE
        # ----------------------------------------------------

        medicine_obj = Medicine(
            name=name,
            category=category,
            unit=unit,
            price=price_value
        )

        db.session.add(
            medicine_obj
        )

        db.session.commit()

        flash(
            "Medicine added successfully"
        )

        return redirect(
            url_for(
                "medicine.list_medicines"
            )
        )

    return render_template(
        "medicines/add.html"
    )


# ============================================================
# EDIT MEDICINE
# ============================================================

@medicine.route(
    "/edit/<int:medicine_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_medicine(medicine_id):

    # --------------------------------------------------------
    # ONLY ADMIN CAN EDIT MEDICINES
    # --------------------------------------------------------

    if current_user.role != "admin":

        return "Access Denied", 403

    # --------------------------------------------------------
    # GET MEDICINE
    # --------------------------------------------------------

    medicine_obj = db.session.get(
        Medicine,
        medicine_id
    )

    if not medicine_obj:

        flash(
            "Medicine not found"
        )

        return redirect(
            url_for(
                "medicine.list_medicines"
            )
        )

    # --------------------------------------------------------
    # PROCESS FORM
    # --------------------------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        unit = request.form.get(
            "unit",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        ).strip()

        is_active = request.form.get(
            "is_active"
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if not name or not unit:

            flash(
                "Medicine name and unit are required"
            )

            return redirect(
                url_for(
                    "medicine.edit_medicine",
                    medicine_id=medicine_id
                )
            )

        # ----------------------------------------------------
        # CHECK DUPLICATE NAME
        # ----------------------------------------------------

        existing = Medicine.query.filter(
            Medicine.name == name,
            Medicine.id != medicine_id
        ).first()

        if existing:

            flash(
                "Another medicine with this name already exists"
            )

            return redirect(
                url_for(
                    "medicine.edit_medicine",
                    medicine_id=medicine_id
                )
            )

        # ----------------------------------------------------
        # VALIDATE PRICE
        # ----------------------------------------------------

        try:

            price_value = float(
                price or 0
            )

        except ValueError:

            flash(
                "Price must be a valid number"
            )

            return redirect(
                url_for(
                    "medicine.edit_medicine",
                    medicine_id=medicine_id
                )
            )

        if price_value < 0:

            flash(
                "Price cannot be negative"
            )

            return redirect(
                url_for(
                    "medicine.edit_medicine",
                    medicine_id=medicine_id
                )
            )

        # ----------------------------------------------------
        # UPDATE MEDICINE
        # ----------------------------------------------------

        medicine_obj.name = name

        medicine_obj.category = category

        medicine_obj.unit = unit

        medicine_obj.price = price_value

        medicine_obj.is_active = (
            is_active == "on"
        )

        db.session.commit()

        flash(
            f"Medicine '{medicine_obj.name}' "
            f"updated successfully"
        )

        return redirect(
            url_for(
                "medicine.list_medicines"
            )
        )

    # --------------------------------------------------------
    # SHOW EDIT PAGE
    # --------------------------------------------------------

    return render_template(
        "medicines/edit.html",
        medicine=medicine_obj
    )