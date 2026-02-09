import unittest
import tempfile
import os
from datetime import datetime
from task_<Surname>_<Name>_graphite_cli import process_log_file, generate_graphite_commands

class GraphiteCliTestCase(unittest.TestCase):
    def setUp(self):
        # Создаем временный файл с примером логов
        self.temp_log = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        # Пример логов для одного запроса:
        # start processing query: python test
        # found 12345 articles for query: python test
        # finish processing query: python test
        self.sample_log_lines = [
            "20231003_154500.123 task_<Surname>_<Name>_web_service_log DEBUG start processing query: python test\n",
            "20231003_154501.456 task_<Surname>_<Name>_web_service_log INFO found 12345 articles for query: python test\n",
            "20231003_154502.789 task_<Surname>_<Name>_web_service_log DEBUG finish processing query: python test\n"
        ]
        self.temp_log.writelines(self.sample_log_lines)
        self.temp_log.close()
    
    def tearDown(self):
        os.unlink(self.temp_log.name)
    
    def test_process_log_file_and_generate_commands(self):
        records = process_log_file(self.temp_log.name)
        # Проверяем, что найден ровно один запрос
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record['query'], "python test")
        self.assertEqual(record['article_count'], 12345)
        self.assertIsNotNone(record['start_time'])
        self.assertIsNotNone(record['finish_time'])
        
        # Генерируем команды для Graphite
        commands = generate_graphite_commands(records, host="localhost", port=2003)
        # На каждый запрос должны генерироваться две команды
        self.assertEqual(len(commands), 2)
        self.assertIn("wiki_search.article_found 12345", commands[0])
        self.assertIn("wiki_search.complexity", commands[1])
        
        # Проверяем, что временная метка округлена вниз до целых секунд.
        # Для finish_time, заданного как "20231003_154502.789" дата-часть "20231003_154502" преобразуется в timestamp:
        dt = datetime.strptime("20231003_154502", "%Y%m%d_%H%M%S")
        expected_timestamp = int(dt.timestamp())
        self.assertIn(str(expected_timestamp), commands[0])
        self.assertIn(str(expected_timestamp), commands[1])

if __name__ == '__main__':
    unittest.main()

