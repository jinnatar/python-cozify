#!/usr/bin/env python3

import pytest

import os, tempfile
from absl import logging

from cozify import http

from cozify.test import debug, state_verify
from cozify.test.fixtures import tmp_config, empty_config, live_config, tmp_hub, tmp_cloud, ready_kwargs, live_hub, live_cloud


@pytest.mark.logic
def test_http_get(ready_kwargs):
    assert http.get('http://headers.jsontest.com', token='foo', **ready_kwargs)
