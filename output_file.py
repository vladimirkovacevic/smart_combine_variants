import os
import re
import toolz
import bgzip

from concurrent.futures import ThreadPoolExecutor
from body_header_line import Body_header_line
from body_record import Body_record
from input_file import Input_file


class Output_file:
    """ Represents the output file that will be generated by combining and merging all input files. """

    def __init__(self, arguments):
        self.path = None
        self.file = None
        self.compressed = None
        self.version = None
        self.keep_variants_different_format = False
        self.chromosomes_position = {}
        self.body_header_line = None
        self.list_of_header_objects = list()
        self.list_of_header_objects_without_ID = list()
        self.list_of_body_records_chrom = list()
        self.list_of_contigs = list()
        self.list_of_input_files_paths = list()
        self.list_of_input_files = list()
        self.list_of_samples_to_be_combined = list()
        self.arguments = arguments
        self.error_message = None
        self.invalid = None
        self.convert = lambda text: int(text) if text.isdigit() else text
        self.alphanum_key = lambda key: [self.convert(c) for c in re.split('([0-9]+)', key)]
        self.extract_info_from_arguments()

    def extract_info_from_arguments(self):
        """ Sets the attributes from respective user input parameters. """

        if self.arguments['--sample_name']:
            self.arguments['--sample_name'] = self.arguments['--sample_name'].split(',')
            for sample_name in self.arguments['--sample_name']:
                self.list_of_samples_to_be_combined.append(sample_name)

        if self.arguments['--out']:
            self.path = self.arguments['--out']

        for file_path in self.arguments['--input_file']:
            if not os.path.isfile(file_path):
                self.invalid = True
                self.error_message = f'No such file {file_path}.'
                return
            input_file = Input_file(file_path, self.list_of_samples_to_be_combined)
            self.list_of_input_files.append(input_file)
            self.list_of_input_files_paths.append(file_path)

        if self.arguments['--out']:
            self.path = self.arguments['--out']
            if self.arguments['--output_format'] == 'COMPRESSED':
                self.compressed = True
            elif self.arguments['--output_format'] == 'UNCOMPRESSED':
                self.compressed = False
            else:
                if self.list_of_input_files[0].compressed:
                    self.compressed = True
                else:
                    self.compressed = False

        if self.path:
            if self.compressed:
                if not (self.path.endswith(".vcf.gz") or self.path.endswith(".vcf.GZ")):
                    if self.path.endswith(".vcf"):
                        self.path += ".gz"
                    else:
                        self.path += ".vcf.gz"
            else:
                if self.path.endswith(".gz") or self.path.endswith(".GZ"):
                    self.path = self.path[:-3]

        if self.arguments['--keep_variants_with_different_format']:
            print("Trueeeeueueu")
            self.keep_variants_different_format = True

    def process_input_files(self):
        """ Processes input files, first it reads the header, then body part, taking into
            consideration the validity of input files. """
        self.read_header_in_input_files()
        self.check_if_input_file_invalid()
        if self.invalid is not True:
            self.process_headers()
            self.write_header_in_output_file()
            self.extract_chromosomes()
            self.check_samples_in_all_input_files()
            if self.invalid is not True:
                self.read_body_in_input_files_and_write()
                if self.invalid is not True:
                    self.check_if_input_file_invalid()

        if self.invalid is True:
            if self.path:
                if os.path.isfile(self.path):
                    os.remove(self.path)
            return False
        else:
            return True

    def read_header_in_input_files(self):
        """ Reads header parts of all input files and adds a list of certain objects into the appropriate lists. """
        for input_file in self.list_of_input_files:
            input_file.read_header_of_file()
            self.list_of_header_objects.extend(input_file.list_of_header_objects)
            self.list_of_header_objects_without_ID.extend(input_file.list_of_header_objects_without_ID)
            self.list_of_contigs.extend(input_file.list_of_contigs)
        self.version = self.list_of_input_files[0].version

    def extract_chromosomes(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            [executor.submit(self.extract_indices_for_chrom_in_file, input_file) for input_file in
             self.list_of_input_files]

    def extract_indices_for_chrom_in_file(self, input_file):
        input_file.extract_indices_for_chromosomes()
        self.chromosomes_position.update(input_file.chromosomes_positions)

    def process_headers(self):
        """ Delete duplicates and sort all lists regarding the header. Creates a body header line according to the
            samples. """
        self.list_of_header_objects = list(toolz.unique(self.list_of_header_objects, key=lambda x: x.tag_and_ID))
        self.list_of_header_objects_without_ID = list(
            toolz.unique(self.list_of_header_objects_without_ID, key=lambda x: x.line))
        self.list_of_contigs = list(toolz.unique(self.list_of_contigs, key=lambda x: x.line))
        self.list_of_header_objects.extend(self.list_of_header_objects_without_ID)
        self.list_of_header_objects.sort(key=lambda x: x.line)
        self.list_of_header_objects.extend(self.list_of_contigs)
        self.list_of_header_objects.sort(key=lambda x: x.tag, reverse=False)
        self.create_body_header_line_for_output()

    def read_body_in_input_files_and_write(self):
        """ Forms list of positions of chromosomes that need to be read from input files then reads one by one
            chromosome from all input files. After reading one chromosome in a file, the list containing information
            is updated. This list is then filtered to remove duplicates and sorted. Then the body records for specific
            chromosomes are written in the output file. """
        list_of_chrom = list(self.chromosomes_position.keys())
        list_of_chrom.sort(key=lambda x: self.alphanum_key(x))

        for chrom in list_of_chrom:
            self.list_of_body_records_chrom.clear()
            with ThreadPoolExecutor(max_workers=10) as executor:
                [executor.submit(self.multithread_test,input_file,chrom) for input_file in self.list_of_input_files]

            self.adjust_body_records_to_samples()
            self.list_of_body_records_chrom = list(toolz.unique(self.list_of_body_records_chrom, key=lambda x: x.line))
            self.list_of_body_records_chrom.sort(key=lambda x: self.alphanum_key(x.line))
            if self.verify_and_merge_body_records():
                self.write_specific_chrom_in_output_file()

    def multithread_test(self, input_file, chrom):
        input_file.read_specific_chrom_body_of_file(chrom)
        self.list_of_body_records_chrom.extend(input_file.list_of_body_records_chrom)

    def check_if_input_file_invalid(self):
        """ Checks whether the input files are all valid. If there is at least one invalid file the error message is
            set according to the invalid input file. """
        error_files = [input_file for input_file in self.list_of_input_files if input_file.invalid is True]
        if len(error_files) > 0:
            self.error_message = error_files[0].error_message
            self.invalid = True

    def write_header_in_output_file(self):
        """ Writes the header in the compressed or uncompressed output file. """
        if self.compressed:
            self.write_header_in_gz_file()
        else:
            self.write_header()

    def write_specific_chrom_in_output_file(self):
        """ Writes records for specific chromosomes in compressed or uncompressed output files. """
        if self.compressed:
            self.write_body_in_gz_file()
        else:
            self.write_body()

    def write_header(self):
        """ Writes header in uncompressed file, or on the stdout, regarding input arguments. """
        if self.path:
            self.file = open(self.path, "w+")
            self.file.write(self.version)
            for list_item in self.list_of_header_objects:
                self.file.write(list_item.line)
            self.file.write(self.body_header_line.line)
            self.file.close()
        else:
            print(self.version, end='')
            for list_item in self.list_of_header_objects:
                print(list_item.line, end='')
            print(self.body_header_line.line, end='')

    def write_body(self):
        """ Writes body in the uncompressed file, or on the stdout, regarding input arguments. """
        if self.path:
            self.file = open(self.path, "a+")
            for list_item in self.list_of_body_records_chrom:
                self.file.write(list_item.line)
            self.file.close()
        else:
            for list_item in self.list_of_body_records_chrom:
                print(list_item.line, end='')

    def write_header_in_gz_file(self):
        """ Writes header in the compressed file, or on the stdout, regarding input arguments. """
        if self.path:
            with open(self.path, "w+b") as raw:
                with bgzip.BGZipWriter(raw) as self.file:
                    self.file.write(self.version.encode('utf-8'))
                    for list_item in self.list_of_header_objects:
                        self.file.write(list_item.line.encode('utf-8'))
                    self.file.write(self.body_header_line.line.encode('utf-8'))
        else:
            for list_item in self.list_of_header_objects:
                print(list_item.line.encode('utf-8'))

    def write_body_in_gz_file(self):
        """ Writes body in the compressed file, or on the stdout, regarding input arguments. """
        if self.path:
            with open(self.path, "a+b") as raw:
                with bgzip.BGZipWriter(raw) as self.file:
                    for list_item in self.list_of_body_records_chrom:
                        self.file.write(list_item.line.encode('utf-8'))
        else:
            for list_item in self.list_of_body_records_chrom:
                print(list_item.line.encode('utf-8'))

    def adjust_body_records_to_samples(self):
        """ First make a list of samples that need to be combined if the list_of_samples_to_be_combined is empty.
            After that, each body record is adjusted to contain only the needed samples. """
        if len(self.list_of_samples_to_be_combined) == 0:
            self.determinate_samples_to_be_combined()
        Body_header_line.list_of_samples_to_be_combined = self.list_of_samples_to_be_combined
        Body_record.list_of_samples_to_be_combined = self.list_of_samples_to_be_combined
        for body_object in self.list_of_body_records_chrom:
            body_object.update_line()

    def create_body_header_line_for_output(self):
        """ Creates a body header line according to the samples. """
        if len(self.list_of_samples_to_be_combined) == 0:
            self.determinate_samples_to_be_combined()
        Body_header_line.list_of_samples_to_be_combined = self.list_of_samples_to_be_combined
        self.body_header_line = Body_header_line("")
        self.body_header_line.has_format_field = len(Body_header_line.list_of_samples_to_be_combined) > 0
        self.body_header_line.samples_names = Body_header_line.list_of_samples_to_be_combined
        self.body_header_line.update_line()

    def check_samples_in_all_input_files(self):
        for input_file in self.list_of_input_files:
            if not set(self.list_of_samples_to_be_combined).issubset(set(input_file.body_header_line.samples_names)):
                self.invalid = True
                self.error_message = f'The input file: {input_file.path} does not have all required samples: ' \
                                     f'{str(self.list_of_samples_to_be_combined)}'

    def determinate_samples_to_be_combined(self):
        """ If no samples are given as an input argument, determinate which samples need to be combined
            according to the samples in the input files. """
        for input_file in self.list_of_input_files:
            for sample_name in input_file.body_header_line.samples_names:
                if sample_name not in self.list_of_samples_to_be_combined:
                    self.list_of_samples_to_be_combined.append(sample_name)
        self.list_of_samples_to_be_combined = list(set(self.list_of_samples_to_be_combined))

    def verify_and_merge_body_records(self):
        """ Verifies if the body records are valid and merge where possible. """
        index = 0
        while index + 1 < len(self.list_of_body_records_chrom):
            if (self.check_condition_for_merging_records(self.list_of_body_records_chrom[index],
                                                         self.list_of_body_records_chrom[index + 1])):

                if self.list_of_body_records_chrom[index].ref == self.list_of_body_records_chrom[index + 1].ref:
                    self.list_of_body_records_chrom[index].id = self.determinate_id(
                        self.list_of_body_records_chrom[index].id, self.list_of_body_records_chrom[index + 1].id)

                    self.list_of_body_records_chrom[index].alt = self.determinate_alt(
                        self.list_of_body_records_chrom[index].alt, self.list_of_body_records_chrom[index + 1].alt)

                    self.list_of_body_records_chrom[index].qual = self.determinate_qual(
                        self.list_of_body_records_chrom[index].qual,
                        self.list_of_body_records_chrom[index + 1].qual)

                    self.determinate_info(self.list_of_body_records_chrom[index],
                                          self.list_of_body_records_chrom[index + 1])

                    self.list_of_body_records_chrom[index].update_line()

                    del self.list_of_body_records_chrom[index + 1]

                else:
                    index += 1
            else:
                index += 1

        return True

    def check_condition_for_merging_records(self, record_one, record_two):
        """ Checks whether mering conditions for two body records are fulfilled. """
        if record_one.pos == record_two.pos and record_one.chrom == record_two.chrom:
            if record_one.has_format_field and record_two.has_format_field:
                if record_one.format != record_two.format:
                    return not self.keep_variants_different_format
                else:
                    samples_data_record_one = (record_one.line.split('\t'))[8:]
                    samples_data_record_two = (record_two.line.split('\t'))[8:]

                    if len(samples_data_record_one) == len(samples_data_record_two):
                        index = 1
                        while index < len(samples_data_record_one):
                            if samples_data_record_one[index] != samples_data_record_two[index]:
                                return False
                            index += 1
            else:
                return True
        else:
            return False

    def determinate_info(self, record_one, record_two):
        """ Determinate merging info of two body records. """
        info_data = {}
        for key, value in record_one.data_from_info.items():
            if key in record_two.data_from_info:
                if value == record_two.data_from_info[key]:
                    info_data[key] = value
            else:
                info_data[key] = value

        for key, value in record_two.data_from_info.items():
            if key not in record_one.data_from_info:
                info_data[key] = value

        record_one.update_data_from_info(info_data)

    def determinate_id(self, id_one, id_two):
        """ Determinate merging id of two body records. """
        if id_one == id_two:
            return id_one
        if id_one == ".":
            return id_two
        if id_two == ".":
            return id_one
        return id_one + "," + id_two

    def determinate_qual(self, qual_one, qual_two):
        """ Determinate merging qual of two body records. """
        if qual_one == qual_two:
            return qual_one
        if qual_one == ".":
            return qual_two
        if qual_two == ".":
            return qual_one
        if float(qual_one) < float(qual_two):
            return qual_one
        return qual_one

    def determinate_alt(self, alt_one, alt_two):
        """ Determinate merging alt of two body records. """
        if alt_one == alt_two:
            return alt_one
        if alt_one == ".":
            return alt_two
        if alt_two == ".":
            return alt_one
        return alt_one + "," + alt_two
