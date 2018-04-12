#!/usr/bin/env python3                                                                                                                                         
from cozify import hub
import pprint, sys
from absl import flags, app

from cozify.test import debug

FLAGS = flags.FLAGS

flags.DEFINE_string('device', None, 'Device to operate on.')

def main(argv):
    del argv
    hub.device_toggle(FLAGS.device)

if __name__ == "__main__":
    flags.mark_flag_as_required('device')
    app.run(main)
