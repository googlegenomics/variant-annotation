**WARNING: Not actively maintained!**

Interactive Variant Annotation
==============================

Given a particular set of variants for an individual or a cohort, the code here
will allow you to interactively annotate the sequence variants
using
[annotation resources available in BigQuery](http://googlegenomics.readthedocs.io/en/latest/use_cases/discover_public_data/annotations_toc.html). Note
that if there is a newer version of the annotation resource that you wish to
use, [you can load it into BigQuery](../curation/tables).

## Status of this sub-project

There is only one example here at the moment but see also similar work:

* http://isb-cancer-genomics-cloud.readthedocs.io/en/latest/sections/COSMIC.html
* https://github.com/googlegenomics/bigquery-examples/tree/master/platinumGenomes
* http://googlegenomics.readthedocs.io/en/latest/use_cases/annotate_variants/interval_joins.html

TODO: add more example queries, Datalab notebooks and RMarkdown.

## Examples

### [Datalab](https://cloud.google.com/datalab/) Notebook Examples

 1. Notebook [InteractiveVariantAnnotation.ipynb](./InteractiveVariantAnnotation.ipynb) will return variants for sample NA12878 that are:
   * annotated as 'pathogenic' or 'other' in ClinVar
   * with observed population frequency less than 5%

