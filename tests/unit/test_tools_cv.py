#!/usr/bin/python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable=dangerous-default-value
# flake8: noqa: W503
# flake8: noqa: W1202

from __future__ import absolute_import, division, print_function
from ansible_collections.arista.cvp.plugins.module_utils.tools_cv import cv_connect
import pytest
from unittest import mock

from tests.lib.mock_ansible import (
    get_ansible_module,
    get_ansible_connection,
    AnsibleFailJson,
)
from contextlib import contextmanager
from cvprac.cvp_client_errors import CvpLoginError

# pytest - -html = report.html - -self-contained-html - -cov = . --cov-report = html - -color yes containerInputs.py - v

# ---------------------------------------------------------------------------- #
#   FIXTURES
# ---------------------------------------------------------------------------- #


@pytest.fixture
def module():
    module = get_ansible_module()
    module._socket_path = __file__
    return module


@pytest.fixture
def connection(request):
    def get_option(key):
        return request.param[key]

    connection = get_ansible_connection()
    connection.get_option = get_option
    return connection


def module_values(
    host="42.42.42.42",
    port=443,
    validate_certs=True,
    remote_user="cvpadmin",
    password="ansible",
    persistent_command_timeout=30,
    persistent_connect_timeout=30,
):
    """
    Default dict to be used to fake module parameters
    """
    return {
        "host": host,
        "port": port,
        "validate_certs": validate_certs,
        "remote_user": remote_user,
        "password": password,
        "persistent_command_timeout": persistent_command_timeout,
        "persistent_connect_timeout": persistent_connect_timeout,
    }


# As per https://docs.pytest.org/en/6.2.x/example/parametrize.html#parametrizing-conditional-raising
@contextmanager
def does_not_raise():
    yield


# ---------------------------------------------------------------------------- #
#   PYTEST
# ---------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "connection, connect_side_effect, expectation",
    [
        pytest.param(module_values(), None, does_not_raise(), id="Succes"),
        pytest.param(
            module_values(password={"__ansible_vault": "DUMMY VAULT"}),
            None,
            pytest.raises(NotImplementedError),
            id="Vault variable undecrypted",
        ),
        pytest.param(
            module_values(),
            CvpLoginError("Test Exception"),
            pytest.raises(AnsibleFailJson),
            id="Failed Connection",
        ),
        pytest.param(
            module_values(password=1234),
            None,
            does_not_raise(),
            id="Password not a string not raising",
        ),
    ],
    indirect=["connection"],
)
def test_cv_connect(module, connection, connect_side_effect, expectation):
    """
    this test is using indirect parametrization to pass arguments to the connection
    fixture.
    Note that implicit fixture parametrization is also possible but it then looks like
    a lot of magic
    https://stackoverflow.com/questions/18011902/pass-a-parameter-to-a-fixture-function
    hmmm
    """
    # Patch the Connection class to return the connection fixture
    with mock.patch(
        "ansible_collections.arista.cvp.plugins.module_utils.tools_cv.Connection",
        return_value=connection,
    ), mock.patch(
        "ansible_collections.arista.cvp.plugins.module_utils.tools_cv.CvpClient.connect",
        side_effect=connect_side_effect,
    ):
        with expectation:
            cv_connect(module)
