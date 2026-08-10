DoBeDo
===========

DoBeDo applies the notion of quantified self to the question of how to spend our
time if optimizing for happiness. Users track how they feel before and after
regular activities to better recognize which ones have the most positive impact 
on their mood. 

At signup, they select up to ten activities to track. Going forward, they record 
when they plan to do an activity and how they're feeling about doing it. Afterward,
once they've done it, they then also log what time they finished and 
how actually felt doing it. The app then provides a visualization of their 
expected and actual sentiment toward all recorded occurrences of each activity 
over time. Also, if the user provides their phone number when signing up for an 
account, they receive an automated text message reminder if 24 hours have passed
since the stated starting time for a planned activity and they haven't yet 
recorded how they felt about it afterward.

#### Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- JavaScript
- Bootstrap
- jQuery
- Jinja
- Chart.js
- SignalWire API

#### Screenshots and Features

![Screenshot of landing page](./screencaps/1_Landing_page.png)

A user can create an account. Their password is hashed in the database, and
providing a phone number indicates they've opted in for text message reminders
about outstanding planned activities.

![Screenshot of account creation page](./screencaps/2_Account_creation.png)

![Screenshot of sign-in page](./screencaps/3_Sign_in.png)

A user can indicate up to 10 activities to track.

![Screenshot of activity setup page](./screencaps/4_Activity_setup.png)

A user can record what time they plan to start doing one of their activities and
how they're feeling about it at that time. They can also record, afterward, how
they actually felt when doing it and what time they finished.

![Screenshot of Before_activity page](./screencaps/5_Before_activity.png)

![Screenshot of After_activity page](./screencaps/6_After_activity.png)

A user can view charts showing expected and actual sentiments toward all 
occurrences of each activity they're tracking over time from the main page's
dashboard.

![Screenshot of Dashboard page](./screencaps/7_Dashboard.png)