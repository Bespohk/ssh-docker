# -*- coding: utf-8 -*-
from collections import namedtuple

Header = namedtuple('Header', 'name start')
Container = namedtuple(
    'Container', 'container_id image command created status ports names')
