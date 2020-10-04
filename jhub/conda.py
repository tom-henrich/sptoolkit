#!/usr/bin/env python3

"""Wraps the conda command line into a package.

"""
import os
import subprocess
import json
import hashlib
import contextlib
import tempfile
import requests
from distutils.version import LooseVersion as V

from jhub import utils


def sha256_file(fname):
    """Return the sha256(cryptographic hash) of a given filename.

    Note:
      Copied from https://stackoverflow.com/a/3431838

    """
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def check_miniconda_version(prefix, version):
    """Returns true if miniconda install with version exists at prefix.

    """
    try:
        installed_version = subprocess.check_output([
            os.path.join(prefix, 'bin', 'conda'),
            '-V'
        ], stderr=subprocess.STDOUT).decode().strip().split()[1]
        return V(installed_version) >= V(version)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Conda doesn't exist
        return False


@contextlib.contextmanager
def download_miniconda_installer(installer_url, sha256sum):
    """Context manager to download miniconda installer from a given URL.

    Note:
      This should be used as a contextmanager. It downloads miniconda
      installer based on version provided, verifies its sha256sum and
      provides the path to the `with` block to run.

    """
    _sha256_ex = 'sha256sum hash mismatch! Downloaded file corrupted.'
    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, 'wb') as f:
            f.write(requests.get(installer_url).content)
        # Return exception message if mismatched hashes
        if sha256_file(f.name) != sha256sum:
            raise Exception(_sha256_ex)

        yield f.name


def fix_permissions(prefix):
    """Fixes the permissions in the install prefix.

    This is run after each install command and checks:
      - everything is owned by current user:group
      - nothing is world-writeable

    """
    utils.run_subprocess(
        ["chown", "-R", "{}:{}".format(os.getuid(), os.getgid()), prefix]
    )
    utils.run_subprocess(["chmod", "-R", "o-w", prefix])


def install_miniconda(installer_path, prefix):
    """Install miniconda with installer at installer_path under prefix.

    """
    utils.run_subprocess([
        '/bin/bash',
        installer_path,
        '-u', '-b',
        '-p', prefix
    ])
    # Once installed, set permissions and ownership as some files have
    # the wrong ownership and permissions initially when run at root
    fix_permissions(prefix)


def ensure_conda_packages(prefix, packages):
    """Ensure packages (conda-forge) are installed in the conda prefix.

    """
    conda_executable = [os.path.join(prefix, 'bin', 'python'), '-m', 'conda']
    abspath = os.path.abspath(prefix)
    # Let subprocess errors propagate and explicitly do *not* capture
    # stderr, since not always JSON
    # FIX: raise different exception when using
    raw_output = subprocess.check_output(conda_executable + [
        'install',
        '-c', 'conda-forge',  # Make customizable if we ever need to
        '--json',
        '--prefix', abspath
    ] + packages).decode()
    # `conda install` outputs JSON lines for fetch updates, and an
    # undelimited output at the end. There is no reasonable way to
    # parse this outside of this kludge.

    # Sometimes the JSON messages start with a \x00 so lstrip removes
    filtered_output = '\n'.join([
        l for l in raw_output.split('\n') if not l.lstrip('\x00').startswith('{"fetch"')
    ])
    # conda messages also randomly throw \x00 in places so lstrip again.
    output = json.loads(filtered_output.lstrip('\x00'))
    if 'success' in output and output['success'] == True:
        return
    fix_permissions(prefix)


def ensure_pip_packages(prefix, packages):
    """Ensure pip packages are installed in the given conda prefix.

    """
    abspath = os.path.abspath(prefix)
    pip_executable = [os.path.join(abspath, 'bin', 'python'), '-m', 'pip']

    utils.run_subprocess(pip_executable + [
        'install',
        '--no-cache-dir',
    ] + packages)
    fix_permissions(prefix)


def ensure_pip_requirements(prefix, requirements_path):
    """Ensure pip packages from requirements installed in conda prefix.

    requirements_path can be a file or a URL.

    """
    abspath = os.path.abspath(prefix)
    pip_executable = [os.path.join(abspath, 'bin', 'python'), '-m', 'pip']

    utils.run_subprocess(pip_executable + [
        'install',
        '-r',
        requirements_path
    ])
    fix_permissions(prefix)
