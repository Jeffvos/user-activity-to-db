import json

def config():
    try:
        with open('config/appconfig.json') as f:
            APPCONFIG = json.load(f)
            return APPCONFIG
    except FileNotFoundError:
        print('configuration file not found')