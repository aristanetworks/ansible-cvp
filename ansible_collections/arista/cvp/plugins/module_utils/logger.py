import logging
from logging.handlers import RotatingFileHandler
import os

# Get Logging level from Environment variable / Default INFO
LOGGING_LEVEL = os.getenv('ANSIBLE_CVP_LOG_LEVEL', 'info')
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
LOGLEVEL = LEVELS.get(LOGGING_LEVEL, logging.NOTSET)

# Get filename to write logs / default /temp/arista.cvp.debug.log
LOGGING_FILENAME = os.getenv(
    'ANSIBLE_CVP_LOG_FILE', '/temp/arista.cvp.debug.log')

# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# set up ROOT handler to use logging with file rotation.
handler = logging.handlers.RotatingFileHandler(
    LOGGING_FILENAME, maxBytes=1000000, backupCount=5)
handler.setFormatter(formatter)
handler.setLevel(LOGLEVEL)
# Unset default logging level for root handler
logging.getLogger('').setLevel(logging.NOTSET)
logging.getLogger('').addHandler(handler)
