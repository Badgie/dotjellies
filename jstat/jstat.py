from flask import Flask, render_template
from requests import get
from subprocess import Popen, run, PIPE

jstat = Flask(__name__)

URL = 'https://jelly.badgy.eu/'
data = {'content': {'header': 'Jellyfin server stats',
                    'intro': 'Server statistics for the Jellyfin server at '},
        'server': {},
        'url': URL}


@jstat.route('/', methods=['GET'])
def index():
    data['status_text'] = 'running' if server_status() else 'down'
    data['status'] = server_status()
    data['storage'] = storage()
    data['server']['OS'] = get_os()
    data['server']['Host'] = get_host()
    data['server']['Kernel'] = get_kernel()
    data['server']['Uptime'] = get_uptime()
    data['server']['CPU'] = get_cpu()
    data['server']['Memory'] = get_mem()
    return render_template('index.html', text=data['content'], server=data['server'],
                           status=data)


def server_status() -> bool:
    try:
        res = get(URL)
        print(res.headers)
        data['server']['Response time (ms)'] = res.elapsed.microseconds // 1000
        data['server']['Web server'] = res.headers['Server'].split('/')[0]
    except ConnectionError:
        return False
    return True


def storage() -> list:
    sp = Popen(['df', '-h'], stdout=PIPE, shell=True)
    drives = run(['grep', '/dev/sd'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split('\n')
    drives = [x.split() for x in drives if x]
    return [{'total': x[1], 'used': x[2], 'avail': x[3], 'percent': x[4],
             'percent_int': int(x[4].strip('%'))} for x in drives]


def get_os() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'OS'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split(':')[1].strip().strip('\x1b[0m')


def get_host() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'Host'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split(':')[1].strip().strip('\x1b[0m')


def get_uptime() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'Uptime'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split(':')[1].strip().strip('\x1b[0m')


def get_kernel() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'Kernel'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8') \
        .split(':')[1].strip().strip('\x1b[0m')


def get_cpu() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'CPU'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split(':')[1].strip().strip('\x1b[0m')


def get_mem() -> str:
    sp = Popen(['neofetch'], stdout=PIPE)
    return run(['grep', 'Memory'], stdin=sp.stdout, stdout=PIPE).stdout.decode('utf-8')\
        .split(':')[1].strip().strip('\x1b[0m')


if __name__ == '__main__':
    jstat.run(host='0.0.0.0', port=8887)
