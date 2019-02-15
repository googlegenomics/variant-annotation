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
# Returns the generation number of a GCS file.
# Arguments:
#   $1: The GCS file.
#################################################
function get_last_update_time {
  gsutil stat $1 | awk '$1 == "Generation:" {print $2}'
}

function main {
  if [[ $# < 3 ]]; then
    echo "Usage: $0 <script_to_run> <watchdog_file_update_interval> <watchdog_file> <script_to_run_args>"
    exit 1
  fi
  script_to_run="$1"
  watchdog_file_update_interval="$2"
  watchdog_file="$3"
  script_to_run_args="${@:4}"
  watchdog_file_allowed_stale_time="$((4*watchdog_file_update_interval))"

  ${script_to_run} ${script_to_run_args} &

  background_pid="$!"
  while ps -p "${background_pid}" > /dev/null
  do
    last_update_sec="$(($(get_last_update_time ${watchdog_file})/1000000))"
    declare -i now_sec
    now_sec="$(date +%s)"
    last_update_age_sec="$((now_sec-last_update_sec))"
    echo "The watchdog file is updated ${last_update_age_sec} seconds ago."
    if (("${last_update_age_sec}">"${watchdog_file_allowed_stale_time}")); then
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
