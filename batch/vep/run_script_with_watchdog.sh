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

# This script runs another script (first argument) in the background. Every
# few seconds (second argument), it reads the time in seconds from one watchdog
# file (third argument) and checks whether the watchdog file is up to date.
# Once the watchdog file is found to be stale, the background process will be
# killed.

function get_last_update_time {
  next_wait_time=0
  declare -i last_update_time
  until last_update_time=`gsutil cat ${1}` || [ ${next_wait_time} -eq 4 ]; do
    sleep $(( next_wait_time++ ))
  done
  echo ${last_update_time}
}

set -euo pipefail

script_to_run=${1}
interval_in_seconds=${2}
watchdog_file=${3}


${script_to_run} ${@:4} &

background_pid="$!"
while ps -p ${background_pid} > /dev/null
do
  start=$(get_last_update_time ${watchdog_file})
  declare -i end
  end=`date +%s`
  diff="$((end-start))"
  echo "The watchdog file is updated ${diff} seconds ago."
  if (($diff>4*${interval_in_seconds})); then
    echo "ERROR: The watchdog file is stale, and running of ${script_to_run} has been killed."
    kill ${background_pid}
    exit 1
  else
    echo "Waiting"
    sleep ${interval_in_seconds}
  fi
done
wait ${background_pid}
if [[ $? -ne 0 ]]; then
  echo "Running of ${script_to_run} failed."
  exit 1
else
  echo "Running of ${script_to_run} succeed."
fi
