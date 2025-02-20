"""Utility file to seed tracker database from data in seed_data/"""

from model import User, Activity, Occurrence, connect_to_db, db
from server import app
import bcrypt


def load_users():
    """Load users from u.user into database."""

    for i, row in enumerate(open("seed_data/u.user")):
        row = row.rstrip()
        email, password, user_handle, age = row.split("|")
        if age == '':
            age = None

        password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        user = User(email=email,
                    password=password,
                    user_handle=user_handle,
                    age=age)

        db.session.add(user)

    db.session.commit()


def load_activities():
    """Load activities from u.activity into database."""

    for i, row in enumerate(open("seed_data/u.activity")):
        row = row.rstrip()
        activity_type, user_id = row.split("|")

        activity = Activity(activity_type=activity_type, user_id=user_id)

        db.session.add(activity)

    db.session.commit()


def load_occurrences():
    """Load occurrences from u.occurrence into database."""

    for i, row in enumerate(open("seed_data/u.occurrence")):
        row = row.rstrip()
        print(row)
        (activity_id, start_time, end_time, before_rating, after_rating,
            notes) = row.split("|")
        if notes == '':
            notes = None

        occurrence = Occurrence(activity_id=activity_id,
                                start_time=start_time,
                                end_time=end_time,
                                before_rating=before_rating,
                                after_rating=after_rating,
                                notes=notes)

        db.session.add(occurrence)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.drop_all()
    db.create_all()

    load_users()
    load_activities()
    load_occurrences()
    # set_val_user_id()
