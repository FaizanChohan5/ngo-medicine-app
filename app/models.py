# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

db = SQLAlchemy()


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    field_person = db.relationship(
        "FieldPerson",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    stock_transactions = db.relationship(
        "StockTransaction",
        back_populates="user"
    )

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):

        return f"<User {self.username}>"


# ============================================================
# FIELD PERSON
# ============================================================

class FieldPerson(db.Model):

    __tablename__ = "field_persons"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(50)
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    user = db.relationship(
        "User",
        back_populates="field_person"
    )

    shops = db.relationship(
        "Shop",
        back_populates="field_person"
    )

    field_stock = db.relationship(
        "FieldStock",
        back_populates="field_person"
    )

    dispatches = db.relationship(
        "StockDispatch",
        back_populates="field_person"
    )

    sales = db.relationship(
        "Sale",
        back_populates="field_person"
    )

    def __repr__(self):

        return f"<FieldPerson {self.id}>"


# ============================================================
# MEDICINE
# ============================================================

class Medicine(db.Model):

    __tablename__ = "medicines"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(100)
    )

    unit = db.Column(
        db.String(50),
        nullable=False
    )

    price = db.Column(
        db.Float,
        default=0
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    stock = db.relationship(
        "Stock",
        back_populates="medicine",
        uselist=False
    )

    field_stock = db.relationship(
        "FieldStock",
        back_populates="medicine"
    )

    stock_transactions = db.relationship(
        "StockTransaction",
        back_populates="medicine"
    )

    dispatches = db.relationship(
        "StockDispatch",
        back_populates="medicine"
    )

    sale_items = db.relationship(
        "SaleItem",
        back_populates="medicine"
    )

    def __repr__(self):

        return f"<Medicine {self.name}>"


# ============================================================
# MAIN STORE STOCK
# ============================================================

class Stock(db.Model):

    __tablename__ = "stocks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        unique=True,
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIP
    # --------------------------------------------------------

    medicine = db.relationship(
        "Medicine",
        back_populates="stock"
    )

    def __repr__(self):

        return (
            f"<Stock "
            f"Medicine={self.medicine_id} "
            f"Qty={self.quantity}>"
        )


# ============================================================
# FIELD PERSON STOCK
# ============================================================

class FieldStock(db.Model):

    __tablename__ = "field_stocks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    field_person_id = db.Column(
        db.Integer,
        db.ForeignKey("field_persons.id"),
        nullable=False
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    field_person = db.relationship(
        "FieldPerson",
        back_populates="field_stock"
    )

    medicine = db.relationship(
        "Medicine",
        back_populates="field_stock"
    )

    # --------------------------------------------------------
    # UNIQUE MEDICINE PER FIELD PERSON
    # --------------------------------------------------------

    __table_args__ = (
        db.UniqueConstraint(
            "field_person_id",
            "medicine_id",
            name="uq_field_person_medicine"
        ),
    )

    def __repr__(self):

        return (
            f"<FieldStock "
            f"FieldPerson={self.field_person_id} "
            f"Medicine={self.medicine_id} "
            f"Qty={self.quantity}>"
        )


# ============================================================
# STOCK TRANSACTION
# ============================================================

class StockTransaction(db.Model):

    __tablename__ = "stock_transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    transaction_type = db.Column(
        db.String(50),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    medicine = db.relationship(
        "Medicine",
        back_populates="stock_transactions"
    )

    user = db.relationship(
        "User",
        back_populates="stock_transactions"
    )

    def __repr__(self):

        return (
            f"<StockTransaction "
            f"{self.transaction_type} "
            f"Medicine={self.medicine_id}>"
        )


# ============================================================
# STOCK DISPATCH
# ============================================================

class StockDispatch(db.Model):

    __tablename__ = "stock_dispatches"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    field_person_id = db.Column(
        db.Integer,
        db.ForeignKey("field_persons.id"),
        nullable=False
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    dispatched_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    field_person = db.relationship(
        "FieldPerson",
        back_populates="dispatches"
    )

    medicine = db.relationship(
        "Medicine",
        back_populates="dispatches"
    )

    def __repr__(self):

        return (
            f"<StockDispatch "
            f"Medicine={self.medicine_id} "
            f"Qty={self.quantity}>"
        )


# ============================================================
# SHOP
# ============================================================

class Shop(db.Model):

    __tablename__ = "shops"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    owner_name = db.Column(
        db.String(150)
    )

    phone = db.Column(
        db.String(50)
    )

    address = db.Column(
        db.String(300)
    )

    field_person_id = db.Column(
        db.Integer,
        db.ForeignKey("field_persons.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # OPENING / PREVIOUS BALANCE
    # --------------------------------------------------------

    opening_balance = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    field_person = db.relationship(
        "FieldPerson",
        back_populates="shops"
    )

    sales = db.relationship(
        "Sale",
        back_populates="shop",
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "ShopPayment",
        back_populates="shop",
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return f"<Shop {self.name}>"


# ============================================================
# SALE
# ============================================================

class Sale(db.Model):

    __tablename__ = "sales"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    shop_id = db.Column(
        db.Integer,
        db.ForeignKey("shops.id"),
        nullable=False
    )

    field_person_id = db.Column(
        db.Integer,
        db.ForeignKey("field_persons.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    shop = db.relationship(
        "Shop",
        back_populates="sales"
    )

    field_person = db.relationship(
        "FieldPerson",
        back_populates="sales"
    )

    items = db.relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return f"<Sale {self.id}>"


# ============================================================
# SALE ITEM
# ============================================================

class SaleItem(db.Model):

    __tablename__ = "sale_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id"),
        nullable=False
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    rate = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    total = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    sale = db.relationship(
        "Sale",
        back_populates="items"
    )

    medicine = db.relationship(
        "Medicine",
        back_populates="sale_items"
    )

    def __repr__(self):

        return (
            f"<SaleItem "
            f"Sale={self.sale_id} "
            f"Medicine={self.medicine_id}>"
        )


# ============================================================
# SHOP PAYMENT
# ============================================================

class ShopPayment(db.Model):

    __tablename__ = "shop_payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    shop_id = db.Column(
        db.Integer,
        db.ForeignKey("shops.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    # --------------------------------------------------------
    # PAYMENT DATE & TIME
    # --------------------------------------------------------

    payment_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    notes = db.Column(
        db.String(300)
    )

    # --------------------------------------------------------
    # RELATIONSHIP
    # --------------------------------------------------------

    shop = db.relationship(
        "Shop",
        back_populates="payments"
    )

    def __repr__(self):

        return (
            f"<ShopPayment "
            f"Shop={self.shop_id} "
            f"Amount={self.amount} "
            f"Date={self.payment_date}>"
        )