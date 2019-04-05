from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Transaction
from functions import password_hash, check_password, create_charge, create_seller_account, create_seller_token, create_customer
import json
import requests
import stripe
import datetime
import os

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "MYSECRETKEY"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

stripe.api_key = os.environ['STRIPE_KEY']
mailgun_key = os.environ['MAILGUN_KEY']

# Use this card number for test purposes 4000 0000 0000 0077
# Account number 000123456789
# Routing number 110000000


def login_required(handler):
    def fn(*a, **kw):
        user_id = session.get('user_id')
        if user_id:
            return handler(user_id, *a, **kw)
        else:
            return redirect('/')
    fn.__name__ = handler.__name__
    return fn


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""
    return render_template("register-form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    phone_number = request.form.get("phone_number")
    password = request.form.get("password")
    # payer_seller = request.form.get("payer_or_receiver")
    password = password_hash(password)
    # check to see if user already exists. If so, update their details.
    if User.fetch_by_email(email) is None:
        current_user = User.add(fullname, email, phone_number, password)

    else:
        current_user = User.fetch_by_email(email)
        current_user.fullname = fullname
        current_user.phone_number = phone_number
        current_user.password = password

    db.session.commit()

    flash("User %s added." % fullname)

    session["user_id"] = current_user.user_id
    # session["payer_seller"] = current_user.payer_seller
    return redirect("/dashboard")


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.fetch_by_email(email)

    if not user:
        flash("No such user")
        return redirect("/login")

    pw_hash = user.password

    if check_password(pw_hash, password) is False:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id
    # session["payer_seller"] = user.payer_seller

    flash("Logged in")
    return redirect("/dashboard")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route("/dashboard", methods=['GET'])
@login_required
def get_dashboard(user_id):
    """Show info about user."""

    if user_id == session["user_id"]:
        user = User.fetch(user_id)
        transaction_payer_filter = Transaction.payer_id == user_id
        transaction_seller_filter = Transaction.seller_id == user_id

        completed_payer_transactions = Transaction.query.filter(
            transaction_payer_filter,
            Transaction.is_completed == True
        ).all()
        completed_seller_transactions = Transaction.query.filter(
            transaction_seller_filter,
            Transaction.is_completed == True
        ).all()
        completed_transactions = completed_payer_transactions + completed_seller_transactions

        pending_payer_transactions = Transaction.query.filter(
            transaction_payer_filter,
            Transaction.is_completed == False,
        ).all()
        pending_seller_transactions = Transaction.query.filter(
            transaction_seller_filter,
            Transaction.is_completed == False,
        ).all()
        pending_transactions = pending_payer_transactions + pending_seller_transactions

        return render_template("dashboard.html",
                               user=user,
                               completed_transactions=completed_transactions,
                               pending_transactions=pending_transactions)
    else:
        flash("Sorry! That's not you!")
        return redirect("/")


@app.route("/dashboard", methods=['POST'])
@login_required
def process_acceptance(user_id):
    """Change status of transaction depending on seller acceptance"""

    acceptance = request.form.get("agree_or_disagree")

    transaction_id = session["transaction"]
    current_transaction = Transaction.fetch(transaction_id)
    seller_user = User.fetch(user_id)
    payer_user = User.fetch(current_transaction.payer_id)

    if acceptance == "agree":
        current_transaction.status = "awaiting payment from payer"
        html = "<html><h2>Good Cheddar</h2><br><p>Hi " + payer_user.fullname \
               + ",</p><br>" + seller_user.fullname + " has approved your contract." \
               + "Please<a href='http://localhost:8088/login'><span> log in </span>" \
               + "</a>to make your payment to Good Cheddar.<br><br> From the Good Cheddar team!</html>"

        # for test purposes, the same buyer email will be used. when live, use '"to": payer_user.email'

        requests.post(
            "https://api.mailgun.net/v3/sandbox9ba71cb39eb046f798ee4676ad972946.mailgun.org/messages",
            auth=('api', 'key-fcaee27772f7acfa5b4246ae675248a0'),
            data={"from": "rayhana.z@hotmail.com",
                  "to": 'rayhanaziai@gmail.com',
                  "subject": "Contract approved!",
                  "html": html})

    else:
        Transaction.new_status(transaction_id, "declined by seller")
    db.session.commit()

    # At this stage an email is sent to the buyer with prompt to pay.
    return redirect("/dashboard")


@app.route("/terms")
@login_required
def transaction_form(user_id):

    user = User.fetch(user_id)
    return render_template("transaction-form.html", user=user)


@app.route("/terms.json", methods=['POST'])
@login_required
def process_new_transaction(user_id):
    """Persist a new transaction into the DB"""

    # Get form variables
    seller_email = request.form.get("seller_email")
    seller_fullname = request.form.get("seller_fullname")
    payment_date = request.form.get("payment_date")
    payment_amount = request.form.get("payment_amount")
    product_details = request.form.get("product_details")
    date = datetime.datetime.strptime(payment_date, "%Y-%m-%d")

    # The recipient is added to the database
    # password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    original_password = '0000'
    password = password_hash(original_password)
    if User.fetch_by_email(seller_email) is None:
        User.add(
            fullname=seller_fullname,
            email=seller_email,
            phone_number='',
            password=password,
        )
    db.session.commit()

    seller = User.fetch_by_email(seller_email)
    seller_id = seller.user_id
    payer_id = session['user_id']
    payer = User.fetch(payer_id)
    payer_fullname = payer.fullname
    # An email is sent to the seller to log in and view the contract
    html = "<html><h2>Good Cheddar</h2><br><p>Hi " + seller_fullname \
        + ",</p><br>" + payer_fullname + " would like to send you money via Good Cheddar. \
        <br> Please<a href='http://localhost:8088/login'><span> log in </span></a>\
        to view and accept the contract:<br>Password: " + str(original_password) \
        + "<br><br> From the Good Cheddar team!</html>"

    requests.post(
        "https://api.mailgun.net/v3/sandbox9ba71cb39eb046f798ee4676ad972946.mailgun.org/messages",
        auth=('api', mailgun_key),
        data={"from": "goodcheddarinc@gmail.com",
              "to": seller_email,
              "subject": "You have a payment pending",
              "html": html})

    status_history = {
        "status":
            [
                "waiting from approval from seller"
            ]
        }
    # The new transaction is created in the database
    new_transaction = Transaction.add(
        payer_id=payer_id,
        seller_id=seller_id,
        payment_amount=float(payment_amount),
        payment_currency="USD",
        payment_date=date,
        payment_is_approved=False,
        product_images='',
        product_details=product_details,
        payment_is_made=False,
        is_disputed=False,
        dispute_images='',
        dispute_details='',
        status_history=json.dumps(status_history),
        status="pending approval from recipient",
        is_completed=False,
    )
    date = date.strftime('%Y-%m-%d')

    flash("Approval prompt sent to the recipient")
    # return redirect("/dashboard")

    return jsonify({'new_transaction_id': new_transaction.transaction_id,
                    'new_recipient': new_transaction.seller.fullname,
                    'new_date': date,
                    'new_amount': payment_amount,
                    'new_status': "pending approval from recipient",
                    'new_action': 'No action'})


@app.route("/approved-form/<int:transaction_id>")
def show_approved_form(transaction_id):

    transaction = Transaction.fetch(transaction_id)
    user_id = session["user_id"]
    payer_seller = session["payer_seller"]
    session["transaction"] = transaction_id
    return render_template('approved-contract.html',
                           transaction=transaction,
                           user_id=user_id,
                           payer_seller=payer_seller)


@app.route('/payment/<int:transaction_id>')
def payment_form(transaction_id):

    return render_template('payment-form.html',
                           transaction_id=transaction_id)


@app.route('/payment/<int:transaction_id>', methods=['POST'])
def payment_process(transaction_id):

    token = request.form.get("stripeToken")

    transfer = Transaction.fetch(transaction_id)
    payer_id = transfer.payer_id
    seller_id = transfer.seller_id
    seller_email = transfer.seller.email
    amount = transfer.amount*100
    currency = transfer.currency
    date = transfer.date
    description = "payment from %d to %d" % (payer_id, seller_id)

    # Any way to check if this payment causes error?
    charge = create_charge(amount, token, description)

    if charge.to_dict()['paid'] is not True:
        flash("Your payment has not gone through. Please try again.")
    else:
        Transaction.new_status(transaction_id, "payment from payer received")

        # As soon as payment is successfull, stripe account set up for seller.
        try:
            new_account = create_seller_account(currency, seller_email)

            account_id = new_account.to_dict()['id']
            s_key = new_account.to_dict()['keys']['secret']

            # Add account_id and s_key to database
            User.fetch(seller_id).account_id = account_id
            User.fetch(seller_id).secret_key = s_key
            db.session.commit()

            #Send prompt email to seller for him to put in account details.
            html = "<html><h2>Good Cheddar</h2><br><p>Hi " + transfer.seller.fullname \
                + ",</p><br>" + transfer.payer.fullname + " has transfered the \
                agreed amount of funds to Good Cheddar. \
                <br> To get paid on the scheduled date, please log in to your \
                Good Cheddar account and enter your account details.\
                <br><br> From the Good Cheddar team!</html>"

            # for test purposes, the same seller email will be used. when live, use '"to": seller_email'
            requests.post(
                "https://api.mailgun.net/v3/sandbox9ba71cb39eb046f798ee4676ad972946.mailgun.org/messages",
                auth=('api', mailgun_key),
                data={"from": "rayhana.z@hotmail.com",
                      "to": seller_email,
                      "subject": "Log in to Good Cheddar",
                      "html": html})

        except stripe.InvalidRequestError as e:
            flash(e.message)
            # send email to seller telling them to put their details in stripe

    print ("***the token is", token)
    return redirect("/dashboard")


@app.route('/accounts/<int:transaction_id>', methods=['GET'])
def account_form(transaction_id):

    return render_template('account-details-form.html', transaction_id=transaction_id)


@app.route('/accounts/<int:transaction_id>', methods=['POST'])
def account_process(transaction_id):

    name = request.form.get("name")
    routing_number = request.form.get("routing-number")
    account_number = request.form.get("account-number")

    response = create_seller_token(name, routing_number, account_number)

    user_id = session['user_id']
    user = User.fetch(user_id)

    seller_email = user.email
    s_key = user.secret_key
    account_token = response.to_dict()['id']
    amount = Transaction.fetch(transaction_id).amount
    currency = Transaction.fetch(transaction_id).currency
    account_id = user.account_id
    create_customer(seller_email, s_key)

    Transaction.new_status(transaction_id, "payment to seller scheduled")

    return redirect("/dashboard")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    connect_to_db(app, "postgresql:///goodcheddar")

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
