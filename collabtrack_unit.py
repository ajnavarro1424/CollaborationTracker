import os
import unittest
from collabtrack import app, Collaboration, Audit, Change, User, mdb
from field_pop import field_pop, import_data
from mongoengine import connect

class TestCase(unittest.TestCase):
    index = 'http://localhost:5000'
    # Initializes the DB. Called before each test is run.
    def setUp(self):
        # Use the existing dev DB for test environment
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        #DB collections are drop and re-initialized.
        field_pop()
        import_data()

    
    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
