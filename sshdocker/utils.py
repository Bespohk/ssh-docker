# -*- coding: utf-8 -*-
import click
from sshdocker import models, client


NL: str = '\n'


def read(stream):
    return stream.read().decode('utf-8')


def ps(client: client.Client, use_cache=False):
    errors: str = None
    if not client.cache['containers'] or not use_cache:
        stdin, stdout, stderr = client('docker ps')
        containers = parse_docker_ps(read(stdout))
        errors = read(stderr)
        client.cache['containers'] = containers
    else:
        containers = client.cache['containers']
    return containers, errors


def format_containers(containers, full=False, numbered=False):
    output = []
    for i, container in enumerate(containers):
        details: str = None
        one_based_index = i + 1
        one_based_index = click.style(f'{one_based_index}', bold=True)
        number = f'[{one_based_index}] ' if numbered else ''
        name = click.style(container.names, fg='yellow')
        if not full:
            details = f'{number}{name}'
        else:
            details = f'{number}{name} ({container.image}) uptime: {container.status}'
        output.append(details)
    return NL.join(output)


def parse_docker_ps(raw_output: str):
    output: list = []
    rows: list = raw_output.split('\n')
    index: int = 0
    headers: list = []
    for row in rows:
        if not row:
            continue
        if index == 0:
            row_headers: list = [r.strip() for r in row.split('  ') if r]
            for header in row_headers:
                headers.append(models.Header(header, row.index(header)))
        else:
            values = []
            for i, header in enumerate(headers):
                try:
                    next_index = headers[i+1].start
                except IndexError:
                    next_index = len(row)
                values.append(row[header.start:next_index].strip())
            output.append(models.Container(*values))
        index += 1
    return output
