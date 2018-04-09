**WARNING: Not actively maintained!**

Run the annotator
=================

This tutorial uses VEP to
annotate
[Platinum Genomes variants called by DeepVariant](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/platinum_genomes_deepvariant.html) and
aligned to build GRCh38.

The [BigQuery Web UI](https://cloud.google.com/bigquery/quickstart-web-ui)
and [dsub](https://cloud.google.com/genomics/v1alpha2/dsub) are used to run all
of these steps in the cloud.

## (1) Identify the variants you wish to annotate.

A query can be used to export variants from
BigQuery
[variants tables](https://cloud.google.com/genomics/v1/bigquery-variants-schema)
in
[a format that VEP can take as input](http://www.ensembl.org/info/docs/tools/vep/vep_formats.html#input).

* The specific query below will export variants for all members of the Platinum
  Genomes cohort in "ensembl" format.
* To use variants from your own table, just change the table name.
* To work with a subset of genomes or just one genome, modify the query to
  filter by call set name.

Run this query using
the [BigQuery Web UI](https://cloud.google.com/bigquery/quickstart-web-ui) and
materialize the result to a table in your project.

``` sql
#standardSQL
  --
  -- Extract the information needed to annotate variants with VEP.
  -- This is small test on just the variants in chromosome 22.
  --
WITH
  variants AS (
  SELECT
    reference_name AS chrom,
    start + 1 AS pos, -- convert to 1-based coordinates
    `end`,
    reference_bases AS ref,
    alt
  FROM
    `genomics-public-data.platinum_genomes_deepvariant.single_sample_genome_calls`,
    UNNEST(alternate_bases) AS alt -- flatten multiallelic sites
  WHERE
    -- Include only sites of variation (exclude non-variant segments).
    alt IS NOT NULL AND alt NOT IN ("<NON_REF>", "<*>")
    -- Remove this line to include the entire genome.
    AND reference_name IN ('chr22', '22')
  )
SELECT
  -- http://www.ensembl.org/info/docs/tools/vep/vep_formats.html#input
  CONCAT(
    chrom, '\t',
    CAST(pos AS STRING), '\t',
    CAST(`end` AS STRING), '\t',
    ref, '/', alt, '\t',
    '+') AS vep_input
FROM
  variants
```

## (2) Extract the VEP input to Cloud Storage.

[Export](https://cloud.google.com/bigquery/docs/exporting-data) the contents of
the table created in the prior step as a gzipped CSV file to Cloud Storage (for
example to path `gs://your-bucket-name/platinum-genomes-grch38-chr22.csv.gz`).

## (3) Run VEP on the variants.

Run [run_vep_remote.sh](./run_vep_remote.sh) to
launch [dsub](https://github.com/googlegenomics/dsub) jobs that will use the VEP
Docker container to run VEP on the variants, writing the resulting annotations
as a BigQuery table.

* Run `./run_vep_remote.sh --help` for additional documentation on its command
  line parameters.

``` bash
# The Google Cloud Platform project id in which the docker containers
# are stored.
PROJECT_ID=your-project-id
# The bucket name (with the gs:// prefix) to hold temp files and logs.
BUCKET=gs://your-bucket-name
# The full path to the VEP input file.
INPUT_FILE=${BUCKET}/platinum-genomes-grch38-chr22.csv.gz

# Kick off annotation.
./run_vep_remote.sh \
    --project_id ${PROJECT_ID} \
    --bucket ${BUCKET}/temp \
    --docker_image gcr.io/${PROJECT_ID}/vep_grch38 \
    --table_name platinum_genomes_grch38_chr22_annotations \
    --shards_per_file 10 \
    ${INPUT_FILE}
```

## (3) Check the annotations.

Use the following query to do some basic checks on the annotations.  The query
below assumes the annotations are in table
`vep.platinum_genomes_grch38_chr22_annotations` in your project.

``` sql
#standardSQL
  --
  -- Count the number of variants per chromosome for both the variants and
  -- VEP output table.  This basic QC metric ensures that every chromosome
  -- we expected successfully completed.
  --
SELECT chrom, variants_count, vep_count
FROM (
  SELECT LTRIM(reference_name, "chr") AS chrom, COUNT(1) AS variants_count
  FROM
    `genomics-public-data.platinum_genomes_deepvariant.single_sample_genome_calls`,
    UNNEST(alternate_bases) AS alt -- flatten multi allelic sites
  WHERE
    -- Include only sites of variantion (exclude non-variant segments).
    alt IS NOT NULL AND alt NOT IN ("<NON_REF>", "<*>")
  GROUP BY reference_name)
FULL JOIN (
  SELECT LTRIM(seq_region_name, "chr") AS chrom, COUNT(1) AS vep_count
  FROM `vep.platinum_genomes_grch38_chr22_annotations`
  GROUP BY seq_region_name)
USING (chrom)
WHERE vep_count IS NOT NULL
ORDER BY chrom
```

We expect a result of 210,279 variants and VEP annotations for chromosome 22.

## (4) Optional: Reshape the annotations table for easier JOINs.

The annotations table created by VEP is a little different than
the
[variant tables](https://cloud.google.com/genomics/v1/bigquery-variants-schema):

* VEP uses 1-based coordinates whereas
  the
  [variants tables](https://cloud.google.com/genomics/v1/bigquery-variants-schema) use
  0-based coordinates per [GA4GH](http://ga4gh.org/).
* VEP rewrites some of the fields. For example field `start`
  excludes the first base for a deletion.

Run a query like the following to reshape the annotations data and materialize
the result to a new table.

``` sql
#standardSQL
  --
  -- Add additional columns to the VEP table to facilitate easier JOINs
  -- with variant tables.
  --
SELECT
  SPLIT(input, "\t")[OFFSET(0)] AS reference_name,
  CAST(SPLIT(input, "\t")[OFFSET(1)] AS INT64) - 1 AS start_0_based_coords,
  SPLIT(SPLIT(input, "\t")[OFFSET(3)], '/')[OFFSET(0)] AS reference_bases,
  SPLIT(SPLIT(input, "\t")[OFFSET(3)], '/')[OFFSET(1)] AS alternate_bases,
  *
FROM
  `vep.platinum_genomes_grch38_chr22_annotations`
```
