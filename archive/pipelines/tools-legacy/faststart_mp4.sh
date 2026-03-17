#!/bin/bash

FILE="$1"

# Only act on mp4
[[ "${FILE,,}" != *.mp4 ]] && exit 0

TMP="${FILE%.mp4}.faststart.mp4"

/opt/homebrew/bin/ffmpeg -y -loglevel error \
  -i "$FILE" \
  -movflags +faststart \
  -c copy \
  "$TMP" || exit 0

mv "$TMP" "$FILE"
