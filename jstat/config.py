from configparser import ConfigParser

CFG_FILE = 'jstat.conf'


def _open_config() -> ConfigParser:
    c = ConfigParser()
    with open(CFG_FILE, 'r') as f:
        c.read_file(f)
    return c


def get_machine_cfg():
    return _open_config()['machine']


def get_storage_cfg():
    return _open_config()['storage']


def get_cpu_cfg():
    return _open_config()['cpu']
