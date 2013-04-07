#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Default values for configuration options (strings only!)
default_config = {
    'map_file': 'test.hfm',
    'server_host': '0.0.0.0',
    'server_port': '12321',
    'send_state_interval': '3.0',
}

# Types of configuration options
option_types = {
    'map_file': str,
    'server_host': str,
    'server_port': int,
    'send_state_interval': float,
}
