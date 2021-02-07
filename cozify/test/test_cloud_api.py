#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from cozify import cloud_api
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import AuthenticationError, APIError, ConnectionError

from mbtest.imposters import Imposter, Predicate, Stub, Response


@pytest.mark.mbtest
def test_cloud_api_mock_lan_ip(mock_server):
    imposter = Imposter(Stub(Predicate(path="/hub/lan_ip"), Response(body='[ "127.0.0.1" ]')))
    with mock_server(imposter):
        assert cloud_api.lan_ip(base=imposter.url)


@pytest.mark.mbtest
def test_cloud_api_timeout(mock_server):
    imposter = Imposter(
        Stub(Predicate(path="/hub/lan_ip"), Response(body='[ "127.0.0.1" ]', wait=6000)))
    with pytest.raises(ConnectionError) as e_info:
        with mock_server(imposter):
            cloud_api.lan_ip(base=imposter.url)


@pytest.mark.mbtest
def test_cloud_api_emaillogin(mock_server, tmp_cloud):
    imposter = Imposter(Stub(Predicate(path="/user/emaillogin"), Response(body=tmp_cloud.token)))
    with mock_server(imposter):
        token = cloud_api.emaillogin(email=tmp_cloud.email, otp='42', base=imposter.url)
        assert isinstance(token, str)
