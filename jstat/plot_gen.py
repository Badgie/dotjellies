import platform

from lib import plot_cpu_avg_per_day as cpu_day, plot_cpu_avg_per_hour as cpu_hour, \
    plot_cpu_avg_per_minute as cpu_minute
from lib import plot_machine_avg_per_hour as machine_hour, \
    plot_machine_avg_per_day as machine_day, plot_machine_avg_per_minute as machine_minute


def gen():
    # cpu
    cpu_day(30, 'month')
    cpu_day(7, 'week')
    cpu_hour(240, 48, 'twoday')
    cpu_hour(120, 24, 'day')
    cpu_hour(60, 12, 'halfday')
    cpu_hour(30, 6, 'sixhour')
    cpu_hour(15, 3, 'threehour')
    cpu_hour(5, 1, 'hour')
    cpu_minute(3, 30, 'thirty')
    cpu_minute(1, 10, 'ten')

    # response time
    machine_day(30, 'month', 'Response time', col='res_time')
    machine_day(7, 'week', 'Response time', col='res_time')
    machine_hour(240, 48, 'twoday', 'Response time', col='res_time')
    machine_hour(120, 24, 'day', 'Response time', col='res_time')
    machine_hour(60, 12, 'halfday', 'Response time', col='res_time')
    machine_hour(30, 6, 'sixhour', 'Response time', col='res_time')
    machine_hour(15, 3, 'threehour', 'Response time', col='res_time')
    machine_hour(5, 1, 'hour', 'Response time', col='res_time')
    machine_minute(3, 30, 'thirty', 'Response time', col='res_time')
    machine_minute(1, 10, 'ten', 'Response time', col='res_time')

    # memory
    machine_day(30, 'month', 'Memory', col='memory')
    machine_day(7, 'week', 'Memory', col='memory')
    machine_hour(240, 48, 'twoday', 'Memory', col='memory')
    machine_hour(120, 24, 'day', 'Memory', col='memory')
    machine_hour(60, 12, 'halfday', 'Memory', col='memory')
    machine_hour(30, 6, 'sixhour', 'Memory', col='memory')
    machine_hour(15, 3, 'threehour', 'Memory', col='memory')
    machine_hour(5, 1, 'hour', 'Memory', col='memory')
    machine_minute(3, 30, 'thirty', 'Memory', col='memory')
    machine_minute(1, 10, 'ten', 'Memory', col='memory')

    # core temp; only for rpi
    if platform.uname().node == 'raspberrypi':
        machine_day(30, 'month', 'Core temperature', col='core_temp')
        machine_day(7, 'week', 'Core temperature', col='core_temp')
        machine_hour(240, 48, 'twoday', 'Core temperature', col='core_temp')
        machine_hour(120, 24, 'day', 'Core temperature', col='core_temp')
        machine_hour(60, 12, 'halfday', 'Core temperature', col='core_temp')
        machine_hour(30, 6, 'sixhour', 'Core temperature', col='core_temp')
        machine_hour(15, 3, 'threehour', 'Core temperature', col='core_temp')
        machine_hour(5, 1, 'hour', 'Core temperature', col='core_temp')
        machine_minute(3, 30, 'thirty', 'Core temperature', col='core_temp')
        machine_minute(1, 10, 'ten', 'Core temperature', col='core_temp')


if __name__ == '__main__':
    gen()
