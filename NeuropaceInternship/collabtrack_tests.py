import os
import unittest
from collabtrack import app, Collaboration, Audit, Change, User
from field_pop import field_pop, import_data
from mongoengine import connect

from selenium import webdriver

class TestCase(unittest.TestCase):
    index = 'http://localhost:5000'
    # Initializes the DB. Called before each test is run.
    def setUp(cls):
        cls.driver = webdriver.Chrome()
        # Creates a connection to a test db
        # Creates necessary db contents for testing
        connect('test_db', host='mongomock://localhost')
        # self.app = app.test_client()
        # conn = get_connection('test_db')
        # self.db_fd, .app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        with app.app_context():
            #Init the test_db with values.
            field_pop()
            import_data()
    # Test visitation to the index page.
    def test_main_page(self):
        response = self.app.get('http://localhost:5000')
        self.assertEqual(response.status_code, 200)
        assert b'NeuroPace Collaboration Tracker' in response.data
    #Login
    def test_user_login(self):
        response = self.app.get('http://localhost:5000/login/bauer123', follow_redirects=True)
        assert b'Logged in successfully.' in response.data

    def new_collab(self):
        response = self.app.get('http://localhost:5000')
        btn_start = driver.find_element_by_link_text("Start Collaboration")
        response = btn_start.click()
        assert b'Initiation' in response.data




    def tearDown(cls):
        cls.driver.quit()
        #Drop neccessary db contents before the next test
        Collaboration.drop_collection()
        Audit.drop_collection()
        User.drop_collection()
        # os.close(self.db_fd)
        # os.unlink(app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
