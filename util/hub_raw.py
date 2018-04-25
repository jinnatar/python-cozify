#!/usr/bin/env python3
from cozify import cloud, hub, hub_api
from cozify.Error import APIError
import pprint, sys
from absl import flags, app, logging

FLAGS = flags.FLAGS

flags.DEFINE_bool('debug', False, 'Enable debug output.')
flags.DEFINE_string('path', None, 'Path to query.')
flags.DEFINE_string('put', None, 'Use PUT instead of GET and send this data.')
flags.DEFINE_string('post', None, 'Use POST instead of GET and send this data.')
flags.DEFINE_bool('pretty', False, 'Pretty-print output assuming it to be a dict.')


def main(argv):
    del argv
    if FLAGS.debug:
        from cozify.test import debug

    hub.ping()
    try:
        if FLAGS.put:
            call = hub_api.put
            payload = FLAGS.put
        elif FLAGS.post:
            call = hub_api.post
            payload = FLAGS.post
        else:
            call = hub_api.get
            payload = ''
        output = call(
            FLAGS.path,
            host=hub.host(),
            remote=hub.remote(),
            hub_token=hub.token(),
            cloud_token=cloud.token(),
            payload=payload)
        if FLAGS.pretty:
            import pprint
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(output)
        else:
            print(output)
    except APIError as e:
        if e.status_code == 404:
            logging.error('Unknown API endpoint \'{0}\': {1}'.format(FLAGS.path, e))
        else:
            raise


if __name__ == "__main__":
    flags.mark_flag_as_required('path')
    app.run(main)
