**WARNING: Not actively maintained!**

Create an All-Possible SNPs Table
=================================

This tutorial combines a particular reference genome with individual annotation
resources to create an "all possible SNPs" table.

[dsub](https://cloud.google.com/genomics/v1alpha2/dsub)
and [BigQuery](https://cloud.google.com/bigquery/) are used to run all of these
steps in the cloud.

## Status of this tutorial

This is a work-in-progress. Next steps are to:

1. add more annotation resources to the JOIN
2. add examples that make use of the all possible SNPs GRCh38 table to analyze
   SNPs from
   the
   [Platinum Genomes DeepVariant](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/platinum_genomes_deepvariant.html) cohort. These
   examples would be similar to
   https://github.com/googlegenomics/bigquery-examples/tree/master/platinumGenomes.

## (1) Configure project variables.

Set a few environment variables to facilitate cutting and pasting the subsequent
commands.

``` bash
# The Google Cloud Platform project id in which to process the annotations.
PROJECT_ID=your-project-id
# The bucket name (with the gs:// prefix) for logs and temp files.
BUCKET=gs://your-bucket-name
# The BigQuery dataset, which must already exist, in which to store annotations.
DATASET=your_bigquery_dataset_name
```
## (2) Identify the reference genome you wish to annotate.

In this tutorial we're specifically working
with
[Verily’s version of GRCh38](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/reference_genomes.html#verily-s-grch38).

Note that instead you could:

* Use one of the other reference genomes are already available in Cloud Storage.
See
[Reference Genomes](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/reference_genomes.html) for
the list and Cloud Storage paths.
* Copy the FASTA file for the desired reference genome to cloud storage. For
  more detail,
  see
  [Copying large files to a bucket](https://cloud.google.com/storage/docs/working-with-big-data#copy-large-file).

## (3) Convert the FASTA file.

Run the following [dsub](https://github.com/googlegenomics/dsub) command to
convert the FASTA file for the reference genome into a format ammenable to
BigQuery.

``` bash
# Copy the script dsub will run to Cloud Storage.
gsutil cp fasta_to_kv.py ${BUCKET}

# Run the conversion operation.
dsub \
  --project ${PROJECT_ID} \
  --zones "us-central1-*" \
  --logging ${BUCKET}/fasta_to_kv.log \
  --image python:2.7-slim \
  --input FASTA=gs://genomics-public-data/references/GRCh38_Verily/GRCh38_Verily_v1.genome.fa \
  --input CONVERTER=${BUCKET}/fasta_to_kv.py \
  --output KV=${BUCKET}/GRCh38_Verily_v1.genome.txt \
  --command 'cat "${FASTA}" | python "${CONVERTER}" > "${KV}"' \
  --wait
```

## (4) Load the sequences into BigQuery.

Use the bq command line tool to load the sequences into BigQuery.

``` bash
bq --project ${PROJECT_ID} load \
  -F '>' \
  --schema unused:string,chr:string,sequence_start:integer,sequence:string \
  ${DATASET}.VerilyGRCh38_sequences \
  ${BUCKET}/GRCh38_Verily_v1.genome.txt
```

## (5) Reshape the sequences into SNPs and JOIN with annotations.

Run script [render_templated_sql.py](./render_templated_sql.py) to create the
SQL that will perform the JOIN.

``` bash
python ./render_templated_sql.py \
  --sequence_table ${DATASET}.VerilyGRCh38_sequences \
  --b38
```

Then run the generated SQL via the BigQuery web UI or the bq command line tool
and materialize the result to a new table.

See `render_templated_sql.py --help` for more details.

