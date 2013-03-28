from ConfigParser import SafeConfigParser

_CONFIG_FILE = 'client/spylightclient.ini'


def load_config():
    global config
    config.read(_CONFIG_FILE)
    print config.sections()

config = SafeConfigParser()

if not config.sections():
    load_config()
