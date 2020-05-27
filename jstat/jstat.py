from flask import Flask, render_template
from requests import get

import db
import lib

jstat = Flask(__name__)

status = {'content': {'header': 'Jellyfin server status',
                      'intro': 'Server status for the Jellyfin server at '},
          'url': 'https://jelly.badgy.eu/', 'name': 'jelly.badgy.eu', 'cpu': {}}


@jstat.route('/', methods=['GET'])
def index():
    status['server'] = lib.machine_status()
    status['storage'] = lib.storage()
    status['cpu']['load'] = lib.cpu_load(db.get_recent_cpu_pair())
    _server_status()
    return render_template('index.html', text=status['content'], server=status['server'],
                           status=status, cpu=status['cpu'])


def _server_status():
    try:
        get(status['url'])
        status['status'] = True
        status['status_text'] = 'running'
    except ConnectionError:
        status['status'] = False
        status['status_text'] = 'down'


if __name__ == '__main__':
    jstat.run(host='0.0.0.0', port=8887)
