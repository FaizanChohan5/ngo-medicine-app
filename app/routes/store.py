from flask import Blueprint, render_template
from flask_login import login_required, current_user


# ============================================================
# STORE BLUEPRINT
# ============================================================

store = Blueprint(
    "store",
    __name__,
    url_prefix="/store"
)


# ============================================================
# STORE DASHBOARD
# ============================================================

@store.route("/dashboard")
@login_required
def dashboard():

    if current_user.role not in ["admin", "store"]:
        return "Access Denied", 403

    return render_template(
        "store/dashboard.html"
    )