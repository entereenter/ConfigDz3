import unittest
from main import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        #Создаем экземпляр парсера для использования в тестах.
        self.parser = ConfigParser()

    def test_parse_constants(self):
        #Тестируем парсинг констант.
        text = """
        let host = @"localhost";
        let port = 1111;
        let user = @"admin";
        """
        expected_constants = {
            "host": "localhost",
            "port": 1111,
            "user": "admin"
        }

        # Убираем константы из текста
        cleaned_text = self.parser.parse_constants(text)
        self.assertEqual(self.parser.constants, expected_constants)
        self.assertEqual(cleaned_text.strip(), "")  # Все константы должны быть удалены

    def test_evaluate(self):
        #Тестируем вычисление выражений.
        self.parser.constants = {
            "host": "localhost",
            "port": 1111
        }

        # Проверка ссылок на константы
        self.assertEqual(self.parser.evaluate("!{host}"), "localhost")
        self.assertEqual(self.parser.evaluate("!{port}"), 1111)

        # Проверка чисел
        self.assertEqual(self.parser.evaluate("123"), 123)

        # Проверка строк
        self.assertEqual(self.parser.evaluate('@"test_string"'), "test_string")

        # Проверка ошибки для неизвестной константы
        with self.assertRaises(ValueError):
            self.parser.evaluate("!{unknown_constant}")

    def test_parse_blocks(self):
        #Тестируем парсинг блоков словарей.
        text = """
        ([
            key1: 123,
            key2: @"value",
            nested: ([
                inner_key: @"inner_value",
                inner_number: 456
            ])
        ])
        """
        expected_output = {
            "key1": 123,
            "key2": "value",
            "nested": {
                "inner_key": "inner_value",
                "inner_number": 456
            }
        }
        result = self.parser.parse_blocks(text.strip())
        self.assertEqual(result, expected_output)

    def test_full_parse(self):
        #Тестируем полный процесс парсинга с использованием примера.
        text = """
        # Константы
        let host = @"localhost";
        let port = 1111;
        let user = @"admin";

        # Основной словарь
        ([
            database: ([
                name: @"example_db",
                user: !{user},
                password: @"secret",
                settings: ([
                    max_connections: 100,
                    timeout: 30
                ])
            ]),
            server: ([
                host: !{host},
                port: !{port}
            ])
        ])
        """
        expected_output = {
            "database": {
                "name": "example_db",
                "user": "admin",
                "password": "secret",
                "settings": {
                    "max_connections": 100,
                    "timeout": 30
                }
            },
            "server": {
                "host": "localhost",
                "port": 1111
            }
        }
        result = self.parser.parse(text.strip())
        self.assertEqual(result, expected_output)

    def test_split_entries(self):
        #Тестируем разделение записей в словаре.
        text = """
        key1: value1,
        key2: value2,
        nested: ([
            inner_key1: inner_value1,
            inner_key2: inner_value2
        ])
        """
        entries = self.parser.split_entries(text.strip())
        expected_entries = [
            "key1: value1",
            "key2: value2",
            "nested: ([\n            inner_key1: inner_value1,\n            inner_key2: inner_value2\n        ])"
        ]
        self.assertEqual(entries, expected_entries)

    def test_parse_value(self):
        # Тестируем парсинг отдельных значений.
        self.parser.constants = {
            "const1": "value1",
            "const2": 123
        }

        # Проверка типов значений
        self.assertEqual(self.parser.parse_value("123"), 123)
        self.assertEqual(self.parser.parse_value('@"string_value"'), "string_value")
        self.assertEqual(self.parser.parse_value("!{const1}"), "value1")
        self.assertEqual(self.parser.parse_value("!{const2}"), 123)

        # Вложенный словарь
        nested_dict = self.parser.parse_value("""([ key: @"value" ])""")
        self.assertEqual(nested_dict, {"key": "value"})

        # Проверка ошибки для некорректного значения
        with self.assertRaises(ValueError):
            self.parser.parse_value("invalid_value")


if __name__ == "__main__":
    unittest.main()