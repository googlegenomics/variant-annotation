### Disclaimer

This is a forked version of
[verilylifesciences/variant-annotation](
https://github.com/verilylifesciences/variant-annotation). The intention is to
gradually update various pieces of this repo for variant annotation needs we
have in [googlegenomics/gcp-variant-transforms](
https://github.com/googlegenomics/gcp-variant-transforms) but at the same time
provide annotation related tools/documentation that:
  - can be used independently,
  - are actively maintained with proper test harnesses.

Any README file that has the following warning message indicates a sub-directory
that has not been updated yet:

**WARNING: Not actively maintained!**

This is the list of modules that *are* actively maintained:
* `batch/vep`


variant-annotation
==================

This repository contains code to annotate human sequence variants using
cloud technology to perform analyses in parallel.

Sub-projects:

* [batch annotation](./batch) code for annotating a particular batch of variants
  using annotation resources available at a particular point in time
* [interactive annotation](./interactive) queries and code to annotate variants
  interactively with new annotation resources as they become available
* [annotation curation](./curation) code for ingesting and reformating raw
  annotation resources for use in interactive annotation

The code in this repository is designed for use with genomic variants stored
in [Google BigQuery](https://cloud.google.com/bigquery/) in a
particular
[variant table format](https://cloud.google.com/genomics/v1/bigquery-variants-schema).

Processing
uses
[Google Container Builder](https://cloud.google.com/container-builder/),
[Docker](https://www.docker.com/),
and [dsub](https://cloud.google.com/genomics/v1alpha2/dsub) for batch
processing. We suggest working through the introductory materials for each tool
before working with the code in this repository.

For interactive annotation, parallelism is accomplished due to the use of
BigQuery.  For batch annotation, parallelism is accomplished due to the use of
dsub to run annotation in parallel on small shards of the input file(s).
