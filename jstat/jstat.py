from flask import Flask, render_template
from requests import get
import re

jstat = Flask(__name__)

URL = 'https://jelly.badgy.eu/'
data = {'content': {'header': 'Jellyfin server stats',
                    'intro': 'Server statistics for the Jellyfin server at '},
        'url': URL, 'name': 'jelly.badgy.eu'}


@jstat.route('/', methods=['GET'])
def index():
    data['server'] = _machine_status()
    data['storage'] = _storage()
    _server_status()
    return render_template('index.html', text=data['content'], server=data['server'],
                           status=data)


def _server_status():
    try:
        res = get(URL)
        data['server']['Response time (ms)'] = res.elapsed.microseconds // 1000
        data['server']['Web server'] = ' '.join(x for x in res.headers['Server'].split('/'))
        data['status'] = True
        data['status_text'] = 'running'
    except ConnectionError:
        data['status'] = False
        data['status_text'] = 'down'


def _storage() -> list:
    with open('data/storage', 'r') as f:
        drives = f.readlines()
    drives = [x.split() for x in drives if x]
    return [{'total': x[1], 'used': x[2], 'avail': x[3], 'percent': x[4],
             'percent_int': int(x[4].strip('%'))} for x in drives]


def _machine_status() -> dict:
    with open('data/status', 'r') as f:
        status = f.readlines()
    return {re.search(r'[a-zA-Z]{2,}', x.split(':')[0]).group().lstrip('m'):
            x.split(':')[1].strip().replace('\x1b[0m', '') for x in status}


if __name__ == '__main__':
    jstat.run(host='0.0.0.0', port=8887)
