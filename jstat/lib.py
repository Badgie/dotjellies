import re
import matplotlib.pyplot as plt
import time

from datetime import datetime
from statistics import mean
from typing import Tuple, List

import db

COLORS = {'blue': (.12, .639, .863), 'gray': (.196, .196, .204)}
GRAPH_DIR = 'static/img/graphs'

"""
Storage
"""


def storage() -> list:
    drives = [x for x in db.get_recent_storage() if x]
    return [{'total': x[2], 'used': x[3], 'avail': x[4], 'percent': x[5].replace('P', '%'),
             'percent_int': int(x[5].strip('%'))} for x in drives]


"""
Machine
"""


def machine_status() -> dict:
    status_file = db.get_recent_machine()
    del status_file[0]  # stamp not needed here
    return {re.search(r'[a-zA-Z ]{2,}', x.split(':')[0]).group().lstrip('m'):
            x.split(':')[1].strip().replace('\x1b[0m', '')
            for x in status_file if x != 'null'}


def plot_machine_avg_per_day(days: int, period: str, col_name: str, col: str = '*'):
    lim = __lim(col)
    grps, stamps = __get_main_machine_data_days(col)
    avg = __avg_by_stamp(grps)

    x = list(avg.keys()) if len(avg.keys()) < days else \
        [list(avg.keys())[day] for day in range(len(avg.keys()) - days, len(avg.keys()))]
    y = list(avg.values()) if len(avg.values()) < days else \
        [list(avg.values())[day] for day in range(len(avg.values()) - days, len(avg.keys()))]

    __jstat_plot(x=x, y=y, title=f'{col_name} over the last {days} days (1 day interval)',
                 lim=lim, ylabel=col_name)
    plt.savefig(f'{GRAPH_DIR}/{col}/{col}_plot_avg_{period}.png', format='png',
                facecolor=COLORS['gray'])
    plt.clf()


def plot_machine_avg_per_minute(interval: int, hours: int, period: str, col_name: str,
                                col: str = '*'):
    lim = __lim(col)
    grps, stamps = __get_main_machine_data_minutes(interval, hours, col)
    avg = __avg_by_stamp(grps)

    __jstat_plot(x=list(avg.keys()), y=list(avg.values()),
                 title=f'{col_name} over the last {hours} hour{"s" if hours > 1 else ""} '
                       f'({interval}m interval)',
                 lim=lim, ylabel=col_name)
    plt.savefig(f'{GRAPH_DIR}/{col}/{col}_plot_avg_minute_{period}.png', format='png',
                facecolor=COLORS['gray'])
    plt.clf()


def __lim(col: str) -> list:
    if col == 'memory':
        return [0, __mem_max(col)]
    else:
        return [0, 150]


def __mem_max(col: str) -> int:
    mem = db.get_recent_machine_col(col)
    return int(mem[1].split('/')[1].replace('MiB\x1b[0m', ''))


def __get_main_machine_data(col: str) -> list:
    data = db.get_all_machine(col if col == '*' else f'time, {col}')
    if col == 'res_time':
        data = [[int(x[0]), float(re.search(r'([0-9]+\.?[0-9]*)', x[1]).groups()[0])] for x in data]
    elif col == 'memory':
        data = [[int(x[0]), int(x[1].split('/')[0].split(':')[1].strip('\x1b[0m MiB'))]
                for x in data]
    return data


def __get_main_machine_data_days(col: str) -> Tuple[dict, List[str]]:
    data = __get_main_machine_data(col)
    stamps = [datetime.fromtimestamp(int(x[0])).strftime('%b %d') for x in data]
    values = [x[1] for x in data]
    grps = __group_by_stamp_day(data, stamps, values)
    return grps, stamps


def __get_main_machine_data_minutes(interval: int, hours: int, col: str)\
        -> Tuple[dict, List[str]]:
    now = round(time.time())
    data = __get_main_machine_data(col)
    stamps = __create_minute_stamps(interval, hours, now)
    values = [x[1] for x in data]
    grps = __group_by_stamp_minutes(data, stamps, values, interval, now, hours)
    return grps, list(grps.keys())


"""
CPU
"""


def __cpu(cpus: list) -> dict:
    # [id, user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice]
    # http://man7.org/linux/man-pages/man5/proc.5.html
    # /proc/stat
    cpu_map = {x[1]: {'raw': [int(x[y]) for y in range(2, len(x))]} for x in cpus}
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


