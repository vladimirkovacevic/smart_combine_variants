#!/usr/bin/env python
# coding: utf-8


"""
SmartCombineVariants (SCV) v1.0 by Zorana Štaka and Darko Pjević
Copyright (c) ETF Beograd

Usage: Smart_combine_variants.py (-i <inputVCF.vcf>)... [-f <output_format>] [-o <out>]

Options:
  -h --help
  
  -i,--input_file <inputVCF.vcf>                                        Input vcf file 
  
  -f,--output_format <output_format>                                    Output file format:
                                                                        COMPRESSED, UNCOMPRESSED or SAME_AS_INPUT
  
  -o,--out <out>                                                        Output file

"""


import collections
import re
import time
import gzip
from docopt import docopt
from Input_file import Input_file
from Body_header_line import Body_header_line
from Body_record import Body_record
from Generic_header import Generic_header


"""
    Read all header lines in all files. 
    Delete all duplicates.
    After reading create objects type of Generic_header according to list_of_lines.
    
"""
 
def read_headers_in_files(file_item):
    previous_position_of_file = file_item.file.tell()
    line_of_file = file_item.file.readline()
        
    while line_of_file.startswith('##'):
          list_of_lines.append(line_of_file)
          previous_position_of_file = file_item.file.tell()
          line_of_file = file_item.file.readline()
            
    file_item.file.seek(previous_position_of_file)

"""
    Read all header lines in all compressed files. 
    Delete all duplicates.
    After reading create objects type of Generic_header according to list_of_lines.
    
"""
def read_headers_in_gz_files(file_item):
    previous_position_of_file = file_item.file.tell()
    line_of_file = str(file_item.file.readline(), 'utf-8')
        
    while line_of_file.startswith('##'):
        list_of_lines.append(line_of_file)
        previous_position_of_file = file_item.file.tell()
        line_of_file = str(file_item.file.readline(), 'utf-8')
            
    file_item.file.seek(previous_position_of_file)

"""
    Verify that there is no collision between records itself and other record with same chrom and pos.
    Will be more developed and more comprehensive, after testing all possible cases.
    
"""
def verify_records(list_of_body_objects):
    index = 0
    check_mutations = True
    while index < len(list_of_body_objects):
        
        #same referent and alternate base on the same mutation - then it is not a mutation
        if list_of_body_objects[index].ref == list_of_body_objects[index].alt:
            print("Error")

        if index + 1 < len(list_of_body_objects):
            #same pos and chromosome
            if(list_of_body_objects[index].pos == list_of_body_objects[index + 1].pos and
                list_of_body_objects[index].chrom == list_of_body_objects[index + 1].chrom and
                  list_of_body_objects[index].ref == list_of_body_objects[index + 1].ref):
        
                if list_of_body_objects[index].id == list_of_body_objects[index + 1].id:
                    if list_of_body_objects[index].alt == list_of_body_objects[index + 1].alt:
                        pass 
                        #to be continued
                
                    else:
                        list_of_body_objects[index].alt = list_of_body_objects[index].alt + "," + list_of_body_objects[index + 1].alt
                        list_of_body_objects[index].update_line()
                        del list_of_body_objects[index + 1]
                
                
                elif list_of_body_objects[index].id != '.' and list_of_body_objects[index + 1].id == '.':
                    
                    if list_of_body_objects[index].alt == list_of_body_objects[index + 1].alt:
                        pass
                        #to be continued
                
                    else:
                        list_of_body_objects[index].alt = list_of_body_objects[index].alt + "," + list_of_body_objects[index + 1].alt
                        list_of_body_objects[index].update_line()
                        
                    del list_of_body_objects[index + 1]
                        
                elif list_of_body_objects[index].id == '.' and list_of_body_objects[index + 1].id != '.':
                    list_of_body_objects[index].id = list_of_body_objects[index + 1].id
                    list_of_body_objects[index].update_line()
                    
                    if list_of_body_objects[index].alt == list_of_body_objects[index + 1].alt:
                        pass
                        #to be continued
                
                    else:
                        list_of_body_objects[index].alt = list_of_body_objects[index].alt + "," + list_of_body_objects[index + 1].alt
                        list_of_body_objects[index].update_line()
                        
                    del list_of_body_objects[index + 1]            
                
                elif list_of_body_objects[index].id != list_of_body_objects[index + 1].id:
                    list_of_body_objects[index].id = list_of_body_objects[index].id + "," + list_of_body_objects[index + 1].id
                    list_of_body_objects[index].update_line()
             
            elif(list_of_body_objects[index].pos == list_of_body_objects[index + 1].pos and
                list_of_body_objects[index].chrom == list_of_body_objects[index + 1].chrom and
                  list_of_body_objects[index].ref != list_of_body_objects[index + 1].ref):
                
                if len(list_of_body_objects[index].ref) == len(list_of_body_objects[index + 1].ref):
                    print("Error")
                    
                elif len(list_of_body_objects[index].ref) < len(list_of_body_objects[index + 1].ref):
                    if list_of_body_objects[index + 1].ref[0:len(list_of_body_objects[index].ref)] == list_of_body_objects[index].ref:
                        pass
                    else:
                        print("Error")
                        
                else:
                    if list_of_body_objects[index].ref[0:len(list_of_body_objects[index + 1].ref)] == list_of_body_objects[index + 1].ref:
                        pass
                    else:
                        print("Error")        
                    
        index += 1

