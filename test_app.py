from flask_testing import TestCase
from app import app, db
from models import MenuItem

class AppTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dmitriy:321123@localhost/club_test'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        response = self.client.get('/')
        self.assert200(response)

    def test_add_menu_item(self):
        response = self.client.post('/menu', json={'name': 'Test Pizza', 'price': 100.0})
        self.assertStatus(response, 201)