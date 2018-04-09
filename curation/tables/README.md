**WARNING: Not actively maintained!**

Curate Individual Annotation Sources
====================================

This tutorial loads several annotation sources to individual BigQuery tables.
These tables are already available in BigQuery
dataset
[bigquery-public-data:human_variant_annotation](https://bigquery.cloud.google.com/dataset/bigquery-public-data:human_variant_annotation),
but the configuration in this tutorial can be updated to load new versions of
these resources or load additional annotation resources.

[Container Builder](https://cloud.google.com/container-builder/docs/overview),
[dsub](https://github.com/googlegenomics/dsub)
and [Google Genomics](https://cloud.google.com/genomics/) are used to run all of
these steps in the cloud.

## (1) Configure project variables.

Set a few environment variables to facilitate cutting and pasting the subsequent
commands.

``` bash
# The Google Cloud Platform project id in which the Docker containers
# will be built and stored.
PROJECT_ID=your-project-id
# The bucket name (with the gs:// prefix) where dsub logs will
# be written.
BUCKET=gs://your-bucket-name
# The BigQuery destination dataset for the imported annotations.
DATASET=your_bigquery_dataset_name
```

## (2) Build the importer Docker container.

Build the VCF importer image using the Container Builder service:

``` bash
gcloud container builds submit \
    --project ${PROJECT_ID} \
    --tag gcr.io/${PROJECT_ID}/vcf_to_bigquery \
    .
```

## (3) Test a small import.

The target BigQuery dataset must already exist, and the service account used to
run [dsub](https://cloud.google.com/genomics/v1alpha2/dsub) jobs must have
"BigQuery Data Owner" role.  (The Compute Engine default service account will
not have this role by
default.
[It would need to be added.](https://cloud.google.com/iam/docs/granting-roles-to-service-accounts))

Submit a single VCF import task
via [dsub](https://cloud.google.com/genomics/v1alpha2/dsub).  Here we use the
small file
`gs://genomics-public-data/1000-genomes/vcf/ALL.chrY.genome_strip_hq.20101123.svs.low_coverage.genotypes.vcf`
for a quick test.

``` bash
dsub \
  --project ${PROJECT_ID} \
  --zones "us-*" \
  --logging ${BUCKET}/upload_logs \
  --image gcr.io/${PROJECT_ID}/vcf_to_bigquery \
  --scopes "https://www.googleapis.com/auth/bigquery" \
    "https://www.googleapis.com/auth/devstorage.read_write" \
  --env \
    SOURCE_VCFS=gs://genomics-public-data/1000-genomes/vcf/ALL.chrY.genome_strip_hq.20101123.svs.low_coverage.genotypes.vcf \
    PROJECT=${PROJECT_ID} \
    DATASET=${DATASET} \
    VARIANTSET=test \
    TABLE=${PROJECT_ID}.${DATASET}.test \
  --script launch_import_vcf_to_bigquery.sh
```

## (4) Configure the annotation sources and destinations.

Edit [vcf_manifest.tsv](vcf_manifest.tsv) to use your desired Cloud Storage,
Google Genomics, and BigQuery destinations.  It can also be edited to use newer
versions of the annotation sources and/or add more annotation sources where the
file format is VCF.

## (5) Run all the annotation imports in parallel.

Submit multiple parallel imports via
[dsub](https://cloud.google.com/genomics/v1alpha2/dsub):

``` bash
dsub \
  --project ${PROJECT_ID} \
  --zones "us-*" \
  --logging ${BUCKET}/upload_logs \
  --image gcr.io/${PROJECT_ID}/vcf_to_bigquery \
  --scopes "https://www.googleapis.com/auth/bigquery" \
    "https://www.googleapis.com/auth/devstorage.read_write" \
  --tasks vcf_manifest.tsv \
  --script launch_import_vcf_to_bigquery.sh
```
