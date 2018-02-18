#!/usr/bin/env python

import os
import sys
import time
import atexit
import argparse
import subprocess

parser = argparse.ArgumentParser(description=(
"""
EXAMPLE: git submodule foreach $PWD/test.py

Loops overall submodules (skipping omero-test-infra)
and calls .omeroci/infra, which in turn checks out
a given branch of omero-test-infra and runs the
appopriate stage. After execution, .omero/compose down
is run.
"""
), formatter_class=argparse.RawTextHelpFormatter)


def process(cmd, logging="onerror"):
    if logging == "all":
        subprocess.call(cmd.split())
    else:
        p = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        o, e = p.communicate()
        rc = p.poll()
        if rc != 0:
            print "Failed: %s" % rc
            if logging == "onerror":
                print "=" * 20
                print o


def main(logging="onerror"):
    name = os.path.basename(os.getcwd())
    if name == "omero-test-infra":
        print "Skipping core"
        sys.exit(0)
    
    
    start = time.time()
    
    def cleanup():
        stop = time.time()
        print "Elapsed: %ds" % (stop-start)
        process(".omero/compose down")
        done = time.time()
        print "Shutdown took %ds" % (done-stop)
    
    atexit.register(cleanup)
    process(".omeroci/infra")

if __name__ == "__main__":
    parser.add_argument("--logging",
                       choices=("none", "all", "onerror"),
                       default="onerror")
    ns = parser.parse_args()
    main(ns.logging)
