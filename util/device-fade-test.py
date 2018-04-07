#!/usr/bin/env python3
from cozify import hub
import numpy, time
from absl import flags, app

FLAGS = flags.FLAGS

flags.DEFINE_string('device', None, 'Device to operate on.')
flags.DEFINE_float('delay', 0.5, 'Step length in seconds.')
flags.DEFINE_float('steps', 20, 'Amount of steps to divide into.')
flags.DEFINE_bool('verify', False, 'Verify if value went through as-is.')


def main(argv):
    del argv
    for step in numpy.flipud(numpy.linspace(0.0, 1.0, num=FLAGS.steps)):
        hub.light_brightness(FLAGS.device, step)
        time.sleep(FLAGS.delay)
        read = 'N/A'
        result = '?'
        if FLAGS.verify:
            devs = hub.devices()
            read = devs[FLAGS.device]['state']['brightness']
            if step == read:
                result = '✔'
            else:
                result = '✖'
        print('[{2}] set: {0} vs. read: {1}'.format(step, read, result))


if __name__ == "__main__":
    flags.mark_flag_as_required('device')
    app.run(main)
