from flask import Flask, request, render_template, redirect, flash, session, jsonify
from model import db, User, Activity, Occurrence, connect_to_db, sign_in_user
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
import os
import pytz
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]


@app.before_request
def check_signed_in():
    """Check that user is logged in before loading pages which should only be
    accessible when logged in. If not, redirect to sign-in page."""

    public_routes = { "/", "/signup", "/signin", "/static/style.css", "/static/landing.css", "/static/heart.jpg" }

    if request.path not in public_routes and not session.get("user_id"):
        flash("You need to be logged in to view this page. Please log in.")
        return redirect("/signin")


@app.route("/")
def show_landing_page():
    """Return landing page."""

    return render_template("landing.html")


@app.route("/signup", methods=["GET"])
def display_signup_form():
    """Return form for signing up for an account."""

    return render_template("signup.html", hide=True)


@app.route("/signup", methods=["POST"])
def signup_user():
    """Process signup form, adding user to database."""

    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    phone_number = request.form.get("phone-number")
    age = request.form.get("age")

    # Check database for pre-existing account by checking for a user with the
    # provided email address
    if User.query.filter(User.email == email).all():
        flash("Looks like you've already registered. If you mistyped, please try again.")

        return redirect("/signup")

    else:

        # Generate salt and hash password to store hashed password in database
        password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Age and phone number are optional
        if age and phone_number:
            new_user = User(user_handle=username,
                            password=password,
                            email=email,
                            phone_number=phone_number,
                            age=age)
        elif age:
            new_user = User(user_handle=username,
                            password=password,
                            email=email,
                            age=age)
        elif phone_number:
            new_user = User(user_handle=username,
                            password=password,
                            email=email,
                            phone_number=phone_number)
        else:
            new_user = User(user_handle=username,
                            password=password,
                            email=email)

        db.session.add(new_user)
        db.session.commit()

        # Immediately sign in new user; otherwise, redirecting to /setup would
        # fail the @app.before_request sign-in check, and user would be
        # redirected to /signin instead
        sign_in_user(email)

    return redirect("/setup")


@app.route("/setup", methods=["GET"])
def request_activity_types():
    """Display form for user to choose the activities they want to track."""

    return render_template("setup.html")


@app.route("/setup", methods=["POST"])
def create_activity_types():
    """Process setup form, adding user-defined activity types to database."""

    activity_1 = request.form.get("activity_1")
    activity_2 = request.form.get("activity_2")
    activity_3 = request.form.get("activity_3")
    activity_4 = request.form.get("activity_4")
    activity_5 = request.form.get("activity_5")
    activity_6 = request.form.get("activity_6")
    activity_7 = request.form.get("activity_7")
    activity_8 = request.form.get("activity_8")
    activity_9 = request.form.get("activity_9")
    activity_10 = request.form.get("activity_10")

    activities = [activity_1, activity_2, activity_3, activity_4, activity_5,
                  activity_6, activity_7, activity_8, activity_9, activity_10]

    new_activities = []

    for activity in activities:
        # User can enter as few as one; if None, it will not be added to the
        # database
        if activity:
            new_activities.append(activity)

    # Handle submission of form with no values
    if new_activities == []:

        flash("""You need to enter at least one activity to continue.
              Please make a selection and try again.""")
        return redirect("/setup")

    # For every activity user provides, add activity to the database
    else:

        for activity in new_activities:
            new_activity = Activity(activity_type=activity,
                                    user_id=session["user_id"])

            db.session.add(new_activity)
        db.session.commit()

        flash("Great! Looks like you're ready to start tracking!")
        return redirect("/main")


@app.route("/signin", methods=["GET"])
def display_signin_form():
    """Display form for logging into existing account."""

    return render_template("signin.html", hide=True)


@app.route("/signin", methods=["POST"])
def signin_user():
    """Handle sign-in."""

    provided_password = request.form.get("provided-password")
    email = request.form.get("email")

    # Check that a user with the provided email address is already in database
    if User.query.filter(User.email == email).all():
        # If so, check that the provided password produces the same hash as
        # what's stored in the database for the user with the provided email
        # address when the salt (stored in the hash) is applied to it
        password = User.query.filter(User.email == email).one().password
        provided_password = provided_password.encode('utf8')
        provided_after_salt = bcrypt.hashpw(provided_password, str(password))
        if password == provided_after_salt:
            # If so, get the user's user_id and user_handle and store them on
            # the session
            sign_in_user(email)

            flash("Thanks for logging in!")
            return redirect("/main")

        else:
            flash("Sorry, we didn't find an account with the email and password\
            you provided. Please try again.")

            return render_template("signin.html")

    else:
        flash("Sorry, we didn't find an account with the email and password you\
               provided. Please try again.")
        return render_template("signin.html")


@app.route("/main", methods=["GET"])
def show_main_page():
    """Load main page."""

    # Get activities for dropdown menu for choosing one to plan
    activities = Activity.query.filter(Activity.user_id == session['user_id']
                                       ).all()

    # Get user's occurrences without end times & before ratings to display as
    # links so user can click to complete them
    user = User.query.filter(User.user_id == session['user_id']).one()
    planned_occurrences = user.get_planned_occurrences()

    # Get list of user's completed occurrences for rendering charts
    completed_occurrences = user.get_completed_occurrences()

    # Charts should only be rendered for activities with at least one completed
    # occurrence
    used_activities = set([])
    for occurrences in completed_occurrences:
        used_activities.add(occurrences.activity)

    used_activities = list(used_activities)

    # Charts should be displayed in a consistent order; this alphabetizes them
    used_activities.sort(key=lambda x: x.activity_type)

    return render_template("/main.html",
                           activities=activities,
                           planned_occurrences=planned_occurrences,
                           completed_occurrences=completed_occurrences,
                           used_activities=used_activities)


