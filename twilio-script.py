from model import Occurrence
from twilio.rest import Client
from datetime import datetime, timedelta
from server import app
import os
import pytz


# Query for phone numbers of people with incompleted occurrences
numbers_to_dial = set()
pacific = pytz.timezone('US/Pacific')
with app.app_context():
    incomplete_occurrences = Occurrence.query.filter((Occurrence.end_time.is_(None) | Occurrence.after_rating.is_(None))).all()

    # Create a list with the phone number for each user who has an incomplete
    # occurrence scheduled to have started over 24 hours ago. This is for an SMS
    # reminder to open the app and complete their entry, given that they should have
    # completed the activity and have had enough time to remember to document it at
    # this point (while not having, yet, forgotten how they felt about it).
    for occurrence in incomplete_occurrences:
        if occurrence.activity.user.phone_number and occurrence.start_time.replace(tzinfo=pacific) < (datetime.now(tz=pacific) - timedelta(hours=24)):
            numbers_to_dial.add((occurrence.activity.user.phone_number, occurrence.activity.user.user_id))

    account_sid = os.environ["ACCOUNT_SID"]
    auth_token = os.environ["AUTH_TOKEN"]
    sw_phone_number = os.environ["SIGNALWIRE_PHONE_NUMBER"]

    client = Client(account_sid, auth_token)

    app.logger.debug(f'{len(numbers_to_dial)} numbers to dial')
    for number_user in numbers_to_dial: 
        try:
            message = client.messages.create(
                to=number_user[0],
                from_=sw_phone_number,
                body="""Hey friend! Looks like you've got one or more planned activities you might have finished. Let's hear how you felt, while it's still fresh in your mind!""")
            print(message.sid)
        except Exception as e:
            app.logger.error(f'Error texting reminder to user {number_user[1]}: {e.message}')
            
