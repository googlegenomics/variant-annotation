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

"""A small end-to-end client that uses apache_beam, but not Variant Transforms.

This prototype client accepts a path to a VCF file, the path to the newly
annotated VCF file, and either `p` or `d` to specify the `production` or
`development` environment.

Run by:
    python example_client.py path/to/infile.vcf, path/to/outfile.vcf, [p|d]
"""

import sys
import uuid
import requests
import apache_beam as beam

class KeyGenFn(beam.DoFn):

    def __init__(self, chunk=1000):
        self.chunk = chunk
        self.key = uuid.uuid4()
        self.counter = 0

    def process(self, element):
        self.counter += 1
        if self.counter == self.chunk:
            self.counter = 0
            self.key = uuid.uuid4()
        yield self.key, element


class Requester(beam.DoFn):

    def __init__(self, url='https://gcp-variant-transforms-test.appspot.com/'):
        self.url = url

    def process(self, vcf_chunk):
        start = vcf_chunk.count('\n')
        response = requests.post(self.url, data={'variants': vcf_chunk})
        try:
            data = response.json()
            if data['stderr']:
                raise ValueError(data['stderr'])
            result = data['stdout']
            end = result.count('\n')
            #print 'This chunk started with {} lines and ended with {}.'.format(start, end)
        except ValueError:
            #TODO (jessime) This should be more robust. We should look at the
            #text and decide what todo based on the text. For example:
            #if we get the 'wait 30s error, we should do that and try again.
            #If it the request size was too large, we can subdivide the string
            #and send multiple smaller requests. If it's a VEP error, then we
            #can actually abort. Or something like this.
            raise ValueError(response.text)
        yield result


def remove_header_lines(vcf):
    return [line for line in vcf.splitlines() if line[0] != '#']


def join_lines(kv):
    return '\n'.join(kv[1])


def run(infile, outfile, env):
    if env == 'd':
        options = {}
    elif env == 'p':
        options = {
            'runner': 'DataflowRunner',
            'num_workers': 50,
            'max_num_workers': 100,
            'project': 'gcp-variant-transforms-test',
            'staging_location': 'gs://jessime_test_bucket/staging',
            'temp_location': 'gs://jessime_test_bucket/temp',
            'job_name': 'vep-as-a-service8',
            'setup_file': './setup.py',
            'save_main_session': True}
    else:
        raise ValueError('env must be `d` (dev.) or `p` (prod.).')

    options = beam.options.pipeline_options.PipelineOptions(**options)
    with beam.Pipeline(options=options) as p:
        results = (p | beam.io.ReadFromText(infile)
                     | beam.ParDo(KeyGenFn())
                     | beam.GroupByKey()
                     | beam.Map(join_lines)
                     | beam.ParDo(Requester())
                     | beam.FlatMap(remove_header_lines))
        results | beam.io.WriteToText(outfile)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])
