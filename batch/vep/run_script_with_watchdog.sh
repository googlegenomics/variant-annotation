#!/bin/bash

# Copyright 2019 Google Inc.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script runs `script_to_run` (first argument) in the background. Every
# `watchdog_file_update_interval` seconds (second argument), it checks the last
# update time of `watchdog_file` (third argument). Once the watchdog file is
# found to be stale, the background process will be killed. The arguments needed
# for `script_to_run` are passed after the third argument.

set -euo pipefail

#################################################
# Returns the generation number of a GCS file. In case of failure, it sleeps and
# retries for at most 4 times.
# Arguments:
#   $1: The GCS file.
#################################################
function get_last_update_time {
  next_wait_time=0
  until last_update_time_in_microseconds=`gsutil stat ${1} | awk '$1 == "Generation:" {print $2}'` || [ ${next_wait_time} -eq 4 ]; do
    sleep $(( next_wait_time++ ))
  done
  echo ${last_update_time_in_microseconds}
}

function main {
  script_to_run=${1}
  watchdog_file_update_interval=${2}
  watchdog_file=${3}
  script_args=${@:4}
  watchdog_file_stale_time="$((4*${watchdog_file_update_interval}))"

  ${script_to_run} ${script_args} &

  background_pid="$!"
  while ps -p ${background_pid} > /dev/null
  do
    start="$(($(get_last_update_time ${watchdog_file})/1000000))"
    declare -i end
    end=`date +%s`
    diff="$((end-start))"
    echo "The watchdog file is updated ${diff} seconds ago."
    if ((${diff}>${watchdog_file_stale_time})); then
      echo "ERROR: The watchdog file is stale, and running of ${script_to_run} has been killed."
      kill "${background_pid}"
      exit 1
    else
      sleep "${watchdog_file_update_interval}"
    fi
  done
  wait "${background_pid}"
  if [[ $? -ne 0 ]]; then
    echo "Running of ${script_to_run} failed."
    exit 1
  else
    echo "Running of ${script_to_run} succeed."
    exit 0
  fi
}

main "$@"
