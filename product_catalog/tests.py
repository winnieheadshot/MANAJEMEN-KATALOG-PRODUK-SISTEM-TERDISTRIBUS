import unittest
from app import app
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_products(self):
        response = self.app.get('/api/products')
        self.assertEqual(response.status_code, 200)
        
    def test_create_product(self):
        data = {
            "name": "Test Product",
            "category": "Electronics",
            "price": 99.99,
            "description": "Test"
        }
        response = self.app.post('/api/products',
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()