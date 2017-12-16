#!/usr/bin/env python3
import tempfile, os
from cozify import config, cloud

def main():
    fh, tmp = tempfile.mkstemp()
    config.setStatePath(tmp)
    
    cloud.authenticate()
    config.dump_state()
    os.remove(tmp)

if __name__ == "__main__":
        main()
