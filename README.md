Парсинг access логов


1. Выборка строк лога по указанной временной дельте.

python parser.py --logs-dir "/path/to/logs" filter-sessions 300


2. Выборка строк лога по указанному значению последнего поля лога

python parser.py --logs-dir "/path/to/logs" filter-orgs "Public Joint Stock Company Vimpel-Communications"


3. Удаление строк лога исходя из наличия дубликатов в 7-ом поле лога

python parser.py --logs-dir "/path/to/logs" remove-dup-logins


4. Построение статистики по количеству совпадений значений в последнем поле лога.

python parser.py --logs-dir "/path/to/logs" stat-orgs "stat_orgs.txt"



В опциях 1, 2, 3 исходные логи перезаписываются новыми данными.
