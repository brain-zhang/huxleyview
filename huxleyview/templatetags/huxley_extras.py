#!/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from django import template

register = template.Library()

def ftimestamp(value):
    if value:
        return datetime.strptime(value, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 'Nocase'

register.filter('ftimestamp', ftimestamp)
