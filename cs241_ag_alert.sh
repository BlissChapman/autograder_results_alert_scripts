#!/bin/bash

# TODO: Make this generic for any AG results.
LTIME=`stat -f %Z shell/results.json`

while true
do
  svn up
  ATIME=`stat -f %Z shell/results.json`
  if [[ "$ATIME" != "$LTIME" ]]
  #if [ 1 -eq 1 ]
  then
      # send slack notification
      # TODO: Make message specific to AG result and attach random pic of doggo.
      curl -X POST -H 'Content-type: application/json' --data '{"text":"<!channel> Shell Autograder results released!"}' $CS241_AG_WEBHOOK

      # For local notifications on macOS:
      # osascript -e 'display notification "CS241 AG results were released!" with title "AG Results"'
      exit 0
  fi
  sleep 60
done
