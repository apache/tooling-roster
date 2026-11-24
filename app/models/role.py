# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""The roles a signed-in person can hold here."""

from __future__ import annotations

import enum


class Role(enum.StrEnum):
    SECRETARY = enum.auto()
    ADMIN = enum.auto()


EDITOR_ROLES: tuple[Role, ...] = (Role.SECRETARY,)
"""The roles that may see and change the roster: it holds personal data, so reading is theirs
alone. Admin is not among them - Tooling maintains the instance, and does not read the roster.
A stand-in until the roster's access rules are decided (apache/tooling-migration, target-architecture)."""
