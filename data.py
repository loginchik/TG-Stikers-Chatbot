import json
import os 

from log import info_logger, error_logger
        
            
def load_extisting_sets(path_to_file: str = os.path.relpath('data/sets.json')) -> dict | None:
    try:
        # Open the source file in reading mode 
        source_file = open(file=path_to_file, mode='r')
        info_logger.info(f'{path_to_file} is opened')
        try: 
            # Load json data into python dict 
            sets = json.load(source_file)
            info_logger.info(f'Loaded {path_to_file}')
            
            # Close the connection to source file 
            source_file.close()
            info_logger.info(f'{path_to_file} is closed')
            
            # Return gathered info
            return sets
        # In case of decoder error 
        # Error message is logged, None is returned by function 
        except json.decoder.JSONDecodeError as e:
            error_logger.error(f'Decode of {path_to_file} error')
            return None
    # In case file is not found, error is logged, None is returned as a restult of function
    except FileNotFoundError:
        error_logger.error(f'{path_to_file} is not found')
        return None
    

print(load_extisting_sets())
