#!/usr/bin/env python3
import time
from math import isclose

import pytest

from cozify import hub
from cozify.Error import APIError
from cozify.test import debug
from cozify.test.fixtures import live_hub, real_test_scenes, tmp_cloud, tmp_hub

# global timer delay for tests that change scene state
delay = 2


@pytest.mark.live
def test_hub_scene_filters(live_hub):
    scenes = live_hub.scenes(filters={"isOn": True, "category": "FACTORY"})
    assert len(scenes) == 1
    for scene_id, state in scenes.items():
        assert state["isOn"]


@pytest.mark.destructive
@pytest.mark.vcr
def test_hub_scene_toggle(live_hub, real_test_scenes):
    for i, s in real_test_scenes.items():
        expect = not s["isOn"]
        live_hub.scene_toggle(i)
        time.sleep(delay)
        scene = live_hub.scene(i)
        assert scene["isOn"] == expect
