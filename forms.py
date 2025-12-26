from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class SignupForm(FlaskForm):
    username = StringField(
        'Username', 
        validators=[
            DataRequired(message='Username is required'), 
            Length(min=1, max=64, message='Username must be between 1 and 64 characters')
        ]
    )
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message='Email is required'), 
            Email(message='Invalid email address')
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(message='Password is required'), 
            Length(min=6, max=128, message='Password must be between 6 and 128 characters')
        ]
    )
    password2 = PasswordField(
        'Repeat Password', 
        validators=[
            DataRequired(message='Please confirm your password'), 
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message='Email is required'), 
            Email(message='Invalid email address')
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[DataRequired(message='Password is required')]
    )
    submit = SubmitField('Log In')

class PortfolioForm(FlaskForm):
    name = StringField(
        'Portfolio Name', 
        validators=[
            DataRequired(message='Portfolio name is required'), 
            Length(min=1, max=100, message='Must be between 1 and 100 characters')
        ]
    )
    submit = SubmitField('Create')

class StockForm(FlaskForm):
    symbol = StringField(
        'Symbol', 
        validators=[
            DataRequired(message='Stock symbol is required'), 
            Length(min=1, max=10, message='Symbol must be between 1 and 10 characters')
        ]
    )
    company_name = StringField(
        'Company Name', 
        validators=[
            DataRequired(message='Company name is required'), 
            Length(min=1, max=120, message='Company Name must be between 1 and 120 characters')
        ]
    )
    market = StringField(
        'Market (e.g. NASDAQ)', 
        validators=[
            DataRequired(message='Market is required'), 
            Length(min=1, max=50, message='Market must be between 1 and 50 characters')
        ]
    )
    submit = SubmitField('Add Stock')

class TransactionForm(FlaskForm):
    portfolio = SelectField(
        'Portfolio', 
        coerce=int, 
        validators=[DataRequired(message='Select a portfolio')]
    )
    stock = SelectField(
        'Stock', 
        coerce=int, 
        validators=[DataRequired(message='Select a stock')]
    )
    type = SelectField(
        'Type', 
        choices=[('buy','Buy'), ('sell','Sell')], 
        validators=[DataRequired(message='Select transaction type')]
    )
    quantity = FloatField(
        'Quantity', 
        validators=[DataRequired(message='Enter quantity')]
    )
    price = FloatField(
        'Price per Share', 
        validators=[DataRequired(message='Enter price per share')]
    )
    submit = SubmitField('Record')

class WalletForm(FlaskForm):
    amount = FloatField(
        'Amount', 
        validators=[DataRequired(message='Enter an amount')]
    )
    action = SelectField(
        'Action', 
        choices=[('deposit','Deposit'), ('withdraw','Withdraw')], 
        validators=[DataRequired(message='Select an action')]
    )
    submit = SubmitField('Submit')