#!/bin/bash
grep -v '^#' /etc/protocols | grep -v '^$' | awk '{print $2, $1}' | sort -k1,1 -n -r | head -5
