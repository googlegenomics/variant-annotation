# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

perl $VEP_SCRIPT \
--allele_num \
--check_ref \
--everything \
--vcf_info_field CSQ_VT \
--format vcf \
--tab \
--offline \
--assembly $ASSEMBLY \
-o /dev/stdout \
--force_overwrite \
--no_stats \
--warning_file warnings.txt \
 --dir $VEP_DIR
