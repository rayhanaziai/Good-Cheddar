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
    phone_number = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    account_id = db.Column(db.String(300), nullable=True)
    secret_key = db.Column(db.String(300), nullable=True)
    # payer_seller = db.Column(db.String(20), nullable=False)

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
    def add(cls, fullname, email, phone_number, password):
        new_user = User(fullname=fullname,
                        email=email,
                        phone_number=phone_number,
                        password=password)

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
    payment_amount = db.Column(db.Float, nullable=False)
    payment_currency = db.Column(db.String(3), nullable=True, default='USD')
    payment_date = db.Column(db.DateTime, nullable=False)
    payment_is_approved = db.Column(db.Boolean, nullable=False)
    product_images = db.Column(db.String(500), nullable=True)
    product_details = db.Column(db.String(300), nullable=False)
    payment_is_made = db.Column(db.Boolean, nullable=False)
    is_disputed = db.Column(db.Boolean, nullable=False)
    dispute_images = db.Column(db.String(500), nullable=True)
    dispute_details = db.Column(db.String(300), nullable=True)
    status_history = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(300), nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False)

    payer = db.relationship("User", foreign_keys=[payer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Transaction transaction_id=%s payment_appoved=%s>" % (self.transaction_id,
                                                                 self.payment_is_approved)
    @classmethod
    def fetch(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def add(cls, payer_id, seller_id, payment_amount, payment_currency, payment_date,
        payment_is_approved, product_images, product_details, payment_is_made, is_disputed,
        dispute_images, dispute_details, status_history, status, is_completed):
        new_transaction = Transaction(
            payer_id=payer_id,
            seller_id=seller_id,
            payment_amount=payment_amount,
            payment_currency=payment_currency,
            payment_date=payment_date,
            payment_is_approved=payment_is_approved,
            product_images=product_images,
            product_details=product_details,
            payment_is_made=payment_is_made,
            is_disputed=is_disputed,
            dispute_images=dispute_images,
            dispute_details=dispute_details,
            status_history=status_history,
            status=status,
            is_completed=is_completed,
        )
        db.session.add(new_transaction)
        db.session.commit()
        return new_transaction

    @classmethod
    def new_status(cls, transaction_id, new_status):

        Transaction.query.get(transaction_id).status = new_status
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
    connect_to_db(app, "postgresql:///goodcheddar")
    print ("Connected to DB.")

