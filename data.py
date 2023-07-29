import json
import os 

from log import info_logger, error_logger
        
            
def load_json(path_to_file: str = os.path.relpath('data/sets.json')) -> dict:
    """Loads json file and loggs the process. 

    Args:
        path_to_file (str, optional): os.path to file. Defaults to os.path.relpath('data/sets.json').

    Returns:
        dict: loaded json data.
    """
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

    
def update_dict_value(key_name: str, new_value: int, dict_name: dict, force_create=True) -> None:
    """Updated the dict and loggs the process.

    Args:
        key_name (str): key in dict. If it doesn't exsist 
        new_value (int): new value to a key.
        dict_name (dict): dictionary to update.
        force_create (bool): sets, if non-existent key should be created. Defaults to True.

    Raises:
        TypeError: type of the data is not appropriate for the function to perform.
        KeyError: key is not in the dict and can't be created due to force_create=False. 
    """
    # Check if all input data is appropriate types. 
    if type(new_value) == int and type(key_name) == str and type(dict_name) == dict:
        # Change value, if key is located in the dictionary
        if key_name in dict_name.keys():
            # Gather old value
            old_value = dict_name[key_name]
            
            if old_value != new_value:
                    # Change value
                    dict_name[key_name] = new_value
                    info_logger.info(f'Value change {key_name} ({dict_name}): {old_value} -> {new_value}')
        else:
            # If key doesn't exist but is forced to create,
            if force_create:
                # created a new key-value pair 
                dict_name[key_name] = [new_value]
                info_logger.info(f'Value creation: {key_name} = {new_value}')
            # else the func raises the error
            else:
                error_logger.error('Force creation is not enabled, though it is required')
                raise KeyError(f'{key_name} does not exist in {dict_name}')
        
        dict_name[key_name] = new_value
    else:
        if type(new_value) != int:
            error_logger.error(f'Inappropriate type provided to update set ({new_value} is not integer)')
            raise TypeError(f"New value is expected to be int, not {type(new_value)}")
        if type(key_name) != str:
            error_logger.error(f'Inappropriate type provided to update set ({key_name} is not string)')
            raise TypeError(f"Set name is expected to be str, not {type(key_name)}")
        if type(dict_name) != dict:
            error_logger.error(f'Inappropriate type provided to update set ({dict_name} is not dict)')
            raise TypeError(f"Sets dict is expected to be str, not {type(dict_name)}")
  

def commit_json_change(dict_to_dump: dict, filepath: str) -> None:
    """Dumps dictionary to exsistend json file. Note that older data in .json will be lost.

    Args:
        dict_to_dump (dict): dictionary to save into json.
        filepath (str): path to .json file. 

    Raises:
        TypeError: file is not .json.
        FileNotFoundError: file is not found. 
    """
    
    if os.path.exists(filepath):
        # File extention has to be '.json'. 
        # Otherwise, it won't be possible to dump dict into it
        if os.path.splitext(filepath)[-1] == '.json': 
            # Open the target json file   
            json_file = open(file=filepath, mode='w') 
            # Save the data and log it
            json.dump(obj=dict_to_dump, fp=json_file)
            info_logger.info(f'JSON file at {filepath} commited')
            # Close the target file
            json_file.close()
        else:
            # Happens, if extention is not '.json'
            error_logger.error('Expected JSON file, but got something else')
            raise TypeError('Expected JSON file')
    else:
        # Happens, if json file doesn't yet exist. 
        # Prevents from duplicates of the db.
        error_logger.error('JSON file to commit does not exists')
        raise FileNotFoundError("Check if file exists")
    
