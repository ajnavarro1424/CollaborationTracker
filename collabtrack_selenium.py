import os
import unittest
from collabtrack import app, Collaboration, Audit, Change, User
from field_pop import field_pop, import_data
from mongoengine import connect

from flask_testing import LiveServerTestCase
from selenium import webdriver


class TestCase(LiveServerTestCase):
    def create_app(self):

        return app

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120,550)
        self.driver.get(self.get_server_url())
        # conn = get_connection('test_db')
        # self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        # Init the test_db with values.
        field_pop()
        import_data()
    # Test visitation to the index page.
    def test_main_page(self):
        self.driver.get(self.get_server_url())
        assert 'NeuroPace Collaboration Tracker' in self.driver.page_source
    #Login
    def test_user_login(self):
        self.driver.get(self.get_server_url()+'/login/bauer123')
        assert 'Logged in successfully.' in self.driver.page_source

    def test_ajax_index(self):
        #Navigate to the index page and ensure collab table has rendered.
        self.driver.get(self.get_server_url())
        self.driver.get(self.get_server_url()+'/login/bauer123')
        assert 'Logged in successfully.' in self.driver.page_source

        #When Archive button is clicked, remove collaboration from list
        btn_archive_list = self.driver.find_elements_by_class_name('btn-archive')

        to_archive_id = btn_archive_list[0].get_attribute('id')
        self.assertIn(to_archive_id, self.driver.page_source,
                      "Can't find id %s" % to_archive_id)
        btn_archive_list[0].click()
        assert to_archive_id not in self.driver.page_source


    # def new_collab(self):
    #     response = self.app.get('http://localhost:5000')
    #     btn_start = driver.find_element_by_link_text("Start Collaboration")
    #     response = btn_start.click()
    #     assert b'Initiation' in response.data




    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
