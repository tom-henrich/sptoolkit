#!/usr/bin/env python3

"""Initializes the SPToolkit JupyterHub server on Ubuntu.

Triggers a base set up to kick-start the hub.installer.

This script is run as:

    curl <script-url> | sudo python3 -

Important:
  - Everything that runs in the script must work in Python 3.6 which
  aligns with Ubuntu 18.04+.
  - The script shoukd be parsed with Python 3.4 for Ubuntu 14.04+ error
  message on exit.
  - Use stdlib modules only.

"""
import os
import sys
import shutil
import logging
import subprocess
import urllib.request
import multiprocessing
from http.server import SimpleHTTPRequestHandler, HTTPServer

from initialize.progress import PROGRESS_HTML, FAVICON_URL, JHUB_URL

logger = logging.getLogger(__name__)


def get_os_release_variable(key):
    """Return the string value for key from /etc/os-release.

    /etc/os-release is a bash file so bash should be used to parse it.
    If not key is found, returns an empty string.

    """
    return subprocess.check_output([
        '/bin/bash', '-c',
        "source /etc/os-release && echo ${{{key}}}".format(key=key)
    ]).decode().strip()


def run_subprocess(cmd, *args, **kwargs):
    """Execute the CMD and provide feedback with log.

    If the command runs successfully, it is printed to the debug log. If
    it fails, it will print output to info logging.

    In SPToolkit, this sends successful output to the installer log,
    and failed output directly to the user's screen.

    Important:
      This is copied into jhub/utils.py and must be an exact
      match to that one. Any changes made here need to be made there or
      vice-versa.

    """
    logger = logging.getLogger('jhub')
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, *args, **kwargs)
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
        # For now, prioritizing human readability over machine readability.
        logger.debug(proc.stdout.decode())


def validate_host():
    """Check if the system running code can run JupyterHub(linux).

    Important:
      This app currently only supports Ubuntu 18.04+ but in the future,
      should be updated to support other systems. For more information,
      launching in a local development environment, see the guide this
      code was derived from at:
        http://tljh.jupyter.org/en/latest/contributing/dev-setup.html

    """
    distro = get_os_release_variable('ID')
    version = float(get_os_release_variable('VERSION_ID'))
    if distro != 'ubuntu':
        print('SPT JupyterHub currently supports Ubuntu Linux only')
        sys.exit(1)
    elif float(version) < 18.04:
        print('SPT JupyterHub requires Ubuntu 18.04 or higher')
        sys.exit(1)

    if sys.version_info < (3, 5):
        print("initialize.py must be run with at least Python 3.5")
        sys.exit(1)

    if not (shutil.which('systemd') and shutil.which('systemctl')):
        print("Systemd is required to run SPT")
        # Only fail running inside docker if systemd isn't present
        if os.path.exists('/.dockerenv'):
            print("systemd MUST be included to run hub in a docker container.")
            print("Production should not be run through docker containers.")
        sys.exit(1)


class LoaderPageRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/logs":
            with open("/opt/jhub/installer.log", "r") as log_file:
                logs = log_file.read()

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(logs.encode('utf-8'))
        elif self.path == "/index.html":
            self.path = "/var/run/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == "/favicon.ico":
            self.path = "/var/run/favicon.ico"
            return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == "/":
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
        else:
            SimpleHTTPRequestHandler.send_error(self, code=403)


