import re

from flask import Flask, render_template
from requests import get

import config

jstat = Flask(__name__)

status = {'content': {'header': 'Jellyfin server status',
                      'intro': 'Server status for the Jellyfin server at '},
          'url': 'https://jelly.badgy.eu/', 'name': 'jelly.badgy.eu', 'cpu': {}}


@jstat.route('/', methods=['GET'])
def index():
    status['server'] = _machine_status()
    status['storage'] = _storage()
    status['cpu']['load'] = _cpu_load()
    _server_status()
    return render_template('index.html', text=status['content'], server=status['server'],
                           status=status, cpu=status['cpu'])


def _server_status():
    try:
        res = get(status['url'])
        status['server']['Response time (ms)'] = res.elapsed.microseconds // 1000
        status['server']['Web server'] = res.headers['Server'].replace('/', ' ')
        status['status'] = True
        status['status_text'] = 'running'
    except ConnectionError:
        status['status'] = False
        status['status_text'] = 'down'


def _storage() -> list:
    drives = config.get_storage_cfg().get('drives').split(':')
    drives = [x.split() for x in drives if x]
    return [{'total': x[0], 'used': x[1], 'avail': x[2], 'percent': x[3].replace('P', '%'),
             'percent_int': int(x[3].strip('P'))} for x in drives]


def _machine_status() -> dict:
    status_file = list(config.get_machine_cfg().values())
    return {re.search(r'[a-zA-Z ]{2,}', x.split(':')[0]).group().lstrip('m'):
            x.split(':')[1].strip().replace('\x1b[0m', '').replace('!', '/') for x in status_file}


def __cpu(ver: str) -> dict:
    cpus = config.get_cpu_cfg().get(f'cpu_{ver}').split(':')
    # [id, user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice]
    # http://man7.org/linux/man-pages/man5/proc.5.html
    # /proc/stat
    cpus = [x.split() for x in cpus if x]
    cpu_map = {x[0]: {'raw': [int(x[y]) for y in range(1, len(x))]} for x in cpus}
    for cid, stat in cpu_map.items():
        stat['total_time'] = sum(stat['raw'])
        stat['user_time'] = stat['raw'][0]
        stat['nice_time'] = stat['raw'][1]
        stat['system_time'] = stat['raw'][2]
        stat['idle_time'] = stat['raw'][3]
        stat['io_wait_time'] = stat['raw'][4]
        stat['irq_time'] = stat['raw'][5]
        stat['soft_irq_time'] = stat['raw'][6]
        stat['steal_time'] = stat['raw'][7]
        stat['guest_time'] = stat['raw'][8]
        stat['guest_nice_time'] = stat['raw'][9]
        stat['idle_time_full'] = stat['idle_time'] + stat['io_wait_time']
        stat['system_time_full'] = stat['system_time'] + stat['irq_time'] + stat['soft_irq_time']
        stat['virtual_time_full'] = stat['guest_time'] + stat['guest_nice_time']
    return cpu_map


def __cpu_diff() -> dict:
    new, old = __cpu('new'), __cpu('old')
    if not new or not old:
        return {}
    cpu_stat = new.copy()
    for cid, stat in cpu_stat.items():
        stat['total_period'] = __sub(new[cid]['total_time'], old[cid]['total_time'])
        stat['user_period'] = __sub(new[cid]['user_time'], old[cid]['user_time'])
        stat['nice_period'] = __sub(new[cid]['nice_time'], old[cid]['nice_time'])
        stat['idle_period'] = __sub(new[cid]['idle_time'], old[cid]['idle_time'])
        stat['io_wait_period'] = __sub(new[cid]['io_wait_time'], old[cid]['io_wait_time'])
        stat['irq_period'] = __sub(new[cid]['irq_time'], old[cid]['irq_time'])
        stat['soft_irq_period'] = __sub(new[cid]['soft_irq_time'], old[cid]['soft_irq_time'])
        stat['steal_period'] = __sub(new[cid]['steal_time'], old[cid]['steal_time'])
        stat['guest_period'] = __sub(new[cid]['guest_time'], old[cid]['guest_time'])
        stat['gust_nice_period'] = __sub(new[cid]['guest_nice_time'], old[cid]['guest_nice_time'])
        stat['idle_period_full'] = __sub(new[cid]['idle_time_full'], old[cid]['idle_time_full'])
        stat['system_period_full'] = __sub(new[cid]['system_time_full'],
                                           old[cid]['system_time_full'])
        stat['virtual_period_full'] = __sub(new[cid]['virtual_time_full'],
                                            old[cid]['virtual_time_full'])
    return cpu_stat


def __sub(x, y) -> int:
    return x - y if x > y else 0


def _cpu_load() -> dict:
    _stat = __cpu_diff()
    percentages = {}
    for cid, stat in _stat.items():
        total = 1 if stat['total_period'] == 0 else stat['total_period']
        user = stat['user_period'] / total * 100
        nice = stat['nice_period'] / total * 100
        sys_all = stat['system_period_full'] / total * 100
        steal_guest = (stat['steal_period'] + stat['guest_period']) / total * 100
        percentages[cid] = f'{user + nice + sys_all + steal_guest:.2f}%'
    del percentages['cpu']
    return percentages


if __name__ == '__main__':
    jstat.run(host='0.0.0.0', port=8887)
