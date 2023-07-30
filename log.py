import logging
import os

formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

def setup_logger(name: str, filepath: os.PathLike, level: int | str = logging.INFO):
    """Returns logger that is setup to use. 

    Args:
        name (str): logger name. 
        filepath (os.Pathlike): path to file to write logs. 
        level (int | str, optional): level of logging. Defaults to logging.INFO.

    Returns:
        _type_: _description_
    """
    # Setup handler
    handler = logging.FileHandler(filepath)
    handler.setFormatter(formatter)
    # Setup logger 
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Add handler to logger 
    logger.addHandler(handler)
    # Return the logger 
    return logger

# Loggers to use
activity_logger = setup_logger(name='activity_logger', filepath='logs/activity.log')
db_logger = setup_logger(name='db_logger', filepath='logs/db.log')
