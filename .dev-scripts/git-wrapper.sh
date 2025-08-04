#!/bin/bash
# Git wrapper script with locale settings for MQTT Publisher

# Set locale to avoid git warnings
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Run git with all passed arguments
exec git "$@"
