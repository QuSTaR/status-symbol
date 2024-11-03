# This code is part of status_symbol.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Utilities for checking PyPi version"""

import sys
import warnings
import requests
from packaging.version import Version, parse
from packaging.requirements import Requirement

from .exceptions import StatusSymbolError


def pypi_version_check(package: str) -> tuple:
    """Check if there is a newer version of a package avaiable via PyPi that is
    compatible with the current version of Python

    Parameters:
        package: Package name.

    Returns:
        Boolean indicating if update avaiable and
        tuple of latest and installed versions

    Notes:
        If a ConnectionError is raised, then the latest version
        will automatically be set to match the installed version
        indicating no update.
    """
    try:
        installed_version = __import__(package.replace("-", "_")).__version__
    except ModuleNotFoundError:
        raise StatusSymbolError(f"Requested package '{package}' not installed.")

    current_python = ".".join(str(num) for num in sys.version_info[:3])
    package_found = True
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=3)
        if not response.ok:
            package_found = False
        else:
            latest_version = response.json()["info"]["version"]
            python_req = response.json()["info"].get("requires_python", "")
    except requests.exceptions.ConnectionError:
        latest_version = installed_version
    if not package_found:
        raise StatusSymbolError(
            f"Pypi check for '{package}' failed. Most likely package does not exist on pypi"
        )
    update_available = False
    if (
        Version(latest_version) > Version(installed_version)
        and parse(current_python) in Requirement("python" + python_req).specifier
    ):
        update_available = True
    return update_available, (latest_version, installed_version)


def emit_update_warning(package: str, versions: tuple) -> None:
    """Display a warning that an update is available

    Parameters:
        package: PyPi package name
        versions: Latest and current versions as strings
    """
    warnings.formatwarning = lambda msg, *args, **kwargs: f"{msg}\n"
    warnings.warn(
        f"A newer version of {package} ({versions[0]}) is available. {versions[1]} currently installed."
    )
