#!/bin/bash
export PATH=/sct/bin:$PATH
export DISPLAY=:1
Xvfb :1 &
exec "$@"