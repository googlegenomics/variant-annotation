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

# [START dockerfile]
FROM gcr.io/google_appengine/python

# Install the fortunes binary from the debian repositories.
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libarchive-zip-perl \
    libdbd-mysql-perl \
    libdbi-perl \
    libfile-copy-recursive-perl \
    libhts1 \
    libjson-perl \
    libmodule-build-perl \
    tabix \
    unzip \
    zlib1g-dev

#Install VEP per the instructions at:
#http://www.ensembl.org/info/docs/tools/vep/script/vep_download.html#installer
ARG ENSEMBL_RELEASE=91
RUN git clone https://github.com/Ensembl/ensembl-vep.git
WORKDIR ensembl-vep
RUN git checkout release/${ENSEMBL_RELEASE}
RUN perl INSTALL.pl \
    --AUTO a \
    --NO_UPDATE
WORKDIR ..

 ARG CACHE=/mnt/vep/vep_cache/
 RUN mkdir -p ${CACHE}
 RUN pip install gsutil

# Change the -p argument to use Python 2.7 if desired.
RUN virtualenv /env -p python2.7

# Set environment variables for server
ENV ANNOTATION_SERVER_ENV production
ENV VEP_DIR /mnt/vep/vep_cache
ENV VEP_SCRIPT ensembl-vep/vep
ENV ASSEMBLY GRCh38

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate. This ensures the application is executed within
# the context of the virtualenv and will have access to its dependencies.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app
CMD gunicorn -b :$PORT -t 600 main:app
