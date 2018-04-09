**WARNING: Not actively maintained!**

Build the annotator
===================

This tutorial builds the tools needed to annotate GRCh37 or GRCh38 of the human
genome reference.

[Container Builder](https://cloud.google.com/container-builder/docs/overview)
and [dsub](https://github.com/googlegenomics/dsub) are used to run all of these
steps in the cloud.

## (1) Configure project variables.

Set a few environment variables to facilitate cutting and pasting the subsequent
commands.

``` bash
# The Google Cloud Platform project id in which the Docker containers
# will be built and stored.
PROJECT_ID=your-project-id
# The bucket name (with the gs:// prefix) where the cached version of
# dbNSFP should be stored.
BUCKET=gs://your-bucket-name
```

## (2) Build the VEP Docker container.

Run one of the commands below to build a Docker container that is configured to
run VEP on human genetic variants in GRCh37 or GRCh38 coordinates with
annotations including dbNSFP, SIFT, and many others. Both of these commands can
be run in parallel if you wish to annotate using both reference genomes.

### GRCh37

``` bash
gcloud container builds submit \
    --substitutions=_GENOME_ASSEMBLY=GRCh37,_ENSEMBL_RELEASE=89,_DBNSFP_BASE=${BUCKET}/dbNSFPv2.9.3/dbNSFP,_CONTAINER_SUFFIX=_89_grch37:latest \
    --config=vep_container.yaml \
    .
```

### GRCh38

``` bash
gcloud container builds submit \
    --substitutions=_GENOME_ASSEMBLY=GRCh38,_ENSEMBL_RELEASE=89,_DBNSFP_BASE=${BUCKET}/dbNSFPv3.4c/dbNSFP,_CONTAINER_SUFFIX=_89_grch38:latest \
    --config=vep_container.yaml \
    .
```
## (3) Cache dbNSFP.

First run the command below to create the Docker container with tools and
scripts needed to process dbNSFP. This Docker container can be used for any
version of dbNSFP.

``` bash
gcloud --project ${PROJECT_ID} container builds submit \
    --substitutions=_CONTAINER_TAG=:latest \
    --config=dbNSFP_container.yaml \
    .
```

Then run the container via dsub to download and cache dbNSFP annotations in
Cloud Storage. These commands can be run in parallel if you wish to annotate
using both reference genomes.

* Note that it can take several hours for the job to complete.
* The values for `FILEID` in the commands came
  from [dbNSFP documentation](https://sites.google.com/site/jpopgen/dbNSFP)
  where you can also get detail on other available versions of dbNSFP.

### GRCh37

``` bash
dsub \
  --project ${PROJECT_ID} \
  --image gcr.io/${PROJECT_ID}/dbnsfp_cache_builder:latest \
  --zones "us-central1-*" \
  --disk-size 200 \
  --min-cores 8 \
  --logging ${BUCKET}/dbNSFPv3.4c/dbNSFPv3.4c.log \
  --env FILEID=0B60wROKy6OqcaWJ4Y0xvR2k1aUU \
  --output-recursive OUTPUT_PATH=${BUCKET}/dbNSFPv3.4c/ \
  --command '/opt/download_dbNSFP.sh &&
             /opt/build_databases.sh'
```

### GRCh38

``` bash
dsub \
  --project ${PROJECT_ID} \
  --image gcr.io/${PROJECT_ID}/dbnsfp_cache_builder:latest \
  --zones "us-central1-*" \
  --disk-size 200 \
  --min-cores 8 \
  --logging ${BUCKET}/dbNSFPv2.9.3/dbNSFPv2.9.3.log \
  --env FILEID=0B60wROKy6OqceTNZRkZnaERWREk \
  --output-recursive OUTPUT_PATH=${BUCKET}/dbNSFPv2.9.3/ \
  --command '/opt/download_dbNSFP.sh &&
             /opt/build_databases.sh'
```
