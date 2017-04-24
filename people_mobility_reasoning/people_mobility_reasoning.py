
import os
import json
import logging
import logging.config

from raise2_self_register.raise2_self_register import Raise2SelfRegisterUglyWay
from raise2_self_register.raise2_self_register import Raise2SelfRegister
from load_dict_from_file.load_dict_from_file import get_dict_from_file



CONFIG_LOG_FILE = 'config/log.conf'
CONFIG_RAISE2_FILE = 'config/raise2.conf'

# TODO: put it all into a dictionary with the aplication configuration
APP_NAME = 'PeopleMobilityReasoning'



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

    raise2_config = get_dict_from_file(CONFIG_RAISE2_FILE)

    # logging.debug("raise2_config:")
    # logging.debug(raise2_config)
    # ugly_self_register = Raise2SelfRegisterUglyWay(raise2_config)
    # ugly_self_register.self_register()

    logging.info("-----------------------------")
    # logging.debug("raise2_config:")
    # logging.debug(raise2_config)
    self_register = Raise2SelfRegister(raise2_config)
    self_register.self_register()
