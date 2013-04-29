#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Default values for configuration options (strings only!)
default_config = {
    'map_file': 'test.hfm',
    'server_host': '0.0.0.0',
    'server_port': '9999',
    'step_state_interval': '0.05',
    'send_state_interval': '0.1',
    'handle_timeout': '10',
}

# Types of configuration options
option_types = {
    'map_file': str,
    'server_host': str,
    'server_port': int,
    'step_state_interval': float,
    'send_state_interval': float,
    'handle_timeout': float,
}
