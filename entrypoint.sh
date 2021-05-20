#!/bin/bash

set -ex

exec /usr/bin/tini -s -- "$@"
