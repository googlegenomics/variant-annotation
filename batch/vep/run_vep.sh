#!/bin/bash

# Copyright 2018 Google Inc.  All Rights Reserved.
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
#
# This script is intended to be used in the Docker image built for VEP.
# Note that except the single input and output files, all other arguments are
# passed through environment variables.
#
# The only environment variable that has to be set is (others are optional):
#
# VEP_CACHE: The path of the VEP cache which is a single .tar.gz file.
#
# The first argument is the input file (might be a VCF or a compressed VCF) and
# the second is the output file which is always a VCF file.
#
# For the full list of supported environment variables and their documentation
# check README.md.
# Capital letter variables refer to environment variables that can be set from
# outside. Internal variables have small letters.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 input_file output_file"
  exit 1
fi

readonly species="${SPECIES:-homo_sapiens}"
readonly assembly="${GENOME_ASSEMBLY:-GRCh38}"
readonly fork_opt="--fork ${NUM_FORKS:-1}"
readonly other_vep_opts="${OTHER_VEP_OPTS:---everything \
  --check_ref --allow_non_variant}"
readonly annotation_field_name="${VCF_INFO_FILED:-CSQ}"

if [[ ! -r "${VEP_CACHE:?VEP_CACHE is not set!}" ]]; then
  echo "ERROR: Cannot read ${VEP_CACHE}"
  exit 1
fi

# Check that the input file is readable.
readonly input_file=${1}
if [[ ! -r "${input_file}" ]]; then
  echo "ERROR: Cannot read ${input_file}"
  exit 1
fi

echo "Checking the input file at $(date)"
ls -l "${input_file}"

# Make sure output file does not exist and can be written.
readonly output_file=${2}
if [[ -e ${output_file} ]]; then
  echo "ERROR: ${output_file} already exist!"
  exit 1
fi
mkdir -p $(dirname ${output_file})
touch ${output_file}
rm ${output_file}

readonly vep_cache_dir="$(dirname ${VEP_CACHE})"
readonly vep_cache_file="$(basename ${VEP_CACHE})"
pushd ${vep_cache_dir}
if [[ -d "${species}" ]]; then
  echo "The cache is already decompressed; found ${species} at $(date)"
else
  echo "Decompressing the cache file ${vep_cache_file} started at $(date)"
  tar xzvf "${vep_cache_file}"
  if [[ ! -d "${species}" ]]; then
    echo "Cannot find directory ${species} after decompressing ${vep_cache_file}!"
    exit 1
  fi
fi
popd

readonly vep_command="/opt/variant_effect_predictor/vep -i ${input_file} \
  -o ${output_file} --dir ${vep_cache_dir} --offline --species ${species} \
  --assembly ${assembly} --vcf --allele_number \
  --vcf_info_field ${annotation_field_name} ${fork_opt} ${other_vep_opts}"
echo "VEP command is: ${vep_command}"

echo "Running vep started at $(date)"
# The next line should not be quoted since we want word splitting to happen.
${vep_command}
