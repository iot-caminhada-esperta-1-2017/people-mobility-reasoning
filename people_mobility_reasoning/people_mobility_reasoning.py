
import os
import json
import logging
import logging.config


CONFIG_LOG_FILE = 'config/log.conf'



def setup_logging(
    default_path=CONFIG_LOG_FILE,
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration from a JSON file.

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)




if __name__ == '__main__':
    setup_logging()
    logging.info("Starting People Mobility Reasoning")
