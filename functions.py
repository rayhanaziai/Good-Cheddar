from model import db, User, Transaction, connect_to_db
from flask_sqlalchemy import SQLAlchemy
import stripe
from flask import Flask
# from flask_bcrypt import Bcrypt
import bcrypt

# bcrypt_app = Flask(__name__)
# bcrypt = Bcrypt(bcrypt_app)


def password_hash(password):
    password = str.encode(password)
    hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
    # We return the unicode version of the hash so that it goes into th db okay. 
    return hashed_pw.decode("utf-8")


def check_password(hashed, password):
    password = str.encode(password)
    hashed = str.encode(hashed)
    return bcrypt.checkpw(password, hashed)


def create_charge(amount, token, description):

    return stripe.Charge.create(
        amount=amount,
        currency='usd',
        source=token,
        description=description
        )


def create_seller_account(currency, email):

    return stripe.Account.create(
        country='us',
        managed=True,
        email=email
        )


def create_seller_token(name, routing_number, account_number):

    response = stripe.Token.create(
        bank_account={
            "country": 'US',
            "currency": 'usd',
            "account_holder_name": name,
            "account_holder_type": 'individual',
            "routing_number": routing_number,
            "account_number": account_number
            },
        )
    return response


def create_customer(email, api_key):

    return stripe.Customer.create(email=email,
                                  api_key=api_key)


def create_transfer(amount, currency, destination):

    # source=account_token would be added at deployment
    # destination is always the account_id
    return stripe.Transfer.create(amount=amount,
                           currency=currency,
                           destination=destination)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app, "postgresql:///goodcheddar")
    print ("Connected to DB.")

