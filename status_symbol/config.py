# This code is part of status_symbol.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Utils for reading a user preference config files."""

import os
import configparser

from .exceptions import StatusSymbolError


if os.getenv('STATUSSYMBOL_CI', False):
    _FILE = "status_symbol_testing.conf"
else:
    _FILE = "status_symbol.conf"

FILENAME = os.path.join(os.path.expanduser("~"), ".status_symbol", _FILE)


class StatusSymbolPackages(dict):
    def __repr__(self):
        # Find max key length
        max_length = 0
        for key in self:
            max_length = max(max_length, len(key))

        indent = 1
        out = "Disabled packages\n"
        out += "=" * 40 + "\n"
        for key, val in self.items():
            out += (" " * indent + key + " " * (max_length - len(key) + 5) + (f"{val}") + "\n")
        return out


class Configuration:
    """Class containing configuation information"""

    def __init__(self):
        """Create a Configuration"""
        self.filename = FILENAME
        self.package_list = {}
        self.parser = configparser.ConfigParser()

        if not os.path.isfile(FILENAME):
            self.parser.read(FILENAME)
            if "DISABLE" not in self.parser.sections():
                self.parser.add_section("disabled")
            os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
            try:
                with open(FILENAME, "w") as cfgfile:
                    self.parser.write(cfgfile)
            except (OSError, PermissionError):
                pass
        self.read_configuration()

    def read_configuration(self):
        """Read configuration information from file"""
        if not os.path.isfile(FILENAME):
            return {}
        self.parser.read(self.filename)
        if "disabled" in self.parser.sections():
            self.package_list = dict(self.parser.items("disabled"))
        return StatusSymbolPackages(self.package_list)

    def is_disabled(self, package_name: str):
        """Is version check disabled for a package?
        Parameters:
            packaged_name (str): Requested package
        Returns:
            bool: True if version check is disabled
        """
        val = self.package_list.get(package_name, "False")
        return True if val == "True" else False

    def disable_version_check(self, package_name: str):
        """Disable version check for a package

        Parameters:
            packaged_name (str): Requested package
        Returns:
            bool: Was operation successful
        """
        if not os.path.isfile(FILENAME):
            return False
        self.parser.read(self.filename)
        if "disabled" in self.parser.sections():
            present = self.parser.get("disabled", package_name, fallback=None)
            if present == "True":
                return True
        if "disabled" not in self.parser.sections():
            self.parser.add_section("disabled")

        self.parser.set("disabled", package_name, str(True))

        try:
            with open(FILENAME, "w") as cfgfile:
                self.parser.write(cfgfile)
        except (OSError, PermissionError) as ex:
            raise StatusSymbolError(
                f"Unable to write the config file {FILENAME}. Error: '{str(ex)}'"
            )
        self.read_configuration()
        return True

    def enable_version_check(self, package_name: str):
        """Enable version check for a package

        Parameters:
            packaged_name (str): Requested package
        Returns:
            bool: Was operation successful
        """
        if not os.path.isfile(FILENAME):
            return False
        self.parser.read(self.filename)
        if "disabled" in self.parser.sections():
            present = self.parser.get("disabled", package_name, fallback=None)
            if present == "True":
                self.parser.set("disabled", package_name, str(False))
            else:
                return True
        try:
            with open(FILENAME, "w") as cfgfile:
                self.parser.write(cfgfile)
        except (OSError, PermissionError) as ex:
            raise StatusSymbolError(
                f"Unable to write the config file {FILENAME}. Error: '{str(ex)}'"
            )
        self.read_configuration()
        return True
