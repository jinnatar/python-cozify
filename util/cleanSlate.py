#!/usr/bin/env python3
import tempfile, os
from cozify import config, cloud, hub


def main():
    fh, tmp = tempfile.mkstemp()
    config.set_state_path(tmp)

    assert cloud.authenticate()
    config.dump()
    print(hub.tz())
    os.remove(tmp)


if __name__ == "__main__":
    main()
