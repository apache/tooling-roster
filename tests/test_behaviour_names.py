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

"""The harness reads the variables that the kit's `scripts/ci/behaviour.py` sets, by the same names.

A name that differs is not an error anywhere: the recording writes no map of what ran, and every later
comparison records everything instead of what a change reaches."""

import pathlib

import pytest

from tests.behaviour import executed, store

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "ci" / "behaviour.py"


@pytest.mark.parametrize("name", [store.OUT_ENV, executed.ENV, executed.SELECT_ENV])
def test_the_harness_reads_what_the_script_sets(name: str) -> None:
    assert f'"{name}"' in _SCRIPT.read_text()
