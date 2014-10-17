#!/usr/bin/env python
import server
import sys

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server.main(port)
