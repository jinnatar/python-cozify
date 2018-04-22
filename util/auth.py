#!/usr/bin/env python3
from cozify import cloud
from absl import flags, app

FLAGS = flags.FLAGS

flags.DEFINE_bool('debug', False, 'Enable debug output.')


def main(argv):
    del argv
    if FLAGS.debug:
        from cozify.test import debug
    cloud.authenticate()


if __name__ == "__main__":
    app.run(main)
