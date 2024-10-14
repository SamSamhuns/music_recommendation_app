#!/bin/bash
docker build -t music_analysis:latest --build-arg UID=$(id -u) .
