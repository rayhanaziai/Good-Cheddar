from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#####################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    account_id = db.Column(db.String(300), nullable=True)
    secret_key = db.Column(db.String(300), nullable=True)
    payer_seller = db.Column(db.String(20), nullable=False)

    # transaction = db.relationship("Transaction",
    #                               backref=db.backref("users", order_by=user_id))
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id,
                                               self.email)

    @classmethod
    def fetch(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def add(cls, fullname, email, password, payer_seller):
        new_user = User(fullname=fullname,
                        email=email,
                        password=password,
                        payer_seller=payer_seller)

        db.session.add(new_user)
        db.session.commit()

        return new_user

    @classmethod
    def fetch_by_email(cls, email):

        return User.query.filter_by(email=email).first()


class Transaction(db.Model):
    """Movie on ratings website."""

    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer,
                               autoincrement=True,
                               primary_key=True)
    payer_id = db.Column(db.Integer,
                         db.ForeignKey('users.user_id'))
    seller_id = db.Column(db.Integer,
                          db.ForeignKey('users.user_id'))
    charge_id = db.Column(db.String(300), nullable=True)
    is_signed = db.Column(db.Boolean, nullable=False)
    payment_received = db.Column(db.Boolean, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    currency = db.Column(db.String(3), nullable=True)
    status = db.Column(db.String(50), nullable=False)

    payer = db.relationship("User", foreign_keys=[payer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Transaction transaction_id=%s is_signed=%s>" % (self.transaction_id,
                                                                 self.is_signed)
    @classmethod
    def fetch(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def add(cls, payer_id, seller_id, is_signed, payment_received, date, amount, currency, status):
        new_trans = Transaction(payer_id=payer_id,
                                seller_id=seller_id,
                                is_signed=is_signed,
                                payment_received=payment_received,
                                date=date,
                                amount=amount,
                                currency=currency,
                                status=status)
        db.session.add(new_trans)
        db.session.commit()
        return new_trans

    @classmethod
    def new_status(cls, transaction_id, new):

        Transaction.query.get(transaction_id).status = new
        db.session.commit()



#####################################################################
# Helper functions

def connect_to_db(app, database_uri):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app, "postgresql:///easypay")
    print "Connected to DB."

