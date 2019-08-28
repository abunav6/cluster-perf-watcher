import re
import time as t
from collections import defaultdict
from datetime import datetime as dt

import mysql.connector as mysql

import sql_conf
import sql_exec
import ssh_exec


def history_update(a, b):
    """
        adds the past values into the corresponding dicts
        :param a: the dict which needs to get the historical vals
        :param b: the dict which has all the hist vals
    """
    for k in list(b.keys()):
        a[k].append(b[k])


def update_max(a, b):
    """
    makes a list which contains the max values of the required param
    max CPU and MEM usages per user and process
    :param a: holds all the values of the corresponding param
    :param b: gets the max param value per user and per process
    """
    for k in a:
        if k not in b or (b[k] < a[k]):
            b[k] = a[k]


def update_avg(a, b, c, d):
    """
    makes a list which contains the avg values of the required param
    Avg CPU and MEM usages per user and process
    :param a: the dict which eventually contains all the average values that are required
    :param b: the dict which has all the data (not averages), the average is calc'd below
    :param c: contains the number of counts totally
    :param d: contains the number of counts for this instance
    """
    for k in list(b.keys()):
        row = b[k]
        if c == 1 or (k not in list(a.keys())):
            a[k] = row
        else:
            a[k] += (row / d) / c


def update_past(a, b):
    """
    makes a list which contains the past 3 values of the required param
    past_3 CPU and MEM usages per user and process
    if length is less than 3, it means we don't have the past 3 values, we append with 0
    :param a: has the data as is
    :param b: gets the past three values in a list
    """
    for k in a:
        if k not in list(b.keys()):
            # simply insert this data (most recent first)
            b[k] = [a[k]]
        elif len(b[k]) == 3:
            # delete the last element and update
            b[k] = [a[k], b[k][0], b[k][1]]
        elif len(b[k]) < 3:
            b[k].append(a[k])


def op(data_file,
       w___="[\d]+\s+([\w]+).\s+[\d]+\s+[\d]+\s+[\d]+\s+[\d]+\s+[\d]+"
            "\s.\s+([\d]+.[\d]+)\s+([\d]+.[\d]+)\s+........([\w]+.*)"):
    """
        :param data_file: this is the file to which the data is to be written
        :param w___: this is the regex statement to get data
        does the core operation, gets the data and returns it in dict form
    """
    users = []
    processes = []
    k = ssh_exec.get_data()
    data_file.write(k)
    data = re.findall(
        "%s" % w___,
        k)
    """
        k[0] User
        k[1] CPU usage
        k[2] MEM usage
        k[3] Process
        for k in data
    """
    for k in data:
        if k[0] not in users:
            users.append(k[0])
        if k[-1] not in processes:
            processes.append(k[-1])
    u_cpu = {k: 0.0 for k in users}
    u_mem = {k: 0.0 for k in users}
    p_cpu = {k: 0 for k in processes}
    p_mem = {k: 0 for k in processes}
    for k in data:
        u_cpu[k[0]] += float(k[1])
        u_mem[k[0]] += float(k[2])
    for k in data:
        p_cpu[k[-1]] += float(k[1])
        p_mem[k[-1]] += float(k[2])
    return u_cpu, u_mem, p_cpu, p_mem, users, processes


def add_data(a, b):
    """
    :param a: dictionary which needs to be added
    :param b: dictionary which gives the values
    """
    global lm
    try:
        for lm in b.keys():
            a[lm] = float(b[lm])
    except KeyError:
        a[lm] = float(int(b[lm]))


def get_temp(a):
    """
    :param a: is the dict which stores the past 3 param vals
    :return: the past three values of the corresponding param, in string format
    """
    b = [str(round(c, 3)) for c in a]
    while len(b) < 3:
        b.append('0.0')
    return b


def fetcher(query, dic, c):
    """
    :param query: is the SQL query
    :param dic: is the dictionary which needs to be updated
    :param c: is the cursor
    """
    c.execute(query)
    res_set = c.fetchall()
    for k in res_set:
        dic[k[0]] = k[1]


