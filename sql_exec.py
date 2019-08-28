"""
    contains the SQL functions we need to execute
"""


def create_tables(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `USERDATA` (id INT AUTO_INCREMENT NOT NULL,username VARCHAR(255),"
        "cpu REAL,mem REAL,past_1CPU VARCHAR(255),past_2CPU VARCHAR(255),past_3CPU VARCHAR(255),past_1MEM VARCHAR(255),"
        "past_2MEM VARCHAR(255),past_3MEM VARCHAR(255),maxCPU REAL,maxMEM REAL,time TIMESTAMP,primary key(id));")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `PROCESSDATA`(id INT AUTO_INCREMENT NOT NULL,command VARCHAR(255),"
        "cpu REAL,mem REAL,past_1CPU VARCHAR(255),past_2CPU VARCHAR(255),past_3CPU VARCHAR(255),past_1MEM VARCHAR(255),"
        "past_2MEM VARCHAR(255),past_3MEM VARCHAR(255),maxCPU REAL,maxMEM REAL,time TIMESTAMP,primary key(id));")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `HISTORY_USER` (user VARCHAR(255),LD_UCPU1 REAl,LD_UCPU2 REAL,LD_UCPU3 REAL,"
        "LD_UMEM1 REAL,LD_UMEM2 REAL,LD_UMEM3 REAL,max1 REAL,max2 REAL,max3 REAL,max4 REAL,max5 REAL,max6 REAL,"
        "time TIMESTAMP);")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `HISTORY_PROCESS` (cmd VARCHAR(255),LD_PCPU1 REAl,LD_PCPU2 REAL,LD_PCPU3 REAL,"
        "LD_PMEM1 REAL,LD_PMEM2 REAL,LD_PMEM3 REAL,max1 REAL,max2 REAL,max3 REAL,max4 REAL,max5 REAL,max6 REAL,"
        "time TIMESTAMP);")
    cursor.execute("CREATE TABLE IF NOT EXISTS `COUNT` (noOfInstances INT);")


def drop_tables(cursor):
    cursor.execute("DROP TABLE dbb.USERDATA;")
    cursor.execute("DROP TABLE dbb.PROCESSDATA;")
    cursor.execute("DROP TABLE dbb.HISTORY_USER;")
    cursor.execute("DROP TABLE dbb.HISTORY_PROCESS;")
    cursor.execute("DROP TABLE dbb.COUNT;")
