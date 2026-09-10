import unittest
import os
from datetime import timedelta

# Set an environment variable for testing before importing the app
os.environ["SECRET_KEY"] = "testing_secret_key"

from app import app, db, User

class FlaskAuthAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a clean testing environment before each test."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF tokens to simplify
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory"  # Use in-memory DB for speed and isolation

        self.client = app.test_client()

        # Initialize database tables
        with app.app_context():
            db.create_all()

            # Create a default seed user
            user = User(username="testuser", password="scrypt:32768:8:1$mockedhash", role="user")
             # Create a default seed admin
            admin = User(username="adminuser", password="scrypt:32768:8:1$mockedhash", role="admin")

            db.session.add(user)
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # ==========================================
    # AUTHENTICATION & REGISTRATION TESTS
    # ==========================================

    def test_home_page_accessible(self):
        """Ensure the public home page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_registration_successful(self):
        """Verify new users can register and roles default safely to 'user'."""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'password': 'securepassword123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful!", response.data)

        # Verify role hardening works as expected
        with app.app_context():
            user = db.session.execute(db.select(User).filter_by(username='newuser')).scalar_one()
            self.assertEqual(user.role, 'user')

        def test_registration_duplicate_username_fails(self):
            """Ensure system rejects registrations with an existing username."""
            response = self.client.post('/register', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertIn(b"Username already exists!", response.data)

        def test_login_validation_and_session(self):
            """Test login works using a mocked password check validation."""
            # Include 'submit' field to satisfy Flask-WTF validation hooks
            response = self.client.post('/login', data={
                'username': 'testuser', 
                'password': 'wrongpassword',
                'submit': 'Sign In'
            }, follow_redirects=True)
            self.assertIn(b"Invalid username or password.", response.data)


    def test_login_validation_and_session(self):
        """Test login works using a mocked password check validation."""
        # Note: Because we used a dummy hash in setUp, we mock the verification or test the route handling
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b"Invalid username or password.", response.data)

    # ==========================================
    # AUTHORIZATION & ROLE PROTECTIONS
    # ==========================================

    def test_dashboard_requires_login(self):
        """Ensure unauthenticated users are redirected from the dashboard."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirects to login view

    def test_admin_panel_restricts_standard_users(self):
        """Verify standard users cannot access administrative endpoints (403 Forbidden)."""
        # Simulate logging in as standard user 'testuser'
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '1'  # ID of testuser
            sess['_fresh'] = True

        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 403)

    def test_admin_panel_allows_admin(self):
        """Verify admin accounts can access administrative endpoints."""
        # 1. Log in the admin user using the session transaction
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '2'  # ID of adminuser created in setUp()
            sess['_fresh'] = True

        # 2. Wrap the request inside an app context to guarantee 
        # Flask-Login maps the ID back to the active DB instance
        with app.app_context():
            response = self.client.get('/admin')
            self.assertEqual(response.status_code, 200)


    # ==========================================
    # PROFILE MANAGEMENT & LOGIC FLAWS
    # ==========================================

    def test_profile_update_username_conflict(self):
        """Ensure profile edit route handles a username change error securely."""
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '1'  # testuser
            sess['_fresh'] = True

        # Attempt to change testuser's name to 'adminuser' (which is already taken)
        response = self.client.post('/profile', data={
            'username': 'adminuser',
            'password': ''
        }, follow_redirects=True)
        
        self.assertIn(b"That username is already taken!", response.data)

    def test_profile_has_errors_variable_bug(self):
        """Verify profile handles dynamic field failures without throwing a 500 UnboundLocalError."""
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '1'
            sess['_fresh'] = True

        # This test ensures your code does not crash when `has_errors` is evaluated.
        # Note: Your current profile code refers to `has_errors` before declaring it 
        # when a conflict occurs. This test catches that crash.
        try:
            response = self.client.post('/profile', data={
                'username': 'adminuser',
                'password': 'newpassword123'
            })
            # If your code hits an UnboundLocalError, the response code will be 500
            self.assertNotEqual(response.status_code, 500)
        except UnboundLocalError:
            self.fail("profile() route raised UnboundLocalError due to undefined 'has_errors' variable!")

if __name__ == '__main__':
    unittest.main()