def main():
    global max_cpu, max_mem
    users = []
    process = []
    avg_cpu_u, avg_cpu_p, avg_mem_u, avg_mem_p, past_cpu_u, past_mem_u, past_cpu_p, past_mem_p, hist_avg_cu, \
    hist_avg_cp, hist_avg_mu, hist_avg_mp, histmax_c, histmax_m = [defaultdict(list) for _ in range(14)]
    dbb = mysql.connect(host=sql_conf.host, user=sql_conf.uname, passwd=sql_conf.pwd,
                        auth_plugin=sql_conf.auth)
    cursor = dbb.cursor(buffered=True)
    data_file = open("data.txt", "w+")
    data_file.flush()
    cursor.execute("CREATE database IF NOT EXISTS dbb;")
    cursor.execute("USE dbb;")
    sql_exec.create_tables(cursor)
    if input("Enter Y to clear all data and anything else to continue:\n").lower() == "y":
        sql_exec.drop_tables(cursor)
        cursor.execute("USE dbb;")
        sql_exec.create_tables(cursor)
    else:
        # fetching past data
        cursor.execute("use dbb;")
        fetcher("select username,cpu from USERDATA", avg_cpu_u, cursor)
        fetcher("select command,cpu from PROCESSDATA", avg_cpu_p, cursor)
        fetcher("select username,mem from USERDATA", avg_mem_u, cursor)
        fetcher("select command,mem from PROCESSDATA", avg_mem_p, cursor)
    long_delay = 90
    short_delay = 30  # no of seconds you want the whole thing to repeat
    interval_time = 5  # values get updated every 'interval_time' seconds
    total = int(long_delay // short_delay)
    tt = int(short_delay // interval_time) * total
    temp2 = total
    cursor.execute("use dbb;")
    cursor.execute("select noOfInstances from COUNT")
    no_of_instances = cursor.fetchall()
    if no_of_instances:
        # this means the program has been run before as well
        temp2 = int(no_of_instances[0][0]) + tt
        sql = """UPDATE `COUNT` SET noOfInstances = %s"""
        cursor.execute(sql, (temp2,))
    else:
        # first time, so we need to add the total number of times 'top' will be called
        sql = """INSERT INTO `COUNT`(noOfInstances)VALUES (%s)"""
        cursor.execute(sql, (tt,))
    dbb.commit()
    while total > 0:
        no_of_times = int(short_delay / interval_time)  # needs to repeat a certain 'no_of_times'
        temp = 1
        while no_of_times > 0:
            cpu_u, cpu_p, mem_u, mem_p = [{} for _ in range(4)]
            max_cpu, max_mem = [defaultdict(float) for _ in range(2)]
            """
            total CPU and MEM usage per user is held by the CPU and MEM dicts w
            we need to get the average for the number of times the top command is run

            calling op() will give a tuple, first and second elements being the CPU usage per user and per process
            third and fourth being MEM usage per user and process
            fifth and sixth being the unique users and processes
            """
            k = op(data_file)
            users = k[4]
            process = k[5]
            add_data(cpu_u, k[0])
            add_data(mem_u, k[1])
            add_data(cpu_p, k[2])
            add_data(mem_p, k[3])
            """
            need to write these values into a SQL dbb
            one instance of top is in the dicts, now to get the total/avg over time
            """
            # updating the past 3 values
            update_past(cpu_u, past_cpu_u)
            update_past(cpu_p, past_cpu_p)
            update_past(mem_u, past_mem_u)
            update_past(mem_p, past_mem_p)
            # getting the max value per user/process every time top is called
            update_max(cpu_u, max_cpu)
            update_max(cpu_p, max_cpu)
            update_max(mem_u, max_mem)
            update_max(mem_p, max_mem)
            # getting the average value of CPU/MEM usage per user/process
            update_avg(avg_cpu_u, cpu_u, temp, temp2)
            update_avg(avg_cpu_p, cpu_p, temp, temp2)
            update_avg(avg_mem_u, mem_u, temp, temp2)
            update_avg(avg_mem_p, mem_p, temp, temp2)
            # casting the default_dicts to dictionaries
            past_cpu_u = dict(past_cpu_u)
            past_cpu_p = dict(past_cpu_p)
            past_mem_u = dict(past_mem_u)
            past_mem_p = dict(past_mem_p)
            max_mem = dict(max_mem)
            max_cpu = dict(max_cpu)
            # inserting the obtained data into the MYSQL database
            sql = """INSERT INTO `USERDATA`(username,cpu,mem,past_1CPU,past_2CPU,past_3CPU,
            past_1MEM,past_2MEM,past_3MEM,maxCPU,maxMEM,time)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            sql2 = """INSERT INTO `PROCESSDATA`(command,cpu,mem,past_1CPU,past_2CPU,past_3CPU,
            past_1MEM,past_2MEM,past_3MEM,maxCpu,maxMEM,time)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor = dbb.cursor(buffered=True)
            if no_of_times == 1:
                # now SQL database contains only the final values at the end of the long delay
                for k in users:
                    ab = get_temp(past_cpu_u[k])
                    ab2 = get_temp(past_mem_u[k])
                    to_be_inserted = (
                        k, round(avg_cpu_u[k], 3), round(avg_mem_u[k], 3), ab[0], ab[1], ab[2], ab2[0], ab2[1], ab2[2],
                        round(max_cpu[k], 3), round(max_mem[k], 3), dt.now())
                    cursor.execute(sql, to_be_inserted)
                    dbb.commit()
                for k in process:
                    ab = get_temp(past_cpu_p[k])
                    ab2 = get_temp(past_mem_p[k])
                    to_be_inserted = (
                        k, round(avg_cpu_p[k], 3), round(avg_mem_p[k], 3), ab[0], ab[1], ab[2], ab2[0], ab2[1], ab2[2],
                        round(max_cpu[k], 3), round(max_mem[k], 3), dt.now())
                    cursor.execute(sql2, to_be_inserted)
                    dbb.commit()
            # the dicts have the current value, we just need to update max
            t.sleep(interval_time)
            no_of_times -= 1
            temp += 1
            cursor.close()
        history_update(hist_avg_cu, avg_cpu_u)
        history_update(hist_avg_cp, avg_cpu_p)
        history_update(hist_avg_mu, avg_mem_u)
        history_update(hist_avg_mp, avg_mem_p)
        history_update(histmax_c, max_cpu)
        history_update(histmax_m, max_mem)
        cursor = dbb.cursor(buffered=True)
        if total == 1:
            sql = """INSERT INTO `HISTORY_USER`(user,LD_UCPU1,LD_UCPU2,LD_UCPU3,LD_UMEM1,LD_UMEM2,LD_UMEM3,
            max1,max2,max3,max4,max5,max6,time) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for k in users:
                ab = get_temp(hist_avg_cu[k])
                ab2 = get_temp(hist_avg_mu[k])
                ab3 = get_temp(histmax_c[k])
                ab4 = get_temp(histmax_m[k])
                to_be_inserted = (
                    k, ab[0], ab[1], ab[2], ab2[0], ab2[1], ab2[2], ab3[0], ab3[1], ab3[2], ab4[0], ab4[1], ab4[2],
                    dt.now())
                cursor.execute(sql, to_be_inserted)
                dbb.commit()
                sql = """INSERT INTO `HISTORY_PROCESS`(cmd,LD_PCPU1,LD_PCPU2,LD_PCPU3,LD_PMEM1,LD_PMEM2,LD_PMEM3,
                max1,max2,max3,max4,max5,max6,time) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for k in process:
                ab = get_temp(hist_avg_cp[k])
                ab2 = get_temp(hist_avg_mp[k])
                ab3 = get_temp(histmax_c[k])
                ab4 = get_temp(histmax_m[k])
                to_be_inserted = (
                    k, ab[0], ab[1], ab[2], ab2[0], ab2[1], ab2[2], ab3[0], ab3[1], ab3[2], ab4[0], ab4[1], ab4[2],
                    dt.now())
                cursor.execute(sql, to_be_inserted)
                dbb.commit()
        total -= 1
        cursor.close()
    data_file.close()


if __name__ == "__main__":
    main()
