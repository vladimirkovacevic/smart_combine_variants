# Smart Combine Variants

Python tool for smart combining of genomic variants

SmartCombineVariants (SCV) is a Python tool that performs combining variants of two VCF files. The tool supports the combining of VCF originating from different variant callers and with different headers. SCV should also support the combining of VCFs with multiple samples. When samples do not match it is possible to configure which samples will be combined through an input key-value parameter.
SCV performs merging of VCF headers. INFO and FORMAT VCF columns will also be bearged and its order maintained in alphabetical order. SCV preserves VCF standard of input VCF files and combined VCF is also according to the VCF standard of input files.

## Usage examples
```
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -f UNCOMPRESSED -o combined.vcf -v
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf -s NORMAL -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -s NORMAL -s TUMOR -f COMPRESSED -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -o combined.vcf -v
Smart_combine_variants.py -i data/test/v1.vcf.gz -i data/test/v2.vcf.gz -i v3.vcf -o combined.vcf
Smart_combine_variants.py -i data/test/v1.vcf    -i data/test/v2.vcf.gz -v
```

## Options and parameters
```
    smart_combine_variants.py (-i <inputVCF.vcf>)... [-s <sample_name>]... [-f <output_format>] [-o <out>] [options]

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

    -v,--verbose                        Printing test data to stderr [default: False]```
```

## Docker
SCV is available in Docker container (```docker pull cgc-images.sbgenomics.com/dpjevic/scv_2.0:latest```) built from [Dockerfile](https://github.com/vladimirkovacevic/smart_combine_variants/blob/master/Docker/Dockerfile). 
