# Annotation Server

## TODO: add descriptions of architecture, development, deployment, etc.

## WARNING

This server is a prototype that is not productionized yet.
But, in initial testing, it has been shown to scale well with Variant Transforms.
The client side code is also still in the prototype phase, and can be found here:

[Variant Transforms PR #361](https://github.com/googlegenomics/gcp-variant-transforms/pull/361)

## Getting Started

The server can be deployed either to Google App Engine, or locally on localhost. To launch to GAE, run:

```
$ cd ~/variant-annotation/service/server/
$ gcloud app deploy --project gcp-variant-transforms-test
```

You can verify that you’re in the correct directory for launching to GAE by ensuring you are in the same folder as the app.yaml file. Launching is a slow process and can easily take 10-20 minutes.

To speed development cycles, you can also run locally. Before launching, add the appropriate environment variables. For example, the following lines can be added to ~/.bashrc:

```
#ENVIRONMENT variables for VEP server
ANNOTATION_SERVER_ENV="local"
VEP_DIR="${HOME}/.vep/"
VEP_SCRIPT="${HOME}/Code/ensembl-vep/vep"
ASSEMBLY="GRCh38"
```

Once these variables are defined, just run:

```
$ cd ~/variant-annotation/service/server/
$ python main.py
```
