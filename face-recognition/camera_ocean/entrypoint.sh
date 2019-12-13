#!/usr/bin/env bash

set -e


case "$1" in

    run)
        cd /app/
        shift
        python camera_ocean/cli.py run "$@"
        ;;

    *)
        exec "$@"
        ;;

esac
