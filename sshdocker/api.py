#!/usr/bin/env python3
import os
import readline  # noqa
import socket
import subprocess
import sys
import click
from sshdocker import utils, client, ssh

DEFAULT_SHELL = os.getenv('SSH_DOCKER_SHELL', '/bin/bash')


def exit(client: client.Client):
    """Close the connection to the host.
    """
    client.close()
    sys.exit()


def list(client: client.Client, full=False, use_cache=False):
    """List all docker containers on the host.

    Usage:\tlist [full]

    [full] will return more information regarding the containers.
    """
    containers, errors = utils.ps(client)
    if 'docker: command not found' in errors:
        errors = 'Docker is not running on this host.'
    return utils.format_containers(containers, full=full), errors


def docker(client: client.Client, command='help', *args):
    """Access to the `docker` command directly.

    Usage:\tdocker [command]
    """
    args = ' '.join(args)
    stdin, stdout, stderr = client(
        f'docker {command} {args}', get_pty=True)
    return utils.read(stdout), utils.read(stderr)


def select_container(client: client.Client, shell: str):
    input_prompt = ['Which container would you like to connect to?']
    containers, _ = utils.ps(client, use_cache=True)
    if not containers:
        return None, None
    input_prompt.append(utils.format_containers(containers, numbered=True))
    input_prompt.append(f'Default [1 {shell}]: ')
    container = input(utils.NL.join(input_prompt))
    if not container:
        container = '1'
    try:
        container_shell = container.split(' ')
        container = container_shell[0]
        if len(container_shell) > 1:
            shell = container_shell[1]
        return containers[int(container) - 1].names, shell
    except IndexError:
        click.secho(f'Container {container} does not exist.', fg='red')
        return select_container(client, shell)
    except ValueError:
        return container, shell


def connect(
        client: client.Client,
        container: str = None,
        shell: str = DEFAULT_SHELL):
    """Connect to a docker container via it's name.

    Usage:\tconnect [container name] [shell]

    [shell] will default to /bin/bash
    """
    if not container:
        container, shell = select_container(client, shell)
        if not container:
            return None, 'There are no containers on this host.'
    ssh_command: str = f'ssh -t {client.hostname} docker exec -it {container} {shell}'
    click.echo()
    click.secho('Connecting to container with...', bold=True)
    click.secho(ssh_command, fg='yellow')
    subprocess.call(
        f'ssh -t {client.hostname} docker exec -it {container} {shell}',
        shell=True)
    sys.exit()


def help(client, command=None):
    methods = ['list', 'connect', 'docker', 'exit']
    output = ['Available commands:', '']
    if not command:
        for method in methods:
            actual_method = globals()[method]
            help_text = actual_method.__doc__.splitlines()[0]
            output.append(f'{actual_method.__name__}\t{help_text}')
        output.append('')
        output.append('For more information type: help [topic]')
        output.append('')
    else:
        if command not in methods:
            return help(client)
        output = [line.strip()
                  for line in globals()[command].__doc__.splitlines()]
    return utils.NL.join(output), None


def similar_hosts(search: str):
    similar = ssh.get_hosts(None, None, incomplete=search, contains=True)
    if similar:
        similar_count = len(similar)
        click.echo(
            f'Found {similar_count} similar hosts, did you mean one of these?')
        input_prompt = []
        for host_index, hostname in enumerate(similar):
            one_based_index = host_index + 1
            styled_index = click.style(f'{one_based_index}', bold=True)
            styled_hostname = click.style(hostname, fg='yellow')
            input_prompt.append(f'[{styled_index}] {styled_hostname}')
        input_prompt.append('Default [1] or enter a new hostname: ')
        host_index = input(utils.NL.join(input_prompt))
        if not host_index:
            host_index = '1'
        try:
            host = similar[int(host_index) - 1]
            click.echo()
            click.secho(f'Connecting to host {host}...', bold=True)
            return host
        except IndexError:
            return similar_hosts(search)
        except Exception:
            return host_index
    return None


def create_client(host: str, username: str = None):
    try:
        return client.Client(host, username=username, interactive=True)
    except socket.gaierror:
        click.secho(f'Unable to connect to host "{host}".', fg='red', err=True)
        return None


def create_connection(host, username: str = None):
    c = create_client(host, username=username)
    if not c:
        host = similar_hosts(host)
        if host:
            c = create_connection(host, username=username)
    return c


@click.command()
@click.argument('host', type=click.STRING, autocompletion=ssh.get_hosts)
@click.option('--container', help='The container to connect to.')
@click.option('--username', help='The username required on the host.')
def main(host: str, container: str = None, username: str = None):
    c = create_connection(host, username=username)
    if not c:
        sys.exit(1)
    try:
        while True:
            if container:
                user_input = ['connect', container]
                container = None
            else:
                user_input = input('> ')
                user_input: list = user_input.split(' ')
            method = None
            command: str = user_input.pop(0)
            errors = None
            output = None
            try:
                method = globals()[command]
            except KeyError:
                click.secho(
                    f'Command "{command}" does not exist.', fg='red', err=True)
                output, _ = help(c)
            if method:
                output, errors = method(c, *user_input)
            if output:
                click.echo(output)
            if errors:
                click.secho(errors, fg='red', err=True)
    except KeyboardInterrupt:
        exit(c)


if __name__ == '__main__':
    main()
