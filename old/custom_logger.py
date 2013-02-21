import logging


logger = logging.getLogger("SpylightApp")
logger.addHandler(logging.FileHandler("spylight.log"))
logger.setLevel(logging.INFO)