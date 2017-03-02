#!/bin/sh

if [ $# == 1 ]; then
  image="$1"
  echo $image
  if [ -f $image ]; then
    echo "exist"
    script="tell application \"Finder\" to set desktop picture to POSIX file \"${image}\""
    echo $script
    osascript -e "$script"
    echo "done"
  else
    echo "not exist"
  fi
fi
