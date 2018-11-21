# -*- coding: utf-8 -*-
import os
import paramiko


def get_client(host: str, username: str, interactive: bool = False):
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_config = get_config()
    connection = {'hostname': host, 'username': username, 'port': 22}
    try:
        user_config = ssh_config.lookup(host)
        connection['hostname'] = user_config['hostname']
        connection['username'] = user_config['user']
        connection['key_filename'] = user_config['identityfile']
    except Exception:
        pass
    client.connect(**connection)
    kwargs = {}
    if interactive:
        kwargs['get_pty'] = True
    return client


def get_config():
    ssh_config = paramiko.SSHConfig()
    user_config_file = os.path.expanduser('~/.ssh/config')
    if os.path.exists(user_config_file):
        with open(user_config_file) as f:
            ssh_config.parse(f)
    return ssh_config


def get_hosts(ctx, args, incomplete):
    ssh_config = get_config()
    return [host for host
            in ssh_config.get_hostnames() if host.startswith(incomplete)]
