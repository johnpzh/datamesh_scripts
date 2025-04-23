#!/bin/bash

set -u

echo
echo "CURRENT_DIR: ${CURRENT_DIR} Type: ${root_type} Hostname: $(hostname)"
echo

start_time=$(date +%s.%N)

set -x
rm -rf "${CURRENT_DIR}"
set +x

end_time=$(date +%s.%N)
exe_time=$(echo "${end_time} - ${start_time}" | bc -l)
echo
echo "Removed ${CURRENT_DIR} (${exe_time} secs, Hostname: $(hostname))"
echo