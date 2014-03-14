#!/usr/bin/env sh

repo=$(dirname "$0")/..
. "$repo/env/bin/activate"
exec python "$repo/python/hat.py" "$@"

