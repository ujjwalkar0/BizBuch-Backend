from rest_framework.test import APITestCase

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}