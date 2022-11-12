import logging

LOGGER: logging.Logger = None


def get_logger():
    if not LOGGER:
        init_basic_logger()
    return LOGGER


def debug(msg: str, **kwargs):
    get_logger().debug(msg, **kwargs)


def info(msg: str, **kwargs):
    get_logger().info(msg, **kwargs)


def warning(msg: str, **kwargs):
    get_logger().warning(msg, **kwargs)


def error(msg: str, **kwargs):
    get_logger().error(msg, **kwargs)


def init_basic_logger():
    global LOGGER
    LOGGER = logging.getLogger('xyaml_parser')
    LOGGER.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: [%(levelname)s]: %(message)s')
    console_handler.setFormatter(formatter)
    LOGGER.addHandler(console_handler)
