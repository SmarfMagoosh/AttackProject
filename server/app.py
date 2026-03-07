from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from form import LoginForm, RegisterForm, AccountForm, TransferForm, DepositForm
from argon2 import PasswordHasher
import datetime
import os

app = Flask(__name__)
scriptdir = os.path.dirname(os.path.abspath(__file__))
dbfile = os.path.join(scriptdir, "db.sqlite3")
hasher = PasswordHasher()

with open("key.txt", "r") as f:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SECRET_KEY'] = f.read()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    accounts = db.relationship("Account", backref="user", lazy=True)


class Account(db.Model):
    __tablename__ = "accounts"
    account_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Integer, db.ForeignKey("users.username"), nullable=False)
    account_name = db.Column(db.String(50), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    transfers_from = db.relationship(
        "Transfer",
        foreign_keys="Transfer.from_account",
        backref="sender",
        lazy=True
    )
    transfers_to = db.relationship(
        "Transfer",
        foreign_keys="Transfer.to_account",
        backref="receiver",
        lazy=True
    )


class Transfer(db.Model):
    __tablename__ = "transfers"
    transfer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_account = db.Column(db.Integer, db.ForeignKey("accounts.account_number"))
    to_account = db.Column(db.Integer, db.ForeignKey("accounts.account_number"))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(255), default="")
    time = db.Column(db.DateTime)
    
with app.app_context():
    db.create_all()

@app.get("/")
def get_index():
    return redirect("/login/")

@app.get("/login/")
def get_login():
    return render_template("login.html", form=LoginForm())

@app.get("/register/")
def get_register():
    return render_template("register.html", form=RegisterForm())

@app.get("/home/")
def get_home():
    username = session.get("username")
    if not username:
        return redirect(url_for("get_login"))
    else:
        user = db.session.get(User, username)
        if not user:
            return redirect(url_for("get_login"))
        accounts = Account.query.filter_by(username=user.username).all()
        return render_template("home.html", user=user, accounts=accounts, aform=AccountForm(), tform=TransferForm(), dform=DepositForm())

@app.get("/account/<int:account_number>")
def get_account(account_number):
    username = session.get("username")
    if not username:
        return redirect(url_for("get_login"))
    
    account = db.session.get(Account, account_number)
    if not account:
        return redirect(url_for("get_home"))
    
    transfers = db.session.query(Transfer).where(or_(
        Transfer.from_account == account_number,
        Transfer.to_account == account_number
    ))
    return render_template("account.html", account=account, transfers=transfers)

@app.get("/logout/")
def get_logout():
    session["username"] = None
    return redirect(url_for("get_login"))

@app.post("/login/")
def post_login():
    form = LoginForm()
    if form.validate():
        user = db.session.get(User, form.username.data)

        # if the user name didn't exist send them back
        if user is None:
            flash(f"That username or password was incorrect")
            return redirect(url_for("get_login"))
        
        # if that password doesn't match send them back
        if hasher.verify(user.password, form.password.data):
            session["username"] = user.username
            return redirect(url_for("get_home"))
        else:
            flash(f"That username or password was incorrect")
            return redirect(url_for("get_login"))
    # if the form contained errors send them back
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

@app.post("/register/")
def post_register():
    form = RegisterForm()
    if form.validate():
        username = form.username.data
        if db.session.get(User, username):
            flash("Sorry, that username has already been taken")
            return redirect(url_for("get_register"))

        user = User(
            username = form.username.data,
            password = hasher.hash(form.password.data),
            first_name = form.first_name.data,
            last_name = form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        session["username"] = form.username.data
        return redirect(url_for("get_home"))
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

@app.post("/new_account/")
def post_new_account():
    username = session.get("username")
    if not username:
        return redirect(url_for("get_login"))
    
    form = AccountForm()
    if form.validate():
        account = Account(
            username=username,
            account_name=form.accnt_name.data,
            account_type=form.accnt_type.data
        )
        db.session.add(account)
        db.session.commit()
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
    return redirect(url_for("get_home"))

@app.post("/transfer/")
def post_transfer():
    username = session.get("username")
    if not username:
        return redirect(url_for("get_login"))
    
    form = TransferForm()
    if form.validate():
        from_accnt = db.session.get(Account, form.from_accnt.data)
        to_accnt = db.session.get(Account, form.to_accnt.data)
        valid = (
            (from_accnt is not None) and 
            (to_accnt is not None) and 
            from_accnt.username == username and 
            from_accnt.balance >= form.amt.data
        )
        if not valid:
            flash("Error in completing transfer. Double check the account numbers, and make sure you aren't transferring more than the current balance.")
        else:
            transfer = Transfer(
                from_account=from_accnt.account_number,
                to_account=to_accnt.account_number,
                amount=form.amt.data,
                description = "" if not form.description.data else form.description.data,
                time=datetime.datetime.now(datetime.UTC)
            )
            db.session.add(transfer)
            from_accnt.balance -= form.amt.data
            to_accnt.balance += form.amt.data
            db.session.commit()
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
    return redirect(url_for("get_home"))

@app.post("/deposit/")
def post_deposit():
    username = session.get("username")
    if not username:
        return redirect(url_for("get_login"))
    
    form = DepositForm()
    if form.validate():
        to_accnt = db.session.get(Account, form.to_accnt.data)
        valid = (
            (to_accnt is not None) and
            to_accnt.username == username
        )
        if not valid:
            flash("Error in depositing funds, double check the account number.")
        else:
            transfer = Transfer(
                from_account=-1, # to signify a deposity rather than a transfer
                to_account=to_accnt.account_number,
                amount=form.amt.data,
                description = "",
                time=datetime.datetime.now(datetime.UTC)
            )
            to_accnt.balance += form.amt.data
            db.session.add(transfer)
            db.session.commit()
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
    return redirect(url_for("get_home"))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
