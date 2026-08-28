from flask import Blueprint
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

    return """
    <h1>Store Dashboard</h1>

    <p>Welcome to Store Management</p>

    <hr>

    <h3>Store Modules</h3>

    <ul>
        <li>Receive Stock</li>
        <li>Main Stock</li>
        <li>Dispatch Stock</li>
        <li>Field Person Stock</li>
        <li>Stock History</li>
    </ul>

    <a href="/logout">Logout</a>
    """