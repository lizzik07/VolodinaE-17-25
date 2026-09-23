#!/bin/bash
dir="${1:-.}"

find "$dir" -type f -print0 \
  | xargs -0 md5sum \
  | sort \
  | awk '
      {
        hash = $1
        $1 = ""
        file = substr($0, 2)
        if (hash == prev_hash) {
          if (!printed_group) {
            print prev_file
            printed_group = 1
          }
          print file
        } else {
          printed_group = 0
        }
        prev_hash = hash
        prev_file = file
      }
    '
