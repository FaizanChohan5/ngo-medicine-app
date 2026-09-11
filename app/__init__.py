from flask import Flask, redirect, url_for, request
import os
from flask_login import login_required, current_user

from app.models import db
from app.routes.auth import auth, login_manager
from app.routes.admin import admin
from app.routes.store import store
from app.routes.field import field
from app.routes.medicine import medicine
from app.routes.inventory import inventory
from app.routes.api import api


def create_app():

    app = Flask(__name__)

    # ============================================================
    # APPLICATION CONFIGURATION
    # ============================================================

    app.config["SECRET_KEY"] = "b134cd22b05a8711d178dfd672427e5d4095584f8eb5f7233389c7a0efae350d"

    # Session cookie security
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Keep False while using local HTTP.
    # Change to True after HTTPS deployment.
    app.config["SESSION_COOKIE_SECURE"] = False

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
    app.register_blueprint(api)

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
<h1>V-Tag Medicine Management System</h1>
<a href="https://v-tag-medicine-management.onrender.com/login">Login</a>
"""

    # ============================================================
    # MAIN DASHBOARD ROUTER
    # ============================================================

    @app.route("/dashboard")
    @login_required
    def dashboard():

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

    # ============================================================
    # TEMPORARY ADMIN SETUP
    # ============================================================

    @app.route("/setup-admin")
    def setup_admin():

        setup_key = request.args.get("key")

        if setup_key != os.environ.get("ADMIN_SETUP_KEY"):
            return "Unauthorized", 401

        from app.models import User

        user = User.query.filter_by(username="admin").first()

        if user:

            user.set_password("Admin@12345")
            user.role = "admin"
            user.full_name = "Administrator"
            user.is_active = True

        else:

            user = User(
                username="admin",
                role="admin",
                full_name="Administrator",
                is_active=True
            )

            user.set_password("Admin@12345")
            db.session.add(user)

        db.session.commit()

        return "Admin setup completed successfully."

    # ============================================================
    # RETURN APPLICATION
    # ============================================================

    return app