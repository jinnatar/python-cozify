#!/usr/bin/env python3
import pytest, time

from math import isclose

from cozify import hub
from cozify.test import debug
from cozify.test.fixtures import live_hub, tmp_hub, tmp_cloud, real_test_scenes
from cozify.Error import APIError

# global timer delay for tests that change scene state
delay = 2


@pytest.mark.live
def test_hub_scene_filters(live_hub):
    scenes = live_hub.scenes(filters={'isOn': True, 'category': 'FACTORY'})
    assert len(scenes) == 1
    for scene_id, state in scenes.items():
        assert state['isOn']


@pytest.mark.destructive
@pytest.mark.vcr
def test_hub_scene_toggle(live_hub, real_test_scenes):
    for i, s in real_test_scenes.items():
        expect = not s['isOn']
        live_hub.scene_toggle(i)
        time.sleep(delay)
        scene = live_hub.scene(i)
        assert scene['isOn'] == expect
