import unittest
from unittest.mock import patch
import requests
from task_<Surname>_<Name>_web_service_log import app

class WebServiceTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_valid_query(self):
        # Симулируем ответ Википедии с числом найденных статей (например, "of 12,345 results")
        sample_html = '<html><body>... of 12,345 results ...</body></html>'
        with patch('task_<Surname>_<Name>_web_service_log.requests.get') as mock_get:
            mock_response = unittest.mock.Mock()
            mock_response.text = sample_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            response = self.client.get('/api/search?query=python test')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['version'], 1.0)
            self.assertEqual(data['article_count'], 12345)
    
    def test_no_query_parameter(self):
        # Если параметр query отсутствует, должно вернуться 0 найденных статей
        response = self.client.get('/api/search')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['article_count'], 0)
    
    def test_nonexistent_route(self):
        # Обращение к несуществующему route должно вернуть 404 с нужным сообщением
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode('utf-8'), "This route is not found")
    
    def test_wikipedia_connection_error(self):
        # При симуляции ошибки соединения (requests.exceptions.ConnectionError)
        # должно возвращаться сообщение с кодом 503
        with patch('task_<Surname>_<Name>_web_service_log.requests.get', side_effect=requests.exceptions.ConnectionError):
            response = self.client.get('/api/search?query=python test')
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.data.decode('utf-8'), "Wikipedia Search Engine is unavailable")

if __name__ == '__main__':
    unittest.main()

