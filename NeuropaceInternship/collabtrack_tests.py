import os
import unittest
from collabtrack import app
from field_pop import field_pop, import_data
from mongoengine import connect

class TestCase(unittest.TestCase):
    # Initializes the DB. Called before each test is run.
    def setUp(self):

        # Creates a connection to a test db
        # Creates necessary db contents for testing
        connect('test_db', host='mongomock://localhost')
        # conn = get_connection('test_db')
        # self.db_fd, .app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        # app = app.test_client()
        # with app.app_context():
        #     app.init_db()

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        #Drop neccessary db contents before the next test
        pass
        # os.close(self.db_fd)
        # os.unlink(app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
