**WARNING: Not actively maintained!**

Batch Variant Annotation
========================

Given a set of variants, the code here will allow you to annotate a batch of
variants using annotation resources available at a particular point in time.
(In comparison, using [interactive annotation](../interactive), variants can be
annotated on the fly with new annotation resources as they become available.)

This code uses
Ensembl's
[Variant Effect Prediction](
http://www.ensembl.org/info/docs/tools/vep/index.html) (VEP)
from McLaren et. al. 2016
([doi:10.1186/s13059-016-0974-4](
https://genomebiology.biomedcentral.com/articles/10.1186/s13059-016-0974-4))
to annotate variants either in VCF files or in a BigQuery table.

To annotate VCF files, check the [documentation](./vep/README.md) in `vep`
directory on how to build docker images containing VEP, how to create VEP cache
for those images, and how to run VEP.

**WARNING: The build_annotator and run_annotator pieces below are not actively
maintained in this repo yet!**

Annotating variants in BigQuery talbes is horizontally scalable due to the use
of [dsub](https://cloud.google.com/genomics/v1alpha2/dsub). A separate instance
of VEP is run by dsub for each shard of each of the files passed on the command
line.  VEP is also configured to run with as many threads as the number of cores
on the virtual machine instantiated by dsub.

## Status of this sub-project

VEP can be configured in many ways and can use as input a large variety of
annotation sources. This code illustrates one possible configuration and could
be modified to accomodate other configurations.

All steps are run in the cloud, but each individual step is launched manually.

## Overview

### Build the annotator

The first step involves building the Docker container holding VEP and cached
annotations for the desired build of the human genome reference.

A second container is built to curate and
cache [dbNSFP](https://sites.google.com/site/jpopgen/dbNSFP) in Cloud Storage.
This is done because dbNSFP is quite a large annotation resource and therefore
we choose not to add it to the same Docker container that includes VEP.

[Follow the tutorial](./build_annotator/README.md) to build the tools needed to
annotate GRCh37 or GRCh38 of the human genome reference.

### Run the annotator

After the annotator has been built for the desired build of the human reference
genome, it can be used to annotate variants from a single genome or a cohort of
genomes in a BigQuery
[variant table](https://cloud.google.com/genomics/v1/bigquery-variants-schema).

[Follow the tutorial](./run_annotator/README.md) to
annotate
[Platinum Genomes variants called by DeepVariant](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/platinum_genomes_deepvariant.html) and
aligned to build GRCh38.