@app.route("/plan_activity", methods=["POST"])
def handle_activity_choice():
    """Handle form for planning an activity."""

    activity_id = request.form.get("activity-choice")

    return redirect("/record_before/" + activity_id)


@app.route("/record_before/<activity_id>", methods=["GET"])
def display_before_form(activity_id):
    """Display form for creating a new occurrence."""

    # Get activity_type to display as a heading
    activity = Activity.query.filter(Activity.activity_id == activity_id).one()
    activity_type = activity.activity_type

    # Get current date and time so that user can quickly select these using now
    # button if desired
    pacific = pytz.timezone('US/Pacific')
    now = datetime.now(tz=pacific)
    now_date = datetime.strftime(now, "%Y-%m-%d")
    now_time = datetime.strftime(now, "%I:%M %p")

    return render_template("/record_before.html",
                           activity_id=activity_id,
                           now_date=now_date,
                           now_time=now_time,
                           activity_type=activity_type)


@app.route("/record_before/<activity_id>", methods=["POST"])
def get_before_values(activity_id):
    """Process form, creating a new occurrence and saving it to the database."""

    before_rating = request.form.get("before-rating")
    start_hour = request.form.get("planned-time")
    start_date = request.form.get("planned-date")

    unformatted_time = start_date + " " + start_hour
    start_time = datetime.strptime(unformatted_time, "%Y-%m-%d %I:%M %p")

    new_occurrence = Occurrence(activity_id=activity_id,
                                start_time=start_time,
                                before_rating=before_rating)

    db.session.add(new_occurrence)
    db.session.commit()

    flash("Entries successfully saved.")
    return redirect("/main")


@app.route("/record_after/<occurrence_id>", methods=["GET"])
def display_after_form(occurrence_id):
    """Display form for completing record of a previously created occurrence."""

    # Get activity_type to display as a heading
    occurrence = Occurrence.query.filter(
        Occurrence.occurrence_id == occurrence_id
        ).one()
    activity_name = occurrence.activity.activity_type

    # Get current date and time so that user can quickly select these using now
    # button if desired
    pacific = pytz.timezone('US/Pacific')
    now = datetime.now(tz=pacific)
    now_date = datetime.strftime(now, "%Y-%m-%d")
    now_time = datetime.strftime(now, "%I:%M %p")

    return render_template("/record_after.html",
                           occurrence_id=occurrence_id,
                           now_date=now_date,
                           now_time=now_time,
                           activity_name=activity_name)


@app.route("/record_after/<occurrence_id>", methods=["POST"])
def get_after_values(occurrence_id):
    """Process form for completing record of a previously created occurrence."""

    after_rating = request.form.get("after-rating")
    end_hour = request.form.get("end-time")
    end_date = request.form.get("end-date")

    unformatted_time = end_date + " " + end_hour
    end_time = datetime.strptime(unformatted_time, "%Y-%m-%d %I:%M %p")

    completed_occurrence = Occurrence.query.filter(
        Occurrence.occurrence_id == occurrence_id
        ).one()

    completed_occurrence.end_time = end_time
    completed_occurrence.after_rating = after_rating

    db.session.commit()

    flash("Changes saved.")
    return redirect("/main")


@app.route("/chart/<activity_id>.json")
def make_lines_chart_json(activity_id):
    """Return json with the data needed to render charts for all activities with
    completed occurrences."""

    completed_occurrences = db.session.query(Occurrence).join(Activity).filter(
        Activity.user_id == session['user_id'],
        Occurrence.end_time.isnot(None),
        Occurrence.after_rating.isnot(None),
        Occurrence.start_time.isnot(None),
        Occurrence.before_rating.isnot(None),
        Activity.activity_id == activity_id).order_by(
        Occurrence.start_time).all()

    before_ratings = [occurrence.before_rating
                      for occurrence in completed_occurrences]
    after_ratings = [occurrence.after_rating
                     for occurrence in completed_occurrences]
    unformatted_start_times = [occurrence.start_time
                               for occurrence in completed_occurrences]
    start_times = [datetime.strftime(unformatted, "%a, %b %d")
                   for unformatted in unformatted_start_times]
    return jsonify({"before": before_ratings,
                    "after": after_ratings,
                    "starts": start_times,
                    "activityId": activity_id})


@app.route("/profile", methods=["GET"])
def display_update_page():
    """Display page where user can update registration data."""

    return render_template("profile.html")


@app.route("/json/user", methods=["GET"])
def get_profile_data():
    """Return json for updating user profile information."""

    user = User.query.get(session['user_id'])
    results = {}
    results['email'] = user.email
    results['username'] = user.user_handle
    results['phoneNumber'] = user.phone_number
    results['age'] = user.age

    return jsonify(results)


@app.route("/profile", methods=["POST"])
def process_profile_update():
    """Process form for changing user data."""

    username = request.form.get("username")
    email = request.form.get("email")
    phone_number = request.form.get("phoneNumber")
    age = request.form.get("age")

    user = User.query.get(session['user_id'])
    user.user_handle = username
    user.email = email
    user.phone_number = phone_number
    user.age = age

    db.session.commit()

    # Update relevant session data immediately
    session['user_handle'] = user.user_handle

    flash("Changes saved.")
    return redirect("/main")


@app.route("/signout", methods=["GET"])
def signout_user():
    """Sign user out and redirect to landing page."""

    del session['user_id']
    del session['user_handle']
    return redirect("/")

# connect_to_db(app)

if __name__ == "__main__":
    app.debug = False
    app.jinja_env.auto_reload = app.debug
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")
