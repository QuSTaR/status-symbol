# status-symbol
A generic status check for pypi versioning

## Installation

```bash
pip install status-symbol
```

## Usage

The most basic usage is simply:

```python

import status_symbol as ss

update_available, versions = ss.pypi_version_check('PACKAGE_NAME')
if update_available:
    ss.emit_update_warning('PACKAGE_NAME', versions)
```

## Disabling update warnings

It is possible to disable update checks for packages like so:

```python

ss.configuration.disable_version_check('PACKAGE_NAME')
```

One can check for disabled packages as well:

```python

ss.configuration.is_disabled('PACKAGE_NAME')
```

So doing a check and enitting as warning looks like:

```python

disabled = ss.configuration.is_disabled('PACKAGE_NAME')
if not disabled:
    update_available, versions = ss.pypi_version_check('PACKAGE_NAME')
    ss.emit_update_warning('PACKAGE_NAME', versions) if update_available else None
```
