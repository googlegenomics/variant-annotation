import sys
import requests
from pprint import pprint
from tqdm import tqdm, trange

class Tests(object):

    def __init__(self, env):
        if env == 'd':
            self.url = 'http://127.0.0.1:8080/'
        elif env == 'p':
            self.url = 'https://gcp-variant-transforms-test.appspot.com/'
        else:
            raise ValueError('env must be `d` (dev.) or `p` (prod.).')

    def example1(self):
        """No payload"""
        return requests.get(self.url)

    def example2(self):
        """A single simple variant"""
        vcf = 'GRCh38_single.vcf'
        with open(vcf) as vcf:
            vcf = vcf.readlines()
        variant = vcf[-1]
        response = requests.post(self.url, data={'variants': variant})
        return response

    def example2_1(self):
        """A single simple variant in the request header"""
        vcf = 'GRCh38_single.vcf'
        with open(vcf) as vcf:
            vcf = vcf.readlines()
        variant = vcf[-1]
        response = requests.post(self.url, params={'variants': variant})
        return response

    def example3(self):
        """A single already annotated variant"""
        vcf = 'gnomad_vep3.vcf'
        with open(vcf) as vcf:
            vcf = vcf.readlines()
        variant = vcf[-1]
        response = requests.post(self.url, data={'variants': variant})
        return response

    def example4(self):
        """Multiple already annotated variants"""
        vcf = 'gnomad_vep3.vcf'
        with open(vcf) as vcf:
            vcf = vcf.readlines()
        variants = ''.join(vcf[-3:])
        #print variants
        response = requests.post(self.url, data={'variants': variants})
        return response

    def example5(self):
        """Timing many variants in a for loop"""
        vcf = 'valid-4.1-large.vcf'
        with open(vcf) as vcf:
            vcf = vcf.readlines()
        variants = [l for l in vcf if l[0] != '#']
        for v in tqdm(variants):
            response = requests.post(self.url, params={'variants': v})
        return response.update({'notes': 'Showing last response only.'})

    def example6(self):
        """Run whatever is currently going on in the `test` route."""
        return requests.get(self.url + 'test')

    def example7(self):
        """10s of Mbs of data in the request body"""
        vcf = '/usr/local/google/home/jessime/data/gnomad_genomes_chrX_head30M.vcf'
        vcf = '/usr/local/google/home/jessime/data/gnomad_genomes_GRCh37_chrX_head2500.vcf'
        with open(vcf) as vcf:
            vcf = vcf.read()
        print '~ request size (MB): ', len(vcf.encode('utf-8'))/float(1024**2)
        return requests.post(self.url, data={'variants': vcf})

    def example8(self):
        """Get headers"""
        return requests.get(self.url + 'headers')

    def run(self, n):
        response = getattr(self, 'example' + n)()
        try:
            data = response.json()
            if isinstance(data, dict):
                for key, value in data.iteritems():
                    print '{}:\n{}\n'.format(key, value)
            else:
                print data
        except ValueError:
            raise ValueError(response.text)

if __name__ == '__main__':
    tests = Tests(sys.argv[1])
    tests.run(sys.argv[2])
