#!/usr/bin/env python3
import time

import numpy
from absl import app, flags

from cozify import hub

FLAGS = flags.FLAGS

flags.DEFINE_string("device", None, "Device to operate on.")
flags.DEFINE_float("delay", 0.5, "Step length in seconds.")
flags.DEFINE_float("steps", 20, "Amount of steps to divide into.")
flags.DEFINE_bool("verify", False, "Verify if value went through as-is.")

green = "\u001b[32m"
yellow = "\u001b[33m"
red = "\u001b[31m"
reset = "\u001b[0m"


def main(argv):
    del argv
    previous = None
    for step in numpy.flipud(numpy.linspace(0.0, 1.0, num=FLAGS.steps)):
        hub.light_brightness(FLAGS.device, step)
        time.sleep(FLAGS.delay)
        read = "N/A"
        result = "?"
        if FLAGS.verify:
            devs = hub.devices()
            read = devs[FLAGS.device]["state"]["brightness"]
            if step == read:
                result = "✔"
                color = green
            else:
                result = "✖"
                if read == previous:
                    color = yellow
                else:
                    color = red
            previous = step
        print(
            "{3}[{2}] set: {0} vs. read: {1}{4}".format(
                step, read, result, color, reset
            )
        )


if __name__ == "__main__":
    flags.mark_flag_as_required("device")
    app.run(main)
