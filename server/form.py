from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, RadioField, IntegerField, DecimalField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=64)])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), Length(min=0, max=64), EqualTo("password")])
    submit = SubmitField("Register")

class AccountForm(FlaskForm):
    accnt_name = StringField("Account Name: ", validators=[InputRequired(), Length(min=5, max=32)])
    accnt_type = RadioField("Account Type: ", choices=[("Checking", "Checking"), ("Savings", "Savings")], validators=[InputRequired()])
    submit = SubmitField("Create Account")

class TransferForm(FlaskForm):
    to_accnt = IntegerField("To: ", validators=[InputRequired()])
    from_accnt = IntegerField("From: ", validators=[InputRequired()])
    amt = DecimalField("Amount: ", places=2, validators=[InputRequired(), NumberRange(min=0.01)])
    description = StringField("Description", validators=[Length(max=128)])
    submit = SubmitField("Transfer")

class DepositForm(FlaskForm):
    to_accnt = IntegerField("To: ", validators=[InputRequired()])
    amt = DecimalField("Amount: ", places=2, validators=[InputRequired(), NumberRange(min=0.01)])
    submit = SubmitField("Deposit")
