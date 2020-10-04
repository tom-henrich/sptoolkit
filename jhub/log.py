#!/usr/bin/env python3

"""Setup jhub logging.

"""
import os
import logging

from .config import INSTALL_PREFIX


def init_logging():
    """Setup default jhub logger.

    """
    logger = logging.getLogger("jhub")
    os.makedirs(INSTALL_PREFIX, exist_ok=True)
    file_logger = logging.FileHandler(os.path.join(INSTALL_PREFIX,
                                                   "installer.log"))
    file_logger.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(file_logger)

    stderr_logger = logging.StreamHandler()
    stderr_logger.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stderr_logger)
    logger.setLevel(logging.INFO)
