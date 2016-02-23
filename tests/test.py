import unittest
import json
from recastrestapi.server import app
from recastrestapi.server import db
from recastdb.models import AccessToken, User
import random
import string

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.app_context().push()
        db.create_all()
        self.client = self.app.test_client()
        self.token = self.random_string()

    def tearDown(self):
        db.session.remove()
        #self.app.app_context().pop()

    def test_add_token(self):
        test_user = User(name="Rest API test user", email="testapi@email.com")
        db.session.add(test_user)
        db.session.commit()
        token = AccessToken(token=self.token, user_id=test_user.id)
        db.session.add(token)
        db.session.commit()

    def get_api_header(self, token="test_token"):
        return {
            'Authorization': 'Basic ' + token, 
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_header())
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEquals(json_response['_error']['code'],404)

    def test_token_auth(self):
        pass

    def test_GET(self):
        pass

    def test_POST(self):
        pass

    def random_string(self, size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
        
