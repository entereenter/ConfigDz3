# ConfigDz3

## Вариант 15

Разработать инструмент командной строки для учебного конфигурационного 
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из 
входного формата в выходной. Синтаксические ошибки выявляются с выдачей 
сообщений.

Входной текст на учебном конфигурационном языке принимается из 
файла, путь к которому задан ключом командной строки. Выходной текст на 
языке toml попадает в стандартный вывод.

Однострочные комментарии:

#Это однострочный комментарий

Словари:

([

 имя : значение,

 имя : значение,

 имя : значение,

 ...

])

Имена:

[a-zA-Z][_a-zA-Z0-9]*

Значения:

• Числа.

• Строки.

• Словари.

Строки:

@"Это строка"

Объявление константы на этапе трансляции:

let имя = значение;

Вычисление константы на этапе трансляции:

!{имя}

Результатом вычисления константного выражения является значение.