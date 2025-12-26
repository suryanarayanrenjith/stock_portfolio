from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Portfolio, Stock, Holding, Transaction, Stock, Wallet
from forms import SignupForm, LoginForm, PortfolioForm, TransactionForm, StockForm, WalletForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
import yfinance as yf

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing = User.query.filter(
            or_(
              User.username == form.username.data,
              User.email    == form.email.data
            )
        ).first()
        if existing:
            flash('That username or email is already taken. Please choose another.')
            return render_template('signup.html', form=form), 409

        u = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Unexpected error: could not create account. Try again.')
            return render_template('signup.html', form=form), 500

        flash('Account created! Please log in.')
        return redirect(url_for('main.login'))

    return render_template('signup.html', form=form)

@bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('main.portfolios'))
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/portfolios', methods=['GET','POST'])
@login_required
def portfolios():
    form = PortfolioForm()
    if form.validate_on_submit():
        p = Portfolio(user_id=current_user.user_id, name=form.name.data)
        db.session.add(p); db.session.commit()
        return redirect(url_for('main.portfolios'))
    all_ports = Portfolio.query.filter_by(user_id=current_user.user_id).all()
    return render_template('portfolios.html', form=form, portfolios=all_ports)

@bp.route('/transactions', methods=['GET','POST'])
@login_required
def transactions():
    form = TransactionForm()
    form.portfolio.choices = [
        (p.portfolio_id, p.name)
        for p in current_user.portfolios
    ]

    form.stock.choices = [
        (s.stock_id, f"{s.symbol} – {s.company_name}")
        for s in Stock.query.order_by(Stock.symbol).all()
    ]

    if form.validate_on_submit():
        p_id, s_id = form.portfolio.data, form.stock.data
        txn_type, qty, price = form.type.data, form.quantity.data, form.price.data
        cost = qty * price
        wallet = current_user.wallet

        h = Holding.query.filter_by(portfolio_id=p_id, stock_id=s_id).first()
        if not h:
            h = Holding(portfolio_id=p_id, stock_id=s_id,
                        total_quantity=0.0, average_price=0.0)
            db.session.add(h); db.session.flush()

        if txn_type == 'buy':
            if wallet.balance < cost:
                flash("Insufficient wallet balance for this purchase.", "danger")
                return render_template('transactions.html', form=form, transactions=[])

            wallet.balance -= cost
            db.session.add(wallet)

            if h.total_quantity == 0:
                h.total_quantity  = qty
                h.average_price   = price
            else:
                prev_cost = h.average_price * h.total_quantity
                new_cost  = prev_cost + cost
                h.total_quantity += qty
                h.average_price  = new_cost / h.total_quantity

        else:
            revenue = cost
            wallet.balance += revenue
            db.session.add(wallet)
            h.total_quantity -= qty

        t = Transaction(holding_id=h.holding_id, type=txn_type,
                        quantity=qty, price=price)
        db.session.add(t)
        db.session.commit()

        flash("Transaction recorded.", "success")
        return redirect(url_for('main.transactions'))

    txs = (Transaction.query
           .join(Holding).join(Portfolio)
           .filter(Portfolio.user_id==current_user.user_id)
           .order_by(Transaction.transaction_date.desc())
           .all())
    return render_template('transactions.html', form=form, transactions=txs)

@bp.route('/holdings/<int:portfolio_id>')
@login_required
def holdings(portfolio_id):
    hlist = Holding.query.filter_by(portfolio_id=portfolio_id).all()

    for h in hlist:
        ticker = yf.Ticker(h.stock.symbol)
        info = ticker.fast_info if hasattr(ticker, 'fast_info') else ticker.info
        current_price = info.get('last_price') or info.get('regularMarketPrice')

        h.current_price = current_price or 0.0
        h.current_value = h.current_price * h.total_quantity

    return render_template('holdings.html', holdings=hlist)

@bp.route('/stocks')
@login_required
def stocks():
    """List all stocks."""
    all_stocks = Stock.query.order_by(Stock.symbol).all()
    return render_template('stocks.html', stocks=all_stocks)

@bp.route('/stocks/create', methods=['GET','POST'])
@login_required
def create_stock():
    """Add a new stock symbol to the system."""
    form = StockForm()
    if form.validate_on_submit():
        s = Stock(
            symbol       = form.symbol.data.upper(),
            company_name = form.company_name.data,
            market       = form.market.data.upper()
        )
        db.session.add(s)
        try:
            db.session.commit()
            flash(f"Stock {s.symbol} added.", 'success')
            return redirect(url_for('main.stocks'))
        except IntegrityError:
            db.session.rollback()
            flash('That symbol already exists.', 'warning')
    return render_template('create_stock.html', form=form)

@bp.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    w = current_user.wallet
    if w is None:
        w = Wallet(user_id=current_user.user_id, balance=0.0)
        db.session.add(w)
        db.session.commit()

    form = WalletForm()
    if form.validate_on_submit():
        amt = form.amount.data
        if form.action.data == 'withdraw' and amt > w.balance:
            flash('Insufficient funds to withdraw.', 'warning')
        else:
            w.balance += amt if form.action.data=='deposit' else -amt
            db.session.add(w)
            db.session.commit()
            flash(f"{form.action.data.title()} of ${amt:.2f} successful.", 'success')
        return redirect(url_for('main.wallet'))

    return render_template('wallet.html', wallet=w, form=form)