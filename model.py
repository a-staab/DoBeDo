from flask_sqlalchemy import SQLAlchemy
from flask import session

db = SQLAlchemy()


class User(db.Model):
    """User. A user has many activities."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(50), nullable=False, unique=True)
    password = db.Column(db.LargeBinary, nullable=False)
    user_handle = db.Column(db.Unicode(50), nullable=False)
    phone_number = db.Column(db.Unicode(20), nullable=True, unique=True)
    age = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<User with user_id %s and email %s>" % (self.user_id,
                                                        self.email)

    # Note to self: as a method, is called in form instance.method()
    def get_planned_occurrences(self):
        """Get all the incomplete occurrences for user."""

        return (db.session.query(Occurrence).join(Activity)
                          .filter(Activity.user_id == self.user_id,
                                  (Occurrence.end_time.is_(None) |
                                   Occurrence.after_rating.is_(None)))
                          .order_by(Occurrence.start_time)
                          .all())

    def get_completed_occurrences(self):
        """Get all the complete occurrences for user."""

        return (db.session.query(Occurrence).join(Activity)
                          .filter(Activity.user_id == self.user_id,
                                  Occurrence.end_time.isnot(None),
                                  Occurrence.after_rating.isnot(None),
                                  Occurrence.start_time.isnot(None),
                                  Occurrence.before_rating.isnot(None))
                          .order_by(Occurrence.start_time)
                          .all())


class Activity(db.Model):
    """Activity. An activity has many occurrences."""

    __tablename__ = "activities"

    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_type = db.Column(db.Unicode(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", backref="activities")

    def __repr__(self):
        return "<Activity with activity_id %s by user_id %s>" % (
            self.activity_id, self.user_id)


class Occurrence(db.Model):
    """Occurrence. An occurrence has one activity. An occurrence has one user."""

    __tablename__ = "occurrences"

    occurrence_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    before_rating = db.Column(db.Integer, nullable=False)
    after_rating = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Unicode(350), nullable=True)

    activity = db.relationship("Activity", backref="occurrences")

    def __repr__(self):
        return "<Occurrence with occurrence_id %s and activity_id %s>" % (
            self.occurrence_id, self.activity_id)


def connect_to_db(app, db_uri='postgresql:///tracker'):
    """Connect to the database."""

    # Making the database a default value for the db_uri parameter allows us to
    # pass in a different database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


# Helper functions
def create_new_user(email, password, user_handle, age=None):
    """Create a new user."""

    return User(email=email,
                password=password,
                user_handle=user_handle,
                age=age)


def sign_in_user(email):
    """Sign in user."""

    user_id = User.query.filter(User.email == email).one().user_id
    session["user_id"] = user_id
    user_handle = User.query.filter(User.email == email).one().user_handle
    session['user_handle'] = user_handle


def example_data():
    """Sample data for testing."""

    # Test creation of new users

    # Test using instantiation
    ashley = User(email='hb-student@hackbright.com', password='python',
                  user_handle='artist')

    # Tests using create_new_user helper function
    soo = create_new_user('coding-student@hackbright.com', 'python', 'boss')
    hannah = create_new_user('hacks@hackbright.com', 'python', 'linguist')
    katrina = create_new_user('testing_rocks@hackbright.com', 'python', 'friend')

    # Test supplying an age, which is optional
    mel = User(email='mel@ubermelon.com',
               password='python',
               user_handle='melons_honcho',
               age=42)

    # Test that an occurrence can be created without end_time, after_rating, and
    # notes
    # t_occurrence_1 = Occurrence(activity_id=1, start_time=, before_rating=,

    # Test that an occurrence can be created with values for all attributes

    # t_occurence_2 = Occurrence(activity_id=2, start_time=, end_time=,
    # before_rating=, after_rating=, notes=)

    # Test than an occurrence can be updated

    # t_occurence_1 = (set values for end_time, after_rating, and notes)

    # ^--Once complete, add test occurrences to list--v
    db.session.add_all([ashley, soo, hannah, katrina, mel])
    db.session.commit()

if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    print("Connected to DB! Woo!")