def serve_forever(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    flags = sys.argv[1:]
    temp_page_flag = "--show-progress-page"

    # Check for flag in the argv list. This doesn't use argparse because
    # it's the only argument that's meant for the intialize script.
    # All the other flags will be passed to and parsed by the installer.
    if temp_page_flag in flags:
        with open("/var/run/index.html", "w+") as f:
            f.write(PROGRESS_HTML)  # was html

        urllib.request.urlretrieve(FAVICON_URL, "/var/run/favicon.ico")

        # If initialize is upgrading hub, raises already in use error
        try:
            loading_page_server = HTTPServer(("", 80),
                                             LoaderPageRequestHandler)
            p = multiprocessing.Process(target=serve_forever,
                                        args=(loading_page_server,))
            # Serves the progress page while hub is being built
            p.start()

            # Remove flag from the args list (not relevant anymore)
            flags.remove("--show-progress-page")

            # Pass the server's pid as a flag to the installer
            pid_flag = "--progress-page-server-pid"
            flags.extend([pid_flag, str(p.pid)])
        except OSError:
            # Only serve the loading page when installing hub
            pass

    validate_host()
    install_prefix = os.environ.get('JHUB_INSTALL_PREFIX', '/opt/jhub')
    hub_prefix = os.path.join(install_prefix, 'hub')

    # Set up logging to print to a file and to stderr
    os.makedirs(install_prefix, exist_ok=True)
    file_logger_path = os.path.join(install_prefix, 'installer.log')
    file_logger = logging.FileHandler(file_logger_path)
    # installer.log should be readable only by root
    os.chmod(file_logger_path, 0o500)

    file_logger.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    file_logger.setLevel(logging.DEBUG)
    logger.addHandler(file_logger)

    stderr_logger = logging.StreamHandler()
    stderr_logger.setFormatter(logging.Formatter('%(message)s'))
    stderr_logger.setLevel(logging.INFO)
    logger.addHandler(stderr_logger)
    logger.setLevel(logging.DEBUG)

    logger.info('Checking if SPT jhub is already installed...')
    if os.path.exists(os.path.join(hub_prefix, 'bin', 'python3')):
        logger.info('SPT jhub is already installed, so upgrading...')
        initial_setup = False
    else:
        logger.info('Setting up hub virtual environment...')
        initial_setup = True
        # Install software-properties-common, so we can get
        # add-apt-repository which ensures the universe repository is
        # enabled. This repository is where the python3-pip package
        # lives. In some very minimal base VM images, it looks like the
        # universe repository is disabled by default, causing initialize
        # to fail.
        run_subprocess(['apt-get', 'update', '--yes'])
        run_subprocess(['apt-get', 'install', '--yes',
                        'software-properties-common'])
        run_subprocess(['add-apt-repository', 'universe'])
        run_subprocess(['apt-get', 'update', '--yes'])
        run_subprocess(['apt-get', 'install', '--yes',
                        'python3', 'python3-venv', 'python3-pip', 'git'])
        logger.info('Python and Virtual Environment installed Successfully!')
        os.makedirs(hub_prefix, exist_ok=True)
        run_subprocess(['python3', '-m', 'venv', hub_prefix])
        logger.info('The hub (JupyterHub) virtual environment created!')

    if initial_setup:
        logger.info('Setting up the jhub installer...')
    else:
        logger.info('Upgrading the jhub installer...')
    # These env vars are set in jhub/config
    pip_flags = ['--upgrade']
    if os.environ.get('JHUB_INITIALIZE_DEV', 'no') == 'yes':
        pip_flags.append('--editable')
    # Protocol written git+https to clarify that it should use Git over HTTPS
    jhub_repo_path = os.environ.get('JHUB_INITIALIZE_PIP_SPEC', JHUB_URL)

    # Upgrade pip
    run_subprocess([
        os.path.join(hub_prefix, 'bin', 'pip'),
        'install',
        '--upgrade',
        'pip==20.0.*'
    ])
    logger.info('pip Upgraded Successfully!')

    run_subprocess([
        os.path.join(hub_prefix, 'bin', 'pip'),
        'install'
    ] + pip_flags + [jhub_repo_path])
    logger.info('Jhub package setup succesfully!')

    logger.info('Starting jhub installer...')
    os.execv(
        os.path.join(hub_prefix, 'bin', 'python3'),
        [
            os.path.join(hub_prefix, 'bin', 'python3'),
            '-m',
            'jhub.installer',
        ] + flags
    )


if __name__ == '__main__':
    main()
