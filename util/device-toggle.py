#!/usr/bin/env python3
from absl import app, flags

from cozify import hub
from cozify.test import debug

FLAGS = flags.FLAGS

flags.DEFINE_string("device", None, "Device to operate on.")


def main(argv):
    del argv
    hub.device_toggle(FLAGS.device)


if __name__ == "__main__":
    flags.mark_flag_as_required("device")
    app.run(main)
