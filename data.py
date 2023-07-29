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
    
def update_set(set_name: str, new_value: int, sets_dict: dict):
    if type(new_value) == int and type(set_name) == str and type(sets_dict) == dict:
        sets_dict[set_name] = new_value
    else:
        if type(new_value) != int:
            error_logger.log(f'Inappropriate type provided to update set ({new_value} is not integer)')
            raise TypeError(f"New value is expected to be int, not {type(new_value)}")
        if type(set_name) != str:
            error_logger.log(f'Inappropriate type provided to update set ({set_name} is not string)')
            raise TypeError(f"Set name is expected to be str, not {type(set_name)}")
        if type(sets_dict) != dict:
            error_logger.log(f'Inappropriate type provided to update set ({sets_dict} is not dict)')
            raise TypeError(f"Sets dict is expected to be str, not {type(sets_dict)}")
    
    
sets = load_extisting_sets()
update_set('someset', new_value='0', sets_dict=sets)
