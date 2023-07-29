import json
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

with open('data/sets.json') as sets_file:
    try: 
        sets = json.load(sets_file)
        logging.info('Loaded json')
    except json.decoder.JSONDecodeError:
        logging.error('JSON sets load error')
    
