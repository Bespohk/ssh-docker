# -*- coding: utf-8 -*-
import paramiko
from sshdocker import ssh


class Client(object):
    hostname: str = None
    paramiko_client: paramiko.SSHClient = None
    cache: dict = None

    def __init__(self, hostname, username: str, interactive: bool = False):
        self.cache = {
            'containers': []
        }
        self.paramiko_client = ssh.get_client(
            hostname, username=username, interactive=True)
        self.hostname = hostname

    def __call__(self, *args, **kwargs):
        return self.paramiko_client.exec_command(*args, **kwargs)
