#!/usr/bin/env python3
import os
import tempfile

from cozify import cloud, config, hub


def main():
    fh, tmp = tempfile.mkstemp()
    config.setStatePath(tmp)

    assert cloud.authenticate()
    config.dump_state()
    print(hub.tz())
    os.remove(tmp)


if __name__ == "__main__":
    main()
