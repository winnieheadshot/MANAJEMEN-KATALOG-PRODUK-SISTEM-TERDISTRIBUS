# ecommerce_client.py
class ProductAPIClient:
    def __init__(self, base_url='http://localhost:5000', api_key=None):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }

    def get_products(self):
        response = requests.get(
            f'{self.base_url}/api/products',
            headers=self.headers
        )
        return response.json()

    def create_product(self, product_data):
        response = requests.post(
            f'{self.base_url}/api/products',
            data=json.dumps(product_data),
            headers=self.headers
        )
        return response.json()