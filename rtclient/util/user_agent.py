# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import platform
#from importlib.metadata import version


def get_user_agent():
    package_version = "0.53"
    python_version = platform.python_version()
    return f"ms-rtclient/{package_version} Python/{python_version}"
