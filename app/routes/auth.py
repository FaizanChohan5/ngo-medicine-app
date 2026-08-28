from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from app.models import User


auth = Blueprint("auth", __name__)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            if not user.is_active:
                flash("Your account is inactive")
                return redirect(url_for("auth.login"))

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid username or password")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))