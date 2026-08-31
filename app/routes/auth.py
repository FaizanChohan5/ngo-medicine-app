from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required
)

from app.models import User


# ============================================================
# AUTH BLUEPRINT
# ============================================================

auth = Blueprint("auth", __name__)

login_manager = LoginManager()


# ============================================================
# USER LOADER
# ============================================================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ============================================================
# LOGIN
# ============================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.check_password(password):

            if not user.is_active:

                flash("Your account is inactive")

                return redirect(
                    url_for("auth.login")
                )

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid username or password")

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )


# ============================================================
# PWA SERVICE WORKER
# ============================================================

@auth.route("/service-worker.js")
def service_worker():

    return send_from_directory(
        "static",
        "service-worker.js",
        mimetype="application/javascript"
    )