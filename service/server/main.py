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

import os
import logging

from subprocess import Popen, PIPE, STDOUT, check_call

from flask import Flask, jsonify, request

from headers import VEP_HEADERS


# This variant is passed to VEP when `headers` is called. This works
# even when `--check_ref` is used because the headers line is still produced.
SAMPLE_VARIANT = 'chr1	807692	.	C	A	0	PASS	KM=11.5	GT	1|1'


def setup_vep_cache():
    """Initialization function to download and build VEP's cache"""
    # TODO(jessime) These values should be loaded from ENV variables
    local_cache = '/mnt/vep/vep_cache/'
    gcs_dir = 'gs://gcp-variant-annotation-vep-cache'
    vep_file = 'vep_cache_homo_sapiens_GRCh38_91.tar.gz'
    gcs_vep_file = os.path.join(gcs_dir, vep_file)
    local_vep_file = os.path.join(local_cache, vep_file)
    check_call('gsutil cp {} {}'.format(gcs_vep_file, local_cache).split())
    check_call('tar xzvf {} -C {}'.format(local_vep_file, local_cache).split())
    # TODO(jessime) Here and elsewhere, replace prints with proper logging
    print 'VEP CACHE setup.'


#Global calls after `setup_vep_cache` is defined but before `app` decorators
if os.environ['ANNOTATION_SERVER_ENV'] == 'production':
    # TODO(jessime) setup configurations for local vs production environments
    setup_vep_cache()
app = Flask(__name__)


def run_vep(variants):
    """Execute VEP in a subprocess.

    Args:
        variants: A single str of vcf formatted variants to be passed to VEP
    Returns:
        response: Dict storing stdout and stderr from VEP subprocess run
    """
    # type: (str) -> Dict[str, str]
    cmd = 'run_vep.sh'
    p = Popen(['bash', cmd], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(input=variants)
    # print('perl stdout: ', stdout)
    # TODO (jessime) Figure out how to deal with harmless warnings.
    # Also figure out how to deal with more important warnings like failing
    # `--check_ref` because the assembly is incorrect
    if stderr.startswith('Possible precedence'):
        stderr = stderr[stderr.index('\n')+1:]
    response = {'stdout': stdout, 'stderr': stderr}
    return response


def extract_headers_and_annotations(vep_tabbed):
    """Separate the header line and annotation lines into seperate variables.

    Args:
        vep_tabbed: str of VEP output in tabbed format. For details see:
            http://useast.ensembl.org/info/docs/tools/vep/vep_formats.html#tab
    Returns:
        header_names: List of annotation header names. e.g. ['GENE', 'IMPACT']
        annotation_lines: All annotations provided by VEP
    """
    # type: (str) -> Tuple[List[str], List[str]]
    header_names = None
    vep_tabbed_lines = vep_tabbed.split('\n')[:-1]  # remove trailing empty line
    annotation_lines = []
    while vep_tabbed_lines:
        line = vep_tabbed_lines.pop(0)
        if line.startswith('#'):
            header_names = line
        else:
            annotation_lines = [line] + vep_tabbed_lines
            break
    header_names = header_names.split('\t')
    return header_names, annotation_lines


def vep_tab_to_json(response):
    """Updates response dict to contain annotations grouped by their variants

    Args:
        response: Dict containing JSON response to send to client
    """
    # TODO(jessime) This function should return something instead of mutating
    # response.
    new_stdout_response = []
    current_variant = None
    header_names, variant_lines = extract_headers_and_annotations(
        response['stdout'])
    for line in variant_lines:
        anno = line.split('\t')
        variant_id = anno.pop(0)
        # TODO(jessime) Why do production annotations give '.' here?
        # Can I reliably use Location as a backup? I'm not sure, but it works
        # for the first 100K of NA12877.vcf. It isn't ideal though.
        if variant_id == '.':
            variant_id = anno[0]
        if variant_id == current_variant:
            new_stdout_response[-1]['data'].append(anno)
        else:
            current_variant = variant_id
            new_variant_dict = {'variant_id': variant_id,
                                'data': [anno]}
            new_stdout_response.append(new_variant_dict)
    print '{} annotations have been processed for {} variants.'.format(
        len(variant_lines), len(new_stdout_response))
    response['stdout'] = new_stdout_response
    # TODO(jessime) I'm pretty sure this isn't necessary any more.
    # Even if it is, tagging it on inside of this function is a bad mutation.
    response['header_names'] = header_names


def check_1to1(response, original_count):
    # TODO(jessime) This code relies on there being a 1-to-1 correspondence
    # between ProcessedVariants and annotations once they have been through
    # vep_tab_to_json. A more robust way of handling this is to make use of the
    # 'variant_id' key in the annotation data dicts made in `vep_tab_to_json`.
    # Those values could store some UID to ensure that annotation data is
    # matched to the proper ProcessedVariant inside of VT.
    grouped_count = len(response['stdout'])
    if grouped_count != original_count:
        variant_names = set(d['variant_id'] for d in response['stdout'])
        print '{} != {}. New names are {}.'.format(grouped_count,
                                                   original_count,
                                                   variant_names)


@app.route('/', methods=['GET', 'POST'])
def annotate():
    """Run annotations.

    Returns:
        response: JSON object containing annotations and/or annotation errors.
            e.g. {'stdout': [{'variant_id': 'chr1:751',
                              'data': [['anno', 'tation', '1'],
                                       ['anno', 'tation', '2']]}]
                  'stderr': '',
                  'header_names': ['name1', 'name2', 'name3']}
    """
    annotator_func = {'vep': run_vep}
    if request.method == 'POST':
        if 'variants' in request.form:
            annotator = request.form.get('annotator', default='vep')
            variants = request.form['variants']
            original_count = variants.count('\n') + 1
            print 'Processing {} variants'.format(original_count)
            response = annotator_func[annotator](variants)
            if not response['stderr']:
                vep_tab_to_json(response)
                check_1to1(response, original_count)
        else:
            response = 'No variant(s) have been POSTed.'
    else:
        response = 'Healthy.'
    return jsonify(response)


@app.route('/headers')
def headers():
    """Run a sample annotation query and return annotation headers.

    Returns:
        headers: Ordered JSON data of annotation headers. e.g.
            [{'name': 'HEADER1', 'type': 'string', 'desc': 'description'},
             {'name': 'HEADER2', 'type': 'string', 'desc': 'description'}]
    """
    response = run_vep(SAMPLE_VARIANT)
    header_names, _ = extract_headers_and_annotations(response['stdout'])
    header_names.pop(0)  #remove variant_id
    headers = [VEP_HEADERS[name] for name in header_names]
    return jsonify(headers)

@app.route('/test')
def test():
    # TODO(jessime) This is a flexible test function for trying things out.
    # It should be deleted before production.
    return jsonify(os.environ['ASSEMBLY'])

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See CMD in Dockerfile.
    app.run(host='127.0.0.1', port=8080, debug=True)
