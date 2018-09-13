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
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app
CMD gunicorn -b :$PORT -t 600 main:app
