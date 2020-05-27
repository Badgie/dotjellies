#!/bin/bash
db='static/db/jstat.db'
url='jelly.badgy.eu'


init_db() {
    sqlite3 "${db}" << EOQ
        attach "${db}" as jstat;
        CREATE TABLE machine (time TEXT, os TEXT, host TEXT, uptime TEXT, kernel TEXT, cpu TEXT, memory TEXT, core_temp INTEGER, res_time INTEGER, web_server TEXT);
        CREATE TABLE storage (time TEXT, drive_id TEXT, size TEXT, used TEXT, avail TEXT, percentage TEXT);
        CREATE TABLE cpu (time TEXT, cpu_id TEXT, user TEXT, nice TEXT, system TEXT, idle TEXT, iowait TEXT, irq TEXT, softirq TEXT, steal TEXT, guest TEXT, guest_nice TEXT);
EOQ
}

create_table() {
    if [[ $1 == 'machine' ]]; then
        name='machine'
        cols='time TEXT, os TEXT, host TEXT, uptime TEXT, kernel TEXT, cpu TEXT, memory TEXT, core_temp INTEGER, res_time INTEGER, web_server TEXT'
    elif [[ $1 == 'cpu' ]]; then
        name='cpu'
        cols='time TEXT, cpu_id TEXT, user TEXT, nice TEXT, system TEXT, idle TEXT, iowait TEXT, irq TEXT, softirq TEXT, steal TEXT, guest TEXT, guest_nice TEXT'
    elif [[ $1 == 'storage' ]]; then
        name='storage'
        cols='time TEXT, drive_id TEXT, size TEXT, used TEXT, avail TEXT, percentage TEXT'
    else
        echo "Error: cannot identify table $1"
        return
    fi
    sqlite3 "${db}" << EOQ
        attach "${db}" as jstat;
        CREATE TABLE $name ($cols);
EOQ
}

check_init() {
    if [[ ! -f "$db" ]]; then
        init_db
    fi

    tables=('machine' 'cpu' 'storage')
    for table in "${tables[@]}"; do
        check=$(sqlite3 -line "${db}" "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';" | sed -r 's/ name = //g')
        if [[ ! $check == "$table" ]]; then
            create_table "$table"
        fi
    done
}

# inp: stamp, os, host, uptime, kernel, cpu, memory, core_temp, res_time, web_server
add_machine() {
    stamp=$(date +%s)

    neo=$(neofetch)

    os=$(echo "$neo" | grep 'OS')
    host=$(echo "$neo" | grep 'Host')
    uptime=$(echo "$neo" | grep 'Uptime')
    kernel=$(echo "$neo" | grep 'Kernel')
    cpu=$(echo "$neo" | grep 'CPU')
    memory=$(echo "$neo" | grep 'Memory')
    # rpi only
    temp=$(vcgencmd measure_temp | sed -r "s/'C//g" | sed -r "s/temp=/Core temp: /g" )

    if [[ $temp == 'bash: vcgencmd: command not found' ]]; then
        temp=null
    fi

    res="$(curl -o /dev/null -s -w %\{time_total\} jelly.badgy.eu)"
    res_time=$(echo "$res * 1000" | bc -l | xargs printf "%.2f")

    web_server=$(curl -I "$url" | grep 'Server:' | tr "/" " ")

    sqlite3 "${db}" << EOQ
        attach "${db}" as jstat;
        INSERT INTO jstat.machine VALUES('${stamp}', '${os}', '${host}', '${uptime}', '${kernel}', '${cpu}', '${memory}', '${temp}', 'Response time: ${res_time} ms', '${web_server}');
EOQ
}

# inp: stamp, id, size, used, avail, percentage
add_storage() {
    stamp=$(date +%s)
    mapfile -t drives < <(df -h | grep '/dev/sd')
    for drive in "${drives[@]}"; do
        read -r -a split <<< "${drive}"
        sqlite3 "${db}" << EOQ
            attach "${db}" as jstat;
            INSERT INTO jstat.storage VALUES('${stamp}', '${split[0]}', '${split[1]}', '${split[2]}', '${split[3]}', '${split[4]}');
EOQ
    done
}

# inp: stamp, id, user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice
add_cpu() {
    stamp=$(date +%s)
    mapfile -t cpus < <(< /proc/stat grep 'cpu')
    for cpu in "${cpus[@]}"; do
        read -r -a split <<< "${cpu}"
        sqlite3 "${db}" << EOQ
            attach "${db}" as jstat;
            INSERT INTO jstat.cpu VALUES('${stamp}', '${split[0]}', '${split[1]}', '${split[2]}', '${split[3]}', '${split[4]}', '${split[5]}', '${split[6]}', '${split[7]}', '${split[8]}', '${split[9]}', '${split[10]}');
EOQ
    done
}

if [[ ! -d static/db ]]; then
    mkdir static/db
fi

# ensure db exists
check_init
# get machine data
add_machine
# get storage data
add_storage
# get cpu data
add_cpu