import logging

logger = logging.getLogger("SpylightApp")
logger.addHandler(logging.FileHandler("spylight.log")) # Logs to a file
logger.addHandler(logging.StreamHandler()) # Logs to sys.stderr
logger.setLevel(logging.DEBUG)