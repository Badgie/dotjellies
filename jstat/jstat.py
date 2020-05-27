import platform

from flask import Flask, render_template, request
from requests import get

import db
import lib

jstat = Flask(__name__)

status = {'content': {'header': 'Jellyfin server status',
                      'intro': 'Server status for the Jellyfin server at '},
          'url': 'https://jelly.badgy.eu/', 'name': 'jelly.badgy.eu', 'cpu': {}}
graphs = {'types': {'cpu': {'base': 'cpu_plot_avg_', 'front': 'minute_hour',
                            'full_path': 'img/graphs/cpu/cpu_plot_avg_minute_hour.png',
                            'header_name': 'CPU'},
                    'memory': {'base': 'memory_plot_avg_', 'front': 'minute_hour',
                               'full_path': 'img/graphs/memory/memory_plot_avg_minute_hour.png',
                               'header_name': 'Memory'},
                    'res_time': {'base': 'res_time_plot_avg_', 'front': 'minute_hour',
                                 'full_path': 'img/graphs/res_time/res_time_plot_avg_'
                                              'minute_hour.png',
                                 'header_name': 'Response time'}},
          'intervals': ['minute_hour', 'minute_threehour', 'minute_sixhour',
                        'minute_halfday', 'minute_day', 'minute_twoday', 'week', 'month'],
          'path': 'img/graphs'}

if platform.uname().node == 'raspberrypi':
    graphs['types']['core_temp'] = {'base': 'core_temp_plot_avg_', 'front': 'minute_hour',
                                    'full_path': 'img/graphs/core_temp/core_temp_plot_avg_'
                                                 'minute_hour',
                                    'header_name': 'Core temp'}


@jstat.route('/', methods=['GET'])
def index():
    status['server'] = lib.machine_status()
    status['storage'] = lib.storage()
    status['cpu']['load'] = lib.cpu_load(db.get_recent_cpu_pair())
    _server_status()
    return render_template('index.html', text=status['content'], server=status['server'],
                           status=status, cpu=status['cpu'], graph=graphs, len=len)


@jstat.route('/graph', methods=['GET'])
def graph():
    target = request.args['target']
    paths = [f'{graphs["path"]}/{target}/{graphs["types"][target]["base"]}{inter}.png'
             for inter in graphs['intervals']]
    return render_template('graphs.html', graphs=paths, info=graphs['types'][target])


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
