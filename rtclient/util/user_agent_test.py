# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import re
from .user_agent import get_user_agent

def test_user_agent_schema():
    user_agent = get_user_agent()
    regex = re.compile(r"ms-rtclient/\d+\.\d+ Python/\d+\.\d+\.\d+")
    assert regex.match(user_agent) is not None
