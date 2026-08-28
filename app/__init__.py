from flask import Flask, redirect, url_for
from flask_login import login_required

from app.models import db
from app.routes.auth import auth, login_manager
from app.routes.admin import admin
from app.routes.store import store
from app.routes.field import field
from app.routes.medicine import medicine
from app.routes.inventory import inventory


def create_app():

    app = Flask(__name__)

    # ============================================================
    # APPLICATION CONFIGURATION
    # ============================================================

    app.config["SECRET_KEY"] = "ngo-medicine-secret-key-change-later"

    # ============================================================
    # DATABASE CONFIGURATION
    # ============================================================

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ngo_medicine.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ============================================================
    # INITIALIZE DATABASE
    # ============================================================

    db.init_app(app)

    # ============================================================
    # INITIALIZE FLASK-LOGIN
    # ============================================================

    login_manager.init_app(app)

    # Login page for unauthorized users
    login_manager.login_view = "auth.login"

    # ============================================================
    # REGISTER BLUEPRINTS
    # ============================================================

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(store)
    app.register_blueprint(field)
    app.register_blueprint(medicine)
    app.register_blueprint(inventory)

    # ============================================================
    # CREATE DATABASE TABLES
    # ============================================================

    with app.app_context():
        db.create_all()

    # ============================================================
    # HOME PAGE
    # ============================================================

    @app.route("/")
    def home():

        return """
        <h1>NGO Medicine Management System</h1>
        <a href="/login">Login</a>
        """

    # ============================================================
    # MAIN DASHBOARD ROUTER
    # ============================================================

    @app.route("/dashboard")
    @login_required
    def dashboard():

        from flask_login import current_user

        if current_user.role == "admin":

            return redirect(
                url_for("admin.dashboard")
            )

        elif current_user.role == "store":

            return redirect(
                url_for("store.dashboard")
            )

        elif current_user.role == "field":

            return redirect(
                url_for("field.dashboard")
            )

        return "Invalid user role", 403

    return app