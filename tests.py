from server import app
from model import db, connect_to_db, example_data
import unittest

class LoggedOut_Page_Loads(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_landing_page_render(self):
        """Tests landing page loads."""
        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Sign Up', result.data)
        self.assertIn(b'Sign In', result.data)

    def test_signup_page_render(self):
        """Tests that signup page loads."""
        result = self.client.get("/signup")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Create your', result.data)

    def test_signin_page_render(self):
        """Tests that sign-in page loads."""
        result = self.client.get("/signin")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'to your account', result.data)


class Logged_In(unittest.TestCase):
    """Tests for pages requiring sign in."""

    @classmethod
    def setUpClass(cls):
        """Just once."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        connect_to_db(app, "postgresql:///test_database")

    def setUp(self):
        """Before each test."""
        self.client = app.test_client()
        # Store a value for user_id in the session to mimic signed-in user
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """After every test."""
        db.session.close()
        db.drop_all()

    def test_setup_page_renders(self):
        """Tests activity setup page loads."""
        result = self.client.get("/setup")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'usually ideal', result.data)

    def test_create_activity_types(self):
        """Tests user can specify an activity type for tracking using every
        available field on the setup page."""
        result = self.client.post("/setup",
                                  data={"activity_1": "coding",
                                        "activity_2": "sports",
                                        "activity_3": "shopping",
                                        "activity_4": "friends",
                                        "activity_5": "studying",
                                        "activity_6": "meditation",
                                        "activity_7": "family",
                                        "activity_8": "napping",
                                        "activity_9": "piano",
                                        "activity_10": "writing"},
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Plan an Activity', result.data)

    def test_main_page_render(self):
        """Tests that main page loads."""
        result = self.client.get("/main")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'activity to begin tracking', result.data)

    # def test_create_new_user(self):
    # """Tests database for existence of user"""

    # result = User.query.filter(User.email == 'hb-student@hackbright.com').one()
    # self.assertIn('with user_id', result.data)

    
if __name__ == '__main__':
    unittest.main()
