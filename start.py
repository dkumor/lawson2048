#!/usr/bin/env python
import cvserver
import sys

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    cvserver.main(port)
