from flask import Flask
from model import User, Transaction, connect_to_db, db
from datetime import datetime
from functions import create_transfer, new_status


def send_payments():
    """Send todays payments that are due."""

    today = datetime.today()
    today = today.strftime("%Y-%m-%d")
    today = datetime.strptime(today, "%Y-%m-%d")

    due_list = Transaction.query.filter_by(date=today).all()

    for item in due_list:
        if item.status == 'payment to seller scheduled':
            account_id = item.seller.account_id
            amount = item.amount
            currency = item.currency
            create_transfer(amount, currency, account_id)

            Transaction.new_status(item.transaction_id, "completed")
            db.session.commit()

if __name__ == "__main__":

    from server import app
    # app = Flask(__name__)
    connect_to_db(app)
    print "Connected to DB."

    send_payments()
