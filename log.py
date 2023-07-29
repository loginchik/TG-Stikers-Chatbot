import logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

def setup_logger(name: str, filepath: str, level: int =logging.INFO):
    
    handler = logging.FileHandler(filepath)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger


info_logger = setup_logger(name='info_logger', filepath='logs/info.log')
error_logger = setup_logger(name='error_logger', filepath='logs/error.log', level=logging.ERROR)
    