import platform

from lib import plot_cpu_avg_per_day as cpu_day, plot_cpu_avg_per_minute as cpu_minute
from lib import plot_machine_avg_per_minute as storage_minute, \
    plot_machine_avg_per_day as storage_day


def gen():
    # cpu
    cpu_day(30, 'month')
    cpu_day(7, 'week')
    cpu_minute(240, 48, 'twoday')
    cpu_minute(120, 24, 'day')
    cpu_minute(60, 12, 'halfday')
    cpu_minute(30, 6, 'sixhour')
    cpu_minute(15, 3, 'threehour')
    cpu_minute(5, 1, 'hour')

    # response time
    storage_day(30, 'month', 'Response time', col='res_time')
    storage_day(7, 'week', 'Response time', col='res_time')
    storage_minute(240, 48, 'twoday', 'Response time', col='res_time')
    storage_minute(120, 24, 'day', 'Response time', col='res_time')
    storage_minute(60, 12, 'halfday', 'Response time', col='res_time')
    storage_minute(30, 6, 'sixhour', 'Response time', col='res_time')
    storage_minute(15, 3, 'threehour', 'Response time', col='res_time')
    storage_minute(5, 1, 'hour', 'Response time', col='res_time')

    # memory
    storage_day(30, 'month', 'Memory', col='memory')
    storage_day(7, 'week', 'Memory', col='memory')
    storage_minute(240, 48, 'twoday', 'Memory', col='memory')
    storage_minute(120, 24, 'day', 'Memory', col='memory')
    storage_minute(60, 12, 'halfday', 'Memory', col='memory')
    storage_minute(30, 6, 'sixhour', 'Memory', col='memory')
    storage_minute(15, 3, 'threehour', 'Memory', col='memory')
    storage_minute(5, 1, 'hour', 'Memory', col='memory')

    # core temp; only for rpi
    if platform.uname().node == 'raspberrypi':
        storage_day(30, 'month', 'Core temperature', col='core_temp')
        storage_day(7, 'week', 'Core temperature', col='core_temp')
        storage_minute(240, 48, 'twoday', 'Core temperature', col='core_temp')
        storage_minute(120, 24, 'day', 'Core temperature', col='core_temp')
        storage_minute(60, 12, 'halfday', 'Core temperature', col='core_temp')
        storage_minute(30, 6, 'sixhour', 'Core temperature', col='core_temp')
        storage_minute(15, 3, 'threehour', 'Core temperature', col='core_temp')
        storage_minute(5, 1, 'hour', 'Core temperature', col='core_temp')


if __name__ == '__main__':
    gen()
