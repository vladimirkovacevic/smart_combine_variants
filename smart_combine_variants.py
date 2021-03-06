#!/usr/bin/env python
# coding: utf-8

"""
SmartCombineVariants (SCV) v1.0 made with Python by Zorana Štaka and Darko Pjević
This tools performs combining of two or more vcf files into one according to the perspective rules.
Copyright (c) ETF Beograd

Usage: 
    smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>] [-f <output_format>] [-o <out>] [options]

Options:

    -h --help

    -i,--input_file <inputVCF.vcf>      Input vcf file

    -s,--sample_name <sample_name>      Name of the sample(s) to be combined. If no sample names have not been provided
                                        all input files have to have matching sample names (order is not important).
                                        If the sample name is provided it must be in all input files. Otherwise, the
                                        error will occur. Example: For VCF_1 with samples A, B, C and VCF_2 with samples
                                        C, D, E, to match A with D and B with E use string: A:D,B:E. To match C from
                                        both VCF files use only string C.

    -f,--output_format <output_format>  Output file format: COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT [default: SAME_AS_INPUT]

    -o,--out <out>                      Output file

    -v,--verbose                        Printing test data to stderr [default: False]

    -k,--keep_variants_with_different_format    Keep variants with same CHROM, POS, REF and ALT, but different format in the output file.

Example:
smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f UNCOMPRESSED -o combined.vcf -v
smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf -s NORMAL -o combined.vcf
smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL,TUMOR -f COMPRESSED -o combined.vcf
smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -o combined.vcf -v
smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -i v3.vcf -o combined.vcf -k
smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf.gz -v -k

"""

import time
from docopt import docopt
from output_file import Output_file
from sys import stderr


start_time = time.time()

if __name__ == '__main__':
    arguments = docopt(__doc__)

    output_file = Output_file(arguments)
    if output_file.invalid is True:
        print(output_file.error_message)

    elif output_file.process_input_files() is False:
        print(output_file.error_message)

    if arguments['--verbose']:
        print("--- %s seconds ---" % (time.time() - start_time), file=stderr)

    stderr.close()
