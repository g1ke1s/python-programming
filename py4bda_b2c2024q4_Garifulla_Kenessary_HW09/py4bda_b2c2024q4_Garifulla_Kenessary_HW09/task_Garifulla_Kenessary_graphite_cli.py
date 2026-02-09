#!/usr/bin/env python3
import re
import argparse
from datetime import datetime
import math

def parse_log_line(line):
    """
    Парсит строку лога, которая имеет формат:
    YYYYMMDD_HHMMSS.mmm <logger> <level> <message>
    Например:
    20231003_154500.123 task_Surname_Name_web_service_log DEBUG start processing query: python test
    """
    pattern = r'^(?P<date>\d{8}_\d{6})\.(?P<msecs>\d{3})\s+(?P<logger>\S+)\s+(?P<level>\S+)\s+(?P<message>.+)$'
    match = re.match(pattern, line)
    if match:
        date_str = match.group('date')
        msecs = int(match.group('msecs'))
        dt = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        timestamp = dt.timestamp() + msecs / 1000.0
        return {
            'timestamp': timestamp,
            'logger': match.group('logger'),
            'level': match.group('level'),
            'message': match.group('message')
        }
    return None

def process_log_file(filename):
    """
    Обрабатывает лог-файл, извлекая для каждого запроса:
    - start_time (время начала обработки),
    - finish_time (время окончания обработки),
    - article_count (число найденных статей).
    
    Предполагается, что для каждого запроса имеются сообщения:
      - "start processing query: <query>"
      - "found <article_count> articles for query: <query>"
      - "finish processing query: <query>"
    """
    records = []  # Список записей для каждого запроса
    active = {}   # Активные (в процессе обработки) запросы; ключ – текст запроса, значение – список индексов записей
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parsed = parse_log_line(line)
            if not parsed:
                continue
            msg = parsed['message']
            # Обработка начала запроса
            if msg.startswith("start processing query: "):
                query = msg[len("start processing query: "):].strip()
                record = {
                    'query': query,
                    'start_time': parsed['timestamp'],
                    'finish_time': None,
                    'article_count': None
                }
                records.append(record)
                active.setdefault(query, []).append(len(records) - 1)
            # Обработка найденного числа статей
            elif msg.startswith("found "):
                # Формат сообщения: "found <article_count> articles for query: <query>"
                m = re.match(r'found\s+(\d+)\s+articles\s+for\s+query:\s+(.+)', msg)
                if m:
                    article_count = int(m.group(1))
                    query = m.group(2).strip()
                    if query in active and active[query]:
                        idx = active[query][0]
                        records[idx]['article_count'] = article_count
            # Обработка завершения запроса
            elif msg.startswith("finish processing query: "):
                query = msg[len("finish processing query: "):].strip()
                if query in active and active[query]:
                    idx = active[query].pop(0)
                    records[idx]['finish_time'] = parsed['timestamp']
    return records

def generate_graphite_commands(records, host, port):
    """
    Для каждого запроса генерируются две команды:
      - Количество найденных статей:
        echo "wiki_search.article_found <article_count> <finish_ts>" | nc -N <host> <port>
      - Сложность (разница finish_time - start_time):
        echo "wiki_search.complexity <complexity> <finish_ts>" | nc -N <host> <port>
    
    Временная метка (finish_ts) округляется вниз до целых секунд.
    """
    commands = []
    for record in records:
        if record['start_time'] is not None and record['finish_time'] is not None:
            complexity = record['finish_time'] - record['start_time']
            finish_ts = int(record['finish_time'])  # округление вниз до целых секунд
            article_count = record['article_count'] if record['article_count'] is not None else 0
            cmd1 = f'echo "wiki_search.article_found {article_count} {finish_ts}" | nc -N {host} {port}'
            cmd2 = f'echo "wiki_search.complexity {complexity:.3f} {finish_ts}" | nc -N {host} {port}'
            commands.append(cmd1)
            commands.append(cmd2)
    return commands

def main():
    parser = argparse.ArgumentParser(description="Парсинг логов Wikipedia Search и генерация команд для Graphite")
    parser.add_argument("--process", required=True, help="Путь к лог-файлу (например, wiki_search_app.log)")
    parser.add_argument("--host", default="localhost", help="Хост Graphite (по умолчанию: localhost)")
    parser.add_argument("--port", type=int, default=2003, help="Порт Graphite (по умолчанию: 2003)")
    args = parser.parse_args()
    
    records = process_log_file(args.process)
    commands = generate_graphite_commands(records, args.host, args.port)
    for cmd in commands:
        print(cmd)

if __name__ == '__main__':
    main()

