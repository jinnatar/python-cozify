#!/usr/bin/env python3
import time
from absl import logging, app, flags
from cozify import hub
import pprint, sys

from cozify.test import debug

FLAGS = flags.FLAGS
flags.DEFINE_string('device', None,
                    'Device ID of a controllable socket into which the Lightify device is plugged')
flags.DEFINE_float('ontime', 5, 'Time to keep the light on', lower_bound=0.0)
flags.DEFINE_float('offtime', 5, 'Time to keep the light off', lower_bound=0.0)
flags.DEFINE_integer('iterations', 5, 'Number of cycles to perform', lower_bound=1)
flags.DEFINE_integer('initial_delay', 5, 'Stablize time before starting cycles', lower_bound=1)

flags.mark_flag_as_required('device')


def init(device):
    hub.ping()
    hub.device_off(device)
    time.sleep(FLAGS.initial_delay)


def cycle(device):
    hub.device_on(device)
    time.sleep(FLAGS.ontime)
    hub.device_off(device)
    time.sleep(FLAGS.offtime)


def main(argv):
    device = FLAGS.device
    init(device)
    for i in range(0, FLAGS.iterations):
        cycle(device)
    hub.device_on(device)


if __name__ == "__main__":
    app.run(main)