"""
    Read all body lines in all files. 
    Delete all duplicates.
    After reading create objects type of Body_record according to list_of_lines.
    
"""
def read_bodies_in_files(list_of_body_lines, file_item):
    list_of_body_lines.clear()
    for line in file_item.file:
        list_of_body_lines.append(line)

"""
    Read all body lines in all compressed files. 
    Delete all duplicates.
    After reading create objects type of Body_record according to list_of_lines.
    
"""
def read_bodies_in_gz_files(list_of_body_lines, file_item):
    list_of_body_lines.clear()
    for line in file_item.file:    
        list_of_body_lines.append(str(line, 'utf-8'))

"""
    Sorting objects by line and writing objects in output file. 
    
"""
        
def write_header_in_file(list_of_lines):
    
    list_of_lines = sorted(set(list_of_lines))
    for list_item in list_of_lines:
        generic_header_object = Generic_header(list_item)
        list_of_header_objects.append(generic_header_object)
        
    list_of_header_objects.sort(key = lambda x : x.line)
    if compressed:
        for value in list_of_header_objects:
            merged_vcf_file.write(value.line.encode('utf-8'))
    else:
        for value in list_of_header_objects:
            merged_vcf_file.write(value.line)
         
    list_of_header_objects.clear()
    list_of_lines.clear() 


"""
    Sorting objects by chromosome and then by position and writing objects in output file. 
    
"""
def write_body_in_file(list_of_body_objects):

    if compressed:
        for value in list_of_body_objects:
            merged_vcf_file.write(value.line.encode('utf-8'))
    else:
        for value in list_of_body_objects:
            merged_vcf_file.write(value.line)
        

    list_of_body_objects.clear() 


def create_body_records_objects_and_verify(list_of_body_lines, file_item):
    list_of_body_lines = sorted(set(list_of_body_lines))
    for list_item in list_of_body_lines:
        body_object = Body_record(list_item, file_item)
        list_of_body_objects.append(body_object)

    list_of_body_objects.sort(key = lambda x : alphanum_key(x.line))
    list_of_body_lines.clear()
    verify_records(list_of_body_objects)

def verify_start_of_header(item):
    
    if item.compressed:
        next_line = str(item.file.readline(), 'utf-8')
    else:
        next_line = item.file.readline()
    if next_line.startswith("#CHROM"): 
        item.set_body_header_line(Body_header_line(next_line))
    else:
        return False

    return True

list_of_lines = list()
list_of_body_lines = list()
list_of_header_objects = list()
list_of_body_objects = list()
list_of_file_objects = list()
list_of_versions = [] 
compressed = False

start_time = time.time() 
        
convert = lambda text: int(text) if text.isdigit() else text
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 

"""
    If files are .vcf.gz then we need to read bytes and convert it to string
"""

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)
      
    for files in arguments['--input_file']:
        file_object = Input_file(files)
        list_of_file_objects.append(file_object)
    print(list_of_file_objects[0].compressed)   
    if not arguments['--out']:
        
        if arguments['--output_format'] == 'COMPRESSED':
            merged_vcf_file = gzip.open("merged.vcf.gz","w+b")
            compressed = True
        elif arguments['--output_format'] == 'UNCOMPRESSED':
            merged_vcf_file = open("merged.vcf","w+")
        else:
            if list_of_file_objects[0].compressed:
                merged_vcf_file = gzip.open("merged.vcf.gz","w+b")
                compressed = True
            else:
                merged_vcf_file = open("merged.vcf","w+")
    else:
        if arguments['--output_format'] == 'COMPRESSED':
            merged_vcf_file = gzip.open(arguments['--out']+'.gz',"r+b")
            compressed = True
        elif arguments['--output_format'] == 'UNCOMPRESSED':
            merged_vcf_file = open(arguments['--out'],"r+")
        else:
            if list_of_file_objects[0].compressed:
                merged_vcf_file = gzip.open(arguments['--out']+'.gz',"r+b")
                compressed = True
            else:
                merged_vcf_file = open(arguments['--out'],"r+")
            
    
    for file_item in list_of_file_objects:
        if file_item.compressed:
            with gzip.open(file_item.path) as file_item.file:
                
                previous_position_of_file = file_item.file.tell()
                line_of_file = (str(file_item.file.readline(), 'utf-8'))
                if line_of_file.startswith('##fileformat'):
                    list_of_versions.append(line_of_file)
                else:
                    file_item.file.seek(previous_position_of_file)
                read_headers_in_gz_files(file_item)
                if verify_start_of_header(file_item):
                    read_bodies_in_gz_files(list_of_body_lines, file_item)

            create_body_records_objects_and_verify(list_of_body_lines, file_item)
        
        elif not file_item.compressed:
            with open(file_item.path) as file_item.file:
                 
                previous_position_of_file = file_item.file.tell()
                line_of_file = file_item.file.readline()
                if line_of_file.startswith('##fileformat'):
                    list_of_versions.append(line_of_file)
                else:
                    file_item.file.seek(previous_position_of_file)
                read_headers_in_files(file_item)
                if verify_start_of_header(file_item):
                    read_bodies_in_files(list_of_body_lines, file_item)

            create_body_records_objects_and_verify(list_of_body_lines, file_item)
        else:
            print('Invalid input format!')
    
    
    if compressed :
        merged_vcf_file.write(list_of_versions[0].encode('utf-8')) 
    else:
        merged_vcf_file.write(list_of_versions[0])
                              
    write_header_in_file(list_of_lines)
    write_body_in_file(list_of_body_objects)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    

