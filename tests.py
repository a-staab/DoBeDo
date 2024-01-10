import unittest
from server import app
from model import db, connect_to_db, example_data


class Test(unittest.TestCase):
    """Tests for public pages."""

    def setUp(self):
        """Do this before each test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///test_database")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do this after every test."""

        # End session and delete tables
        db.session.close()
        db.drop_all()

    def test_signup_page_render(self):
        """Tests that signup page loads."""

        result = self.client.get("/signup")
        self.assertEqual(result.status_code, 200)
        self.assertIn("Create your", result.data)

    def test_signin_page_render(self):
        """Tests that sign-in page loads."""

        result = self.client.get("/signin")
        self.assertEqual(result.status_code, 200)
        self.assertIn("to your account", result.data)

    # def test_create_new_user(self):
    #     """Tests database for existence of user created using create_new_user
    #     helper function."""

    #     result = User.query.filter(User.email == 'hb-student@hackbright.com').one()
    #     self.assertIn('with user_id', result.data)


class Test_Signed_In(unittest.TestCase):
    """Tests for pages requiring sign in."""

    def setUp(self):
        """Do this before each test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'

        # Store a value for user_id in the session to mimic signed-in user
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

        # Connect to test database
        connect_to_db(app, "postgresql:///test_database")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do this after every test."""

        # End session and delete tables
        db.session.close()
        db.drop_all()

    def test_request_activity_types(self):
        """Tests activity setup page loads."""

        result = self.client.get("/setup")
        self.assertEqual(result.status_code, 200)
        self.assertIn('usually ideal', result.data)

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
        self.assertIn('Plan an Activity', result.data)

    def test_main_page_render(self):
        """Tests that main page loads."""

        result = self.client.get("/main")
        self.assertEqual(result.status_code, 200)
        self.assertIn("activity to begin tracking", result.data)

    def test_get_table_sizes(self):
        """Tests get_table_sizes function."""

        self.assertEqual(get_table_sizes((['name'] * 11), [(5, 1), (3, 2)])


if __name__ == '__main__':
    unittest.main()
