import logging
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

# set up logging to file - see previous section for more details
logging.basicConfig(level=LOGLEVEL,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOGGING_FILENAME,
                    filemode='w')

# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# Now, we can log to the root logger, or any other logger. First the root...
# logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your

# logger1 = logging.getLogger('myapp.area1')
# logger2 = logging.getLogger('myapp.area2')

# logger1.debug('Quick zephyrs blow, vexing daft Jim.')
# logger1.info('How quickly daft jumping zebras vex.')
# logger2.warning('Jail zesty vixen who grabbed pay from quack.')
# logger2.error('The five boxing wizards jump quickly.')
