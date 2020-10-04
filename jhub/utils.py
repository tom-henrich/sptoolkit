#!/usr/bin/env python3

"""Miscellaneous functions useful in at least two unrelated places.

"""
import logging
import subprocess
import pluggy

from jhub import hooks


def run_subprocess(cmd, *args, **kwargs):
    """Execute the CMD and provide feedback with log.

    If the command runs successfully, it is printed to the debug log. If
    it fails, it will print output to info logging.

    In SPToolkit, this sends successful output to the installer log,
    and failed output directly to the user's screen.

    Important:
      This is copied into initialize/initialize.py and must be an exact
      match to that one. Any changes made here need to be made there or
      vice-versa.

    """
    logger = logging.getLogger('jhub')
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          *args,
                          **kwargs)
    printable_command = ' '.join(cmd)
    if proc.returncode != 0:
        # Our process failed! Show output to the user
        logger.error('Ran {command} with exit code {code}'.format(
            command=printable_command, code=proc.returncode
        ))
        logger.error(proc.stdout.decode())
        raise subprocess.CalledProcessError(cmd=cmd,
                                            returncode=proc.returncode)
    else:
        # This goes into installer.log
        logger.debug('Ran {command} with exit code {code}'.format(
            command=printable_command, code=proc.returncode
        ))
        # This produces multi line log output
        # For now, prioritizing human readability over machine readability
        logger.debug(proc.stdout.decode())


def get_plugin_manager():
    """Return plugin manager instance.

    """
    # Set up plugin infrastructure
    pm = pluggy.PluginManager('jhub')
    pm.add_hookspecs(hooks)
    pm.load_setuptools_entrypoints('jhub')

    return pm
