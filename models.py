from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id       = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    portfolios    = db.relationship('Portfolio', backref='owner', lazy=True)

    def get_id(self):
        return str(self.user_id)

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    portfolio_id = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    holdings     = db.relationship('Holding', backref='portfolio', lazy=True)

class Stock(db.Model):
    __tablename__ = 'stocks'
    stock_id     = db.Column(db.Integer, primary_key=True)
    symbol       = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    market       = db.Column(db.String(50), nullable=False)
    holdings     = db.relationship('Holding', backref='stock', lazy=True)

class Holding(db.Model):
    __tablename__ = 'holdings'
    holding_id   = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.portfolio_id'), nullable=False)
    stock_id     = db.Column(db.Integer, db.ForeignKey('stocks.stock_id'), nullable=False)
    total_quantity = db.Column(db.Float, default=0.0)
    average_price  = db.Column(db.Float, default=0.0)
    transactions   = db.relationship('Transaction', backref='holding', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    holding_id     = db.Column(db.Integer, db.ForeignKey('holdings.holding_id'), nullable=False)
    type           = db.Column(db.String(4), nullable=False)
    quantity       = db.Column(db.Float, nullable=False)
    price          = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

class Wallet(db.Model):
    __tablename__ = 'wallets'
    wallet_id  = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=False,
        unique=True
    )
    balance    = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user       = db.relationship(
        'User',
        backref=db.backref('wallet', uselist=False),
        lazy=True
    )