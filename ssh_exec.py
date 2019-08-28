"""
    for execution of top command after SSH connection is established
"""
import paramiko
import ssh_conn


def get_data():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ssh_conn.server, username=ssh_conn.name, password=ssh_conn.password)
    except Exception as error:
        print("Connection failed")
        print(error)
        exit()
    stdin, stdout, stderr = ssh.exec_command("top -bn 1")

    return ' '.join(stdout.readlines())
