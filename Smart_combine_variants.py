#!/usr/bin/env python
# coding: utf-8

"""
SmartCombineVariants (SCV) v1.0 made with Python by Zorana Štaka and Darko Pjević
This tools performs combining of two or more vcf files into one according to the perspective rules.
Copyright (c) ETF Beograd

Usage: Smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>]... [-f <output_format>] [-o <out>]

Options:
  -h --help

  -i,--input_file <inputVCF.vcf>                                        Input vcf file
  -s, --sample_name <sample_name>                                       Name of the sample(s) to be combined

  -f,--output_format <output_format>                                    Output file format:
                                                                        COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT

  -o,--out <out>                                                        Output file
"""

import time
from docopt import docopt
from Output_file import Output_file
import profile

start_time = time.time()
output_file = None

"""
    Collecting arguments from input line. 
    Create object of class Output_file.
"""

if __name__ == '__main__':
    arguments = docopt(__doc__)

    output_file = Output_file(arguments)

    output_file.read_input_files()

    print("--- %s seconds ---" % (time.time() - start_time))
