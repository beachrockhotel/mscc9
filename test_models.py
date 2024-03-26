import unittest
from app import app, db
from models import MenuItem

class ModelsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dmitriy:321123@localhost/club_test'

    def setUp(self):
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_menu_item_model(self):
        with app.app_context():
            db.session.query(MenuItem).delete()
            db.session.commit()

            item = MenuItem(name="Test Pizza", price=100.0)
            db.session.add(item)
            db.session.commit()

            self.assertEqual(MenuItem.query.count(), 1)