#!/usr/bin/env python3
import subprocess
import sys
import click
from sshdocker import utils, client, ssh


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
    return utils.format_containers(containers, full=full), errors


def docker(client: client.Client, command='help'):
    """Access to the `docker` command directly.

    Usage:\tdocker [command]
    """
    stdin, stdout, stderr = client(
        f'docker {command}', get_pty=True)
    return utils.read(stdout), utils.read(stderr)


def select_container(client: client.Client):
    input_prompt = ['Which container would you like to connect to?']
    containers, _ = utils.ps(client, use_cache=True)
    input_prompt.append(utils.format_containers(containers, numbered=True))
    input_prompt.append('Default [1]: ')
    container = input(utils.NL.join(input_prompt))
    if not container:
        container = 0
    try:
        return containers[int(container) - 1].names
    except IndexError:
        click.secho(f'\nContainer {container} does not exist.\n', fg='red')
        return select_container(client)
    except ValueError:
        return container


def connect(client: client.Client, container: str = None, shell: str = '/bin/bash'):
    """Connect to a docker container via it's name.

    Usage:\tconnect [container name] [shell]

    [shell] will default to /bin/bash
    """
    if not container:
        container = select_container(client)
    ssh_command: str = f'ssh -t {client.hostname} docker exec -it {container} {shell}'
    click.echo()
    click.secho('Connecting to container with...', bold=True)
    click.secho(ssh_command, fg='yellow')
    subprocess.call(
        f'ssh -t {client.hostname} docker exec -it {container} {shell}', shell=True)
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


@click.command()
@click.argument('host', type=click.STRING, autocompletion=ssh.get_hosts)
@click.option('--username')
def main(host: str, username: str = None):
    c = client.Client(host, username=username, interactive=True)
    try:
        while True:
            user_input = input('> ')
            user_input: list = user_input.split(' ')
            command: str = user_input.pop(0)
            method = None
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
