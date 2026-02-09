import logging
import re
import time
from datetime import datetime

from flask import Flask, request, jsonify
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

app = Flask(__name__)

# Настройка логирования с указанным форматом и датой
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y%m%d_%H%M%S"
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

@app.route('/api/search')
def api_search():
    query = request.args.get('query')
    if query is None:
        # Если параметр query отсутствует, считаем, что запрос валиден и возвращаем 0 найденных статей
        return jsonify({"version": 1.0, "article_count": 0})
    
    start_time = time.time()
    app.logger.debug("start processing query: %s", query)
    
    try:
        # Проксируем запрос к Википедии
        response = requests.get("https://en.wikipedia.org/w/index.php", params={"search": query})
        response.raise_for_status()
    except ConnectionError:
        app.logger.error("Wikipedia Search Engine is unavailable for query: %s", query)
        # При недоступности wikipedia.org возвращаем 503 с текстовым сообщением
        return "Wikipedia Search Engine is unavailable", 503

    # Попытка извлечь число найденных документов из HTML-страницы
    # Предполагается, что страница содержит шаблон вида "of <number> results"
    match = re.search(r'of\s+([\d,]+)\s+results', response.text)
    if match:
        count_str = match.group(1).replace(',', '')
        try:
            article_count = int(count_str)
        except ValueError:
            article_count = 0
    else:
        article_count = 0

    app.logger.info("found %s articles for query: %s", article_count, query)
    finish_time = time.time()
    app.logger.debug("finish processing query: %s", query)
    
    return jsonify({"version": 1.0, "article_count": article_count})

# Обработчик обращения к несуществующим route
@app.errorhandler(404)
def handle_404(error):
    return "This route is not found", 404

if __name__ == '__main__':
    app.run(debug=True)

