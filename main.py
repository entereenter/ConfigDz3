import re
import sys
import toml

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):

        # Удаление комментариев
        text = re.sub(r'#.*', '', text)

        # Обработка констант
        text = self.parse_constants(text)

        # Парсинг основного контента
        data = self.parse_blocks(text.strip())
        return data

    def parse_constants(self, text):
        #Парсинг и вычисление констант let и !{}
        const_pattern = r'let\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+?);'
        for match in re.findall(const_pattern, text):
            name, value = match
            value = self.evaluate(value.strip())
            self.constants[name] = value
        return re.sub(const_pattern, '', text)

    def evaluate(self, expression):
        #Вычисление выражений: числа, строки и ссылки на константы
        const_pattern = r'!{([a-zA-Z][_a-zA-Z0-9]*)}'
        if match := re.match(const_pattern, expression):
            const_name = match.group(1)
            if const_name not in self.constants:
                raise ValueError(f"Неизвестная константа: {const_name}")
            return self.constants[const_name]
        elif re.match(r'^\d+$', expression):  # Числа
            return int(expression)
        elif re.match(r'^@"(.*)"$', expression):  # Строки
            return re.match(r'^@"(.*)"$', expression).group(1)
        else:
            raise ValueError(f"Неподдерживаемое выражение: {expression}")

    def parse_blocks(self, text):
        """Обработка словарей (включая вложенные)"""
        if not text.startswith('([') or not text.endswith('])'):
            raise ValueError("Некорректный блок словаря")
        inner_content = text[2:-2].strip()  # Убираем ([ и ])
        return self.parse_dict(inner_content)

    def parse_dict(self, text):
        #Парсинг словаря, включая вложенные значения
        entries = self.split_entries(text)
        parsed_dict = {}
        for entry in entries:
            if ':' not in entry:
                continue
            key, value = entry.split(':', 1)
            key = key.strip()
            value = self.parse_value(value.strip())
            if not re.match(r'^[a-zA-Z][_a-zA-Z0-9]*$', key):
                raise ValueError(f"Некорректное имя ключа: {key}")
            parsed_dict[key] = value
        return parsed_dict

    def parse_value(self, value):
        #Определение типа значения: число, строка, константа или словарь
        if re.match(r'^\d+$', value):  # Число
            return int(value)
        elif re.match(r'^@"(.*)"$', value):  # Строка
            return re.match(r'^@"(.*)"$', value).group(1)
        elif re.match(r'^!{[a-zA-Z][_a-zA-Z0-9]*}$', value):  # Константа
            return self.evaluate(value)
        elif re.match(r'^\(\[.*\]\)$', value, re.DOTALL):  # Вложенный словарь
            return self.parse_blocks(value)  # Вызов для вложенных блоков
        else:
            raise ValueError(f"Неподдерживаемое значение: {value}")

    def split_entries(self, text):
        #Разделение записей в словаре с учётом вложенности
        entries = []
        current = []
        depth = 0

        for char in text:
            if char == ',' and depth == 0:
                entries.append(''.join(current).strip())
                current = []
            else:
                if char == '(' and text[text.index(char):].startswith('(['):
                    depth += 1
                elif char == ')' and depth > 0:
                    depth -= 1
                current.append(char)

        if current:
            entries.append(''.join(current).strip())
        return entries


def main():
    if len(sys.argv) != 2:
        print("Использование: main.py <путь_к_файлу>")
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        parser = ConfigParser()
        parsed_data = parser.parse(input_text)

        # Преобразование в TOML
        toml_output = toml.dumps(parsed_data)
        print(toml_output)
    except FileNotFoundError:
        print(f"Файл {input_path} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