def __cpu_diff(cpus: list) -> dict:
    new, old = __cpu(cpus[len(cpus) // 2:]), __cpu(cpus[:len(cpus) // 2])
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
        stat['guest_nice_period'] = __sub(new[cid]['guest_nice_time'], old[cid]['guest_nice_time'])
        stat['idle_period_full'] = __sub(new[cid]['idle_time_full'], old[cid]['idle_time_full'])
        stat['system_period_full'] = __sub(new[cid]['system_time_full'],
                                           old[cid]['system_time_full'])
        stat['virtual_period_full'] = __sub(new[cid]['virtual_time_full'],
                                            old[cid]['virtual_time_full'])
    return cpu_stat


def __sub(x, y) -> int:
    return x - y if x > y else 0


def cpu_load(cpus: list, str_format: bool = True, plot: bool = False) -> dict:
    _stat = __cpu_diff(cpus)
    percentages = {}
    for cid, stat in _stat.items():
        total = 1 if stat['total_period'] == 0 else stat['total_period']
        user = stat['user_period'] / total * 100
        nice = stat['nice_period'] / total * 100
        sys_all = stat['system_period_full'] / total * 100
        steal_guest = (stat['steal_period'] + stat['guest_period']) / total * 100
        percentages[cid] = f'{user + nice + sys_all + steal_guest:.2f}%' if str_format else \
            user + nice + sys_all + steal_guest
    if not plot:
        del percentages['cpu']
    return percentages


def __get_main_cpu_data() -> list:
    return [entry for entry in db.get_all_cpu() if entry[1] == 'cpu']


def __get_main_cpu_data_days() -> Tuple[dict, List[str]]:
    """
    Gets all available CPU data from database, groups them by timestamp with data, stamp, and load
    percentage. Returns a dict on the form {data: list, stamp: str, load: float} and a list of
    present stamps as a tuple.
    """
    data = __get_main_cpu_data()
    stamps = [datetime.fromtimestamp(int(x[0])).strftime('%b %d') for x in data]
    percentages = [cpu_load([data[x - 1], data[x]], False, True) for x in range(1, len(data))]
    # no percentage entry for first index
    del data[0]
    # normalize stamps
    del stamps[0]
    grps = __group_by_stamp_day(data, stamps, [x['cpu'] for x in percentages])
    return grps, stamps


def __get_main_cpu_data_minutes(interval: int, hours: int) -> Tuple[dict, List[str]]:
    now = round(time.time())
    data = __get_main_cpu_data()
    stamps = __create_minute_stamps(interval, hours, now)
    percentages = [cpu_load([data[x - 1], data[x]], False, True) for x in range(1, len(data))]
    # no percentage entry for first index
    del data[0]
    grps = __group_by_stamp_minutes(data, stamps, [x['cpu'] for x in percentages], interval, now,
                                    hours)
    return grps, list(grps.keys())


def plot_cpu_avg_per_day(days: int, period: str):
    """
    Plots the average CPU load over the last {days} days, with daily interval.
    """
    grps, stamps = __get_main_cpu_data_days()
    avg = __avg_by_stamp(grps)

    x = list(avg.keys()) if len(avg.keys()) < days else \
        [list(avg.keys())[day] for day in range(len(avg.keys()) - days, len(avg.keys()))]
    y = list(avg.values()) if len(avg.values()) < days else \
        [list(avg.values())[day] for day in range(len(avg.values()) - days, len(avg.keys()))]

    __jstat_plot(x=x, y=y, title=f'CPU load over the last {days} days (1 day interval)',
                 lim=[0, 100], ylabel='CPU load')
    plt.savefig(f'{GRAPH_DIR}/cpu/cpu_plot_avg_{period}.png', format='png', facecolor=COLORS['gray'])
    plt.clf()


def plot_cpu_avg_per_minute(interval: int, hours: int, period: str):
    """
    Plots the average CPU load over the last {hours} hours, with {interval} minute interval.
    """
    grps, stamps = __get_main_cpu_data_minutes(interval, hours)
    avg = __avg_by_stamp(grps)

    __jstat_plot(x=list(avg.keys()), y=list(avg.values()),
                 title=f'CPU load over the last {hours} hour{"s" if hours > 1 else ""} '
                       f'({interval}m interval)',
                 lim=[0, 100], ylabel='CPU load')
    plt.savefig(f'{GRAPH_DIR}/cpu/cpu_plot_avg_minute_{period}.png', format='png',
                facecolor=COLORS['gray'])
    plt.clf()


"""
Plot generation
"""


def __jstat_plot(x: list, y: list, title: str, lim: list, ylabel: str):
    """
    Sets up plot layout.
    """
    plt.plot(x, y, color=COLORS['blue'])
    plt.gca().set_facecolor(COLORS['gray'])
    plt.gca().set_ylim(lim)
    plt.title(title, color=COLORS['blue'])
    plt.tick_params(color='white')
    plt.ylabel(ylabel, color='white')
    [i.set_color('white') for i in plt.gca().spines.values()]
    [i.set_color('white') for i in plt.gca().get_xticklabels()]
    [i.set_color('white') for i in plt.gca().get_yticklabels()]


def __group_by_stamp_minutes(data: list, stamps: List[dict], percentages: list,
                             interval: int, now: int, hours: int) -> dict:
    grps = {x['stamp']: [] for x in stamps}
    checkpoint = 0
    interval_sec = interval * 60
    first_stamp = now - (now % (interval * 60)) - (hours * 3600)
    stamp_int = now - (now % (interval * 60))

    for x in range(len(stamps)):
        if stamps[x]['real'] > stamp_int:
            stamp_int -= interval * 60
        else:
            for y in range(checkpoint, len(data)):
                if not __is_valid(first_stamp, int(data[y][0])):
                    continue
                if __is_in_next(stamps[x]['real'], int(data[y][0]), interval_sec):
                    checkpoint = y
                    break
                grps[stamps[x]['stamp']].append({'data': data[y], 'stamp': stamps[x]['real'],
                                                 'val': percentages[y]})
    return grps


def __group_by_stamp_day(data: list, stamps: list, percentages: list) -> dict:
    grps = {stamp: [] for stamp in stamps}
    for x in range(len(data)):
        grps[stamps[x]].append({'data': data[x], 'stamp': stamps[x], 'val': percentages[x]})
    return grps


def __is_in_next(stamp: int, cur_entry: int, interval_sec: int) -> bool:
    if stamp > cur_entry > stamp - interval_sec:
        return False
    return True


def __is_valid(first_stamp: int, cur_entry: int) -> bool:
    if first_stamp > cur_entry:
        return False
    return True


def __create_minute_stamps(interval: int, hours: int, now: int) -> list:
    last = now - (now % (interval * 60))
    first = last - (hours * 3600)
    return [{'stamp': datetime.fromtimestamp(x).strftime('%H:%M'), 'real': x}
            for x in range(first, last + 1, interval * 60)]


def __avg_by_stamp(grps: dict) -> dict:
    return {stamp: mean([x['val'] for x in entries]) for stamp, entries in grps.items() if entries}
