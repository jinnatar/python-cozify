#!/usr/bin/env python3
import tempfile, os
from cozify import config, cloud, hub
from absl import flags, app

FLAGS = flags.FLAGS

flags.DEFINE_bool('debug', False, 'Enable debug output.')


def main(argv):
    del argv
    if FLAGS.debug:
        from cozify.test import debug

    fh, tmp = tempfile.mkstemp()
    config.set_state_path(tmp)

    assert cloud.authenticate()
    config.dump()
    print(hub.tz())
    os.remove(tmp)


if __name__ == "__main__":
    app.run(main)
