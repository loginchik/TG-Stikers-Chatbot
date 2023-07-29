import logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

def setup_logger(name: str, filepath: str, level: int =logging.INFO):
    
    handler = logging.FileHandler(filepath)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

activity_logger = setup_logger(name='activity_logger', filepath='logs/activity.log')
db_logger = setup_logger(name='db_logger', filepath='logs/db.log')
