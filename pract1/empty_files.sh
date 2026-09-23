#!/bin/bash
dir="${1:-.}"
find "$dir" -maxdepth 1 -type f -empty
