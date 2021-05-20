import json

def queries():
    try:
        with open('queries/queries.json') as f:
            QUERIES = json.load(f)
            return QUERIES
    except FileNotFoundError:
        print('configuration file not found')