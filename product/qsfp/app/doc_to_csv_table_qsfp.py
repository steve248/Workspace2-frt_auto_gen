#////////////////////////////////////////////////////////////////////
# Read and parse PDF file. Create one CSV file worksheet. (TBD: Then create perl style def file for Perl)
#///////////////////////////////////////////////////////////////////
# Description:
# Read PDF file, extract TABLE for memory map file.
# Then Create one CSV file
# (TBD Then use the CSV file as input, create perl style def file for Perl)
#
# Applicable:
#
# Date    : $Date$
# Revision: $Rev: 553 $
# Author  : $Author: steve.lin $
# ID      : $Id:$
#
#///////////////////////////////////////////////////////////////////
#// Reserved Copyright (C) 2013. Finisar Corporation
#///////////////////////////////////////////////////////////////////
#

import os
import sys
import re

formfactor_name_list = [ 'xfp', 'sfp', 'qsfp', 'cxp', 'topaz', 'cfp', 'boa_25', ]
csv_delimiter = ','

#NAdef text_list_to_csv_syntax(line_list):
#NA    """ Make the tab-delimited text line compatible with CSV syntax
#NA        - double quote the text in a cell if it contain a comma
#NA        - double quote the text in a cell if it contain any double quote, which should be duplicated itself
#NA        - Finally, change tab into comma (last)
#NA
#NA    paramter: the tab-delimited line list
#NA    Return: the line list
#NA
#NA    """
#NA    for line_idx in range(len(line_list)):
#NA        if any (z in line_list[line_idx] for z in (',', '"')):
#NA            # text includes one or more comma or double quote
#NA            tmp_list = line_list[line_idx].split('\t')
#NA            for tmp_str in tmp_list:
#NA                if any (z in tmp_str for z in (',', '"')):
#NA                    tmp_str = '"' + tmp_str.replace('"', '""') + '"'
#NA            line_list[line_idx] = ','.join(tmp_str)
#NA        else:
#NA            # text does not include comma nor double quote
#NA            line_list[line_idx] = line_list[line_idx].replace('\t', ',')
#NA    return line_list

def text_to_excessive_space_on_hyphen(this_line):
    # remove the space in 'xx- xx', or 'xx -xx'
    if any (z in this_line for z in ('- ', ' -')):
        this_line = this_line.replace('- ', '-').replace(' -', '-')
    return this_line


def text_to_csv_syntax(this_line):
    """ Make the tab-delimited text line compatible with CSV syntax
        - double quote the text in a cell if it contains a comma
        - double quote the text in a cell if it contains any double quote, which should be duplicated itself
        - double quote the text in a cell if it contains match symbol (+-*/)
        - Finally, change tab into comma (last)

    paramter: the tab-delimited line list
    Return: the line list

    """

    date_key_list = ['-', '/']
    csv_key_list = [',', '"']

#    need_enclosure = False
#    if any (z in this_line for z in csv_key_list ) or any (z in this_line for z in date_key_list ):
#        # text includes one or more comma or double quote
#        need_enclosure = True
#
#    elif re.search('^\d{1,2}[-/]\d{1,2}$', this_line):
#        # contain only at most 2 digit before and after - or /
#        need_enclosure = True
#
#        DEBUG_date = True
#        if DEBUG_date: header = '>>>DEBUG_date:\t'
#        if DEBUG_date: print header, this_line.strip()
#
#    else:
#        need_enclosure = False
#    
#    if need_enclosure:
    if any (z in this_line for z in csv_key_list ) or any (z in this_line for z in date_key_list ):
        # text includes one or more comma or double quote, or date format key
        tmp_list = this_line.split('\t')
        for idx in range(len(tmp_list)):
            tmp_str = tmp_list[idx]

            if '"' in tmp_str:
                # text includes one or more comma or double quote
                tmp_str = tmp_str.replace('"', '""') # add space after the leading double quote to avoid EXCEL treat the cell as Date format
                tmp_str = '"' + tmp_str + '"'
            elif re.search('^\d{1,2}[-/]\d{1,2}$', tmp_str):
                DEBUG_date = False
                if DEBUG_date: header = '>>>DEBUG_date:\t'

                # text is in date format 'nn-nn' or 'nn/nn'
                matchobj1 = re.search('^(\d{1,2})[-/](\d{1,2})$', tmp_str)
                if 1<= int(matchobj1.group(1)) <= 12 and 1 <= int(matchobj1.group(2)) <=31:
                    tmp_str = ' ' + tmp_str # add space before the date-formated text to avoid EXCEL treats the text as Date format
                    if True:
                        tmp_str = '"' + tmp_str + '"' # double quote optional

                    if DEBUG_date: print header, True, this_line.strip()
                else:
                    pass
                    if DEBUG_date: print header, False, this_line.strip()

            tmp_list[idx] = tmp_str
        this_line = ','.join(tmp_list)
    else:
        # text does not include comma , double quote, nor math operator
        this_line = this_line.replace('\t', ',')
    return this_line


    csv_key_list = [',', '"', '+', '-', '*', '/']
    if any (z in this_line for z in csv_key_list ):
        # text includes one or more comma or double quote
        tmp_list = this_line.split('\t')
        for idx in range(len(tmp_list)):
            tmp_str = tmp_list[idx]

            if any (z in tmp_str for z in csv_key_list):
                #tmp_str = '"' + tmp_str.replace('"', '""') + '"'
                tmp_str = '"' + ' ' + tmp_str.replace('"', '""') + '"' # add space after the leading double quote to avoid EXCEL treat the cell as Date format
                tmp_list[idx] = tmp_str
        this_line = ','.join(tmp_list)
    else:
        # text does not include comma , double quote, nor math operator
        this_line = this_line.replace('\t', ',')
    return this_line


def extract_table_1(first_line_idx, lineIN_list):
    """ For QSFP PDF conly
    """ 
    DEBUG_1A = False
    if DEBUG_1A: header_1A = '>>>DEBUG_1A:\t'

    DEBUG_1 = False
    if DEBUG_1: header = '>>>DEBUG_1:\t'
    if DEBUG_1: print header, 'first_line_idx', first_line_idx 
    if DEBUG_1: from pprint import pprint as pp
    my_lineOUT_list = []
    my_lineIN_list = []

    #OBS header_of_the_table = 'Parameter'
    cell0_without_tab_list = [
        'Time bus',
        'Input Rise Time',
        'Input Fall Time',
        'Serial Interface Clock',
        ]
    tab_within_cell_list = [
        'Clock', 
        'Holdoff',
        ]


    for line_idx in range(first_line_idx+1, len(lineIN_list) ):
        #if lineIN_list[line_idx].startswith('Parameter'):
        #    my_lineIN_list.append(lineIN_list[line_idx].strip().replace(' ', csv_delimiter)) # CSV delimiter
        #    continue

        this_line = lineIN_list[line_idx].rstrip('\n') # strip EOL only, not other whtite space
        #this_line = lineIN_list[line_idx].replace('\n', '') # strip EOL
        #this_line = lineIN_list[line_idx].rstrip()

        #TMP if DEBUG_1: print
        #TMP if DEBUG_1: print header, '%3d: 1000, this_line\t(%s)'%(line_idx, this_line)
        #TMP if DEBUG_1: print header, '%3d: len(this_line)\t(%s)'%(line_idx, len(this_line))
        #TMP if DEBUG_1: print header, '%3d: len(my_lineIN_list)\t(%s)'%(line_idx, len(my_lineIN_list))
        #TMP if DEBUG_1A and 'Time bus' in this_line: print header_1A, '%3d: 1000, this_line\t(%s)'%(line_idx, this_line)

        # Fix unwantted tab in original PDF file: replace unwanted tab into a space
        for tmp_str in tab_within_cell_list:
            this_line = this_line.replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        if len(this_line) != 0:
            try:
                header_of_the_table 
            except NameError:
                header_of_the_table = re.sub('\t.*', '', this_line) # extract only the first cell
            my_lineIN_list.append(this_line)
        else:
            # The table itself is between 2 blank lines
            if len(my_lineIN_list) != 0:
                break

    # Make the text line compatible with CSV syntax
    line_idx = 0
    while line_idx < len(my_lineIN_list):
        this_line = my_lineIN_list[line_idx]
        this_delimiter_count = this_line.count('\t')

        if DEBUG_1: print header, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)
        if DEBUG_1A and 'Time bus' in this_line: print header_1A, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)

        if this_line.startswith(header_of_the_table):
            # header of the table
            delimiter_count = this_delimiter_count
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)

        else:
            # Get one or more line until enough cells: 
            if DEBUG_1A and 'Time bus' in this_line: print header_1A, '%3d: 2400, this_line\t(%s)'%(line_idx, this_line)

            while this_line.count('\t') < delimiter_count:
                if DEBUG_1A and 'Time bus' in this_line: print header_1A, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                # append next line
                if line_idx+1 < len(my_lineIN_list):
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_1: print header, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                    if DEBUG_1A and 'Time bus' in this_line: print header_1A, '%3d: 4000, this_line\t(%s)'%(line_idx, this_line)
                else:
                    break

            # Has enough cells: append one or more line if these line has no tab except 
            # the line start with a specific text
            while line_idx+1 < len(my_lineIN_list) and not '\t' in my_lineIN_list[line_idx+1]:
                if any (z in my_lineIN_list[line_idx+1] for z in cell0_without_tab_list):
                    break
                else:
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_1: print header, '%3d: 4000, this_line\t(%s)'%(line_idx, this_line)
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)
        line_idx += 1

    #if DEBUG_1: pp(my_lineOUT_list)
    if DEBUG_1: 
         for str2 in my_lineOUT_list:
             if DEBUG_1: print header, 'str2(%r)'%(str2)

    return my_lineOUT_list

def extract_table_2(first_line_idx, lineIN_list):
    """ For QSFP PDF conly
    """ 
    DEBUG_2 = False
    if DEBUG_2: header = '>>>DEBUG_2:\t'
    if DEBUG_2: print header, 'first_line_idx', first_line_idx 
    if DEBUG_2: from pprint import pprint as pp
    my_lineOUT_list = []
    my_lineIN_list = []

    #OBS header_of_the_table = 'Parameter'
    cell0_without_tab_list = [
        'Endurance',
        ]
    tab_within_cell_list = [
        ]

    for line_idx in range(first_line_idx+1, len(lineIN_list) ):

        this_line = lineIN_list[line_idx].rstrip('\n') # strip EOL only, not other whtite space

        #TMP if DEBUG_2: print
        #TMP if DEBUG_2: print header, '%3d: 1000, this_line\t(%s)'%(line_idx, this_line)
        #TMP if DEBUG_2: print header, '%3d: len(this_line)\t(%s)'%(line_idx, len(this_line))
        #TMP if DEBUG_2: print header, '%3d: len(my_lineIN_list)\t(%s)'%(line_idx, len(my_lineIN_list))

        # Fix unwantted tab in original PDF file: replace unwanted tab into a space
        for tmp_str in tab_within_cell_list:
            this_line = this_line.replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        if len(this_line) != 0:
            try:
                header_of_the_table 
            except NameError:
                header_of_the_table = re.sub('\t.*', '', this_line) # extract only the first cell
            my_lineIN_list.append(this_line)
        else:
            # The table itself is between 2 blank lines
            if len(my_lineIN_list) != 0:
                break 

    # Make the text line compatible with CSV syntax
    line_idx = 0
    while line_idx < len(my_lineIN_list):
        this_line = my_lineIN_list[line_idx]
        this_delimiter_count = this_line.count('\t')

        if DEBUG_2: print header, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)

        if this_line.startswith(header_of_the_table):
            # header of the table
            delimiter_count = this_delimiter_count
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)

        else:
            # Get one or more line until enough cells: 

            while this_line.count('\t') < delimiter_count:
                # append next line
                if line_idx+1 < len(my_lineIN_list):
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_2: print header, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                else:
                    break

            # Has enough cells: append one or more line if these line has no tab except 
            # the line start with a specific text
            while line_idx+1 < len(my_lineIN_list) and not '\t' in my_lineIN_list[line_idx+1]:
                if any (my_lineIN_list[line_idx+1].startswith(z) for z in cell0_without_tab_list):
                    break
                else:
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_2: print header, '%3d: 4000, this_line\t(%s)'%(line_idx, this_line)
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)
        line_idx += 1

    #if DEBUG_2: pp(my_lineOUT_list)
    if DEBUG_2: 
        for str2 in my_lineOUT_list: print header, 'str2(%r)'%(str2)
    return my_lineOUT_list

    
def extract_table_3(first_line_idx, lineIN_list):
    """ For QSFP PDF conly
    """ 
    DEBUG_3 = False
    if DEBUG_3: header = '>>>DEBUG_3:\t'
    if DEBUG_3: print header, 'first_line_idx', first_line_idx 
    if DEBUG_3: from pprint import pprint as pp
    my_lineOUT_list = []
    my_lineIN_list = []

    cell0_without_tab_list = [
        ]
    tab_within_cell_list = [
        ]

    for line_idx in range(first_line_idx+1, len(lineIN_list) ):
        this_line = lineIN_list[line_idx].rstrip('\n') # strip EOL only, not other whtite space

        # Fix unwantted tab in original PDF file: replace unwanted tab into a space
        for tmp_str in tab_within_cell_list:
            this_line = this_line.replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        if len(this_line) != 0:
            try:
                header_of_the_table 
            except NameError:
                header_of_the_table = re.sub('\t.*', '', this_line) # extract only the first cell
            my_lineIN_list.append(this_line)
        else:
            # The table itself is between 2 blank lines
            if len(my_lineIN_list) != 0:
                break

    # Make the text line compatible with CSV syntax
    line_idx = 0
    while line_idx < len(my_lineIN_list):
        this_line = my_lineIN_list[line_idx]
        this_delimiter_count = this_line.count('\t')

        if DEBUG_3: print header, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)

        if this_line.startswith(header_of_the_table):
            # header of the table
            delimiter_count = this_delimiter_count
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)

        else:
            # Get one or more line until enough cells: 
            while this_line.count('\t') < delimiter_count:
                # append next line
                if line_idx+1 < len(my_lineIN_list):
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_3: print header, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                else:
                    break

            # Has enough cells: append one or more line if these line has no tab except 
            # the line start with a specific text
            while line_idx+1 < len(my_lineIN_list) and not '\t' in my_lineIN_list[line_idx+1]:
                if any (my_lineIN_list[line_idx+1].startswith(z) for z in cell0_without_tab_list):
                    break
                else:
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_3: print header, '%3d: 4000, this_line\t(%s)'%(line_idx, this_line)
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)
        line_idx += 1

    if DEBUG_3:
        for str2 in my_lineOUT_list: print header, 'str2(%r)'%(str2)
    return my_lineOUT_list
    
def extract_table_4(first_line_idx, lineIN_list):
    """ For QSFP PDF conly
    """ 
    DEBUG_4 = False
    if DEBUG_4: header = '>>>DEBUG_4:\t'
    if DEBUG_4: print header, 'first_line_idx', first_line_idx 
    if DEBUG_4: from pprint import pprint as pp
    my_lineOUT_list = []
    my_lineIN_list = []

    cell0_without_tab_list = [
        ]
    tab_within_cell_list = [
        ]

    for line_idx in range(first_line_idx+1, len(lineIN_list) ):
        this_line = lineIN_list[line_idx].rstrip('\n') # strip EOL only, not other whtite space

        # Fix unwantted tab in original PDF file: replace unwanted tab into a space
        for tmp_str in tab_within_cell_list:
            this_line = this_line.replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        if len(this_line) != 0:
            try:
                header_of_the_table 
            except NameError:
                header_of_the_table = re.sub('\t.*', '', this_line) # extract only the first cell
            my_lineIN_list.append(this_line)
            if DEBUG_4: print header, '%3d: 1900, header_of_the_table\t(%s)'%(line_idx, header_of_the_table)
        else:
            # The table itself is between 2 blank lines
            if len(my_lineIN_list) != 0:
                break

    # Make the text line compatible with CSV syntax
    line_idx = 0
    while line_idx < len(my_lineIN_list):
        this_line = my_lineIN_list[line_idx]
        this_delimiter_count = this_line.count('\t')

        if DEBUG_4: print header, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)

        if this_line.startswith(header_of_the_table):
            # header of the table
            delimiter_count = this_delimiter_count
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)

        else:
            # Get one or more line until enough cells: 
            while this_line.count('\t') < delimiter_count:
                # append next line
                if line_idx+1 < len(my_lineIN_list):
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_4: print header, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                else:
                    break

            # Has enough cells: append one or more line if these line has no tab except 
            # the line start with a specific text
            while line_idx+1 < len(my_lineIN_list) and not '\t' in my_lineIN_list[line_idx+1]:
                if DEBUG_4: print header, '%3d: 3900, this_line\t(%s)'%(line_idx, this_line)
                #if any (my_lineIN_list[line_idx+1].startswith(z) for z in cell0_without_tab_list):
                if len(cell0_without_tab_list) >0 and any (my_lineIN_list[line_idx+1].startswith(z) for z in cell0_without_tab_list):
                    break
                else:
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_4: print header, '%3d: 4000, this_line\t(%s)'%(line_idx, this_line)
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)
        line_idx += 1

    if DEBUG_4:
        for str2 in my_lineOUT_list: print header, 'str2(%r)'%(str2)
    return my_lineOUT_list
    
def extract_table_byte_table(first_line_idx, lineIN_list):
    """ For QSFP PDF conly
    """ 
    DEBUG_byte_table = False
    if DEBUG_byte_table: header = '>>>DEBUG_byte_table:\t'
    if DEBUG_byte_table: print header, 'first_line_idx', first_line_idx 
    if DEBUG_byte_table: from pprint import pprint as pp
    my_lineOUT_list = []
    my_lineIN_list = []

    #OBS header_of_the_table = 'Bytes'
    cell0_without_tab_list = [
        ['17', '105-'],
        ['18', '111-'],
        ['19', '131-'],
        ['19', '148-'],
        ['19', '165-'],
        ['19', '168-'],
        ['19', '184-'],
        ['19', '186-'],
        ['19', '188-'],
        ['19', '193-'],
        ['19', '196-'],
        ['19', '212-'],
        ['19', '224-'],
        ['34', '128-'],
        ['34', '130-'],
        ['34', '132-'],
        ['34', '134-'],
        ['34', '136-'],
        ['34', '144-'],
        ['34', '146-'],
        ['34', '148-'],
        ['34', '150-'],
        ['34', '152-'],
        ['34', '160-'],
        ['34', '176-'],
        ['34', '178-'],
        ['34', '180-'],
        ['34', '182-'],
        ['34', '184-'],
        ['34', '186-'],
        ['34', '188-'],
        ['34', '190-'],
        ['34', '192-'],
        ['34', '194-'],
        ['34', '196-'],
        ['34', '198-'],
        ['34', '200-'],
        ['34', '208-'],
    ]
    tab_within_cell_list = [
        ] 
    merged_cell_list = [
        # text in this cell is merged cells
        '\tSee Table',
        '\t-',
        ] 
    #unwanted_line_list = [
        #['19', 'Base ID fields'],
        #['19', 'Extended ID fields'],
        #['19', 'Vendor Specific ID fields'],
    #]
    #ignore_blank_line = [
    #    '13',
    #]

 
    DEBUG0 = False
    if DEBUG0: header0 = '>>>DEBUG0:\t'
    if DEBUG0: 
        start_line = 1720
        end_line = start_line + 100
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print header0, '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, lineIN_list[line_idx].rstrip())
            #if new_lineIN_list[line_idx].startswith('255\t'):
            #    break

    DEBUG1 = False
    if DEBUG1: header1 = '>>>DEBUG1:\t'

    for line_idx in range(first_line_idx+1, len(lineIN_list) ):

        #this_line = lineIN_list[line_idx]
        #if DEBUG1: print header1, 1000, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)

        #this_line = lineIN_list[line_idx].replace('\n', '') # strip EOL only, not other whtite space
        #if DEBUG1: print header1, 1002, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)

        this_line = lineIN_list[line_idx].rstrip('\n') # strip EOL only, not other whtite space
        #if DEBUG1: print header1, 1004, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)

        if DEBUG1: print header1, 1000, 'This table: len(my_lineIN_list)(%d)'%(len(my_lineIN_list))

        # Fix unwantted tab in original PDF file: replace unwanted tab into a space
        for tmp_str in tab_within_cell_list:
            if DEBUG1: print header1, 1500, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)
            this_line = this_line.replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        if len(this_line) != 0:
        #if re.search('^ *$', this_line): # look for zero or more space, but do not touch the tab
            if DEBUG1: print header1, 2000, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)
            try:
                header_of_the_table 
                if DEBUG1: print header1, 2100, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)
            except NameError:
                header_of_the_table = re.sub('\t.*', '', this_line) # extract only the first cell
                if DEBUG1: print header1, 2200, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)

            # Ignore unwanted line within a table
            #for this_table, this_value in unwanted_line_list:
            #    if this_table in lineIN_list[first_line_idx] and this_value in this_line:
            #        if DEBUG_byte_table: print header, 'SKIPPED %3d: 2000, this_line\t(%s)'%(line_idx, this_line)
            #        pass
            #    else:
            #        my_lineIN_list.append(this_line)
            my_lineIN_list.append(this_line)
        else:
            # The table itself is between 2 blank lines, except TABLE 13
            #if any(this_table in lineIN_list[first_line_idx] for this_table in ignore_blank_line):
            #    if '13' in lineIN_list[first_line_idx]:
            #        my_lineIN_list.append('\t') # line for bit 0 has a missing trailing tab
            #        pass

            # The table itself is between 2 blank lines
            if DEBUG1: print header1, 6000, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)
            if len(my_lineIN_list) != 0:
                if DEBUG1: print header1, 6400, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)
                break
            if DEBUG1: print header1, 6600, 'line_idx(%d). (this_line)(%s)'%(line_idx, this_line)

    DEBUG2 = False
    if DEBUG2: header2 = '>>>DEBUG2:\t'
    if DEBUG2: 
        print header2, 'This table: len(my_lineIN_list)(%d)'%(len(my_lineIN_list))
        for line_idx in range(len(my_lineIN_list)):
            print header2, 'my_lineIN_list[%d](%s):'%(line_idx, my_lineIN_list[line_idx])

    # Make the text line compatible with CSV syntax
    line_idx = 0
    while line_idx < len(my_lineIN_list):
        this_line = my_lineIN_list[line_idx]
        this_delimiter_count = this_line.count('\t')

        if DEBUG_byte_table: print
        if DEBUG_byte_table: print header, '%3d: 2000, this_line\t(%s)'%(line_idx, this_line)

        if this_line.startswith(header_of_the_table):
            #if DEBUG_byte_table: print header, '%3d: 2010, this_line\t(%s)'%(line_idx, this_line)
            # header of the table
            delimiter_count = this_delimiter_count
            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)

        else:
            #if DEBUG_byte_table: print header, '%3d: 2020, this_line\t(%s)'%(line_idx, this_line)
            # Get one or more line until enough cells: 
            while this_line.count('\t') < delimiter_count:
                # append next line
                if line_idx+1 < len(my_lineIN_list):
                    if DEBUG_byte_table: print header, '%3d: 2035, my_lineIN_list[line_idx+1]\t(%s)'%(line_idx, my_lineIN_list[line_idx+1])
                    #if any(my_lineIN_list[line_idx+1].startswith(z) for z in (merged_cell_list)):
                    if any(z in my_lineIN_list[line_idx] for z in (merged_cell_list)):
                        if DEBUG_byte_table: print header, '%3d: 2040, this_line\t(%s)'%(line_idx, this_line)
                        break # Done because a line with merged cell has less total number of cells 
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]

                    if DEBUG_byte_table: print header, '%3d: 3000, this_line\t(%s)'%(line_idx, this_line)
                else:
                    break

            # Has enough cells: append one or more line if these line has no tab except 
            # the line start with a specific text
            while line_idx+1 < len(my_lineIN_list) and not '\t' in my_lineIN_list[line_idx+1]:
                #if any (my_lineIN_list[line_idx+1].startswith(z) for tbl, z in cell0_without_tab_list):

                DEBUG_4 = False
                if DEBUG_4: header = '>>>DEBUG_4:\t'
                if DEBUG_4:
                    pass
                    #if any (this_table in lineIN_list[first_line_idx] and my_lineIN_list[line_idx+1].startswith(z) for this_table, z in cell0_without_tab_list):
                    #print header, cell0_without_tab_list
                    print header, cell0_without_tab_list
                    #print header, for this_table, z in cell0_without_tab_list):
                    #print header, if any (this_table in lineIN_list[first_line_idx] and my_lineIN_list[line_idx+1].startswith(z) for this_table, z in cell0_without_tab_list):
                    for this_table, z in cell0_without_tab_list:
                        print header, 'this_table(%r), z(%r), lineIN_list[first_line_idx](%r), my_lineIN_list[line_idx+1](%r)'%(this_table, z, lineIN_list[first_line_idx], my_lineIN_list[line_idx+1]),
                        print this_table in lineIN_list[first_line_idx] and my_lineIN_list[line_idx+1].startswith(z)


                if any (this_table in lineIN_list[first_line_idx] and my_lineIN_list[line_idx+1].startswith(z) for this_table, z in cell0_without_tab_list):
                    break
                else:
                    line_idx += 1
                    this_line += ' ' + my_lineIN_list[line_idx]
                    if DEBUG_byte_table: print header, '%3d: 4020, this_line\t(%s)'%(line_idx, this_line)
                    if DEBUG_byte_table: print header, '%3d: 4030, text appended\t(%s)'%(line_idx, my_lineIN_list[line_idx])

            this_line = text_to_csv_syntax(this_line) # text line compatible with CSV syntax
            this_line = text_to_excessive_space_on_hyphen(this_line) # remove the space in 'xx- xx', or 'xx -xx'
            my_lineOUT_list.append(this_line)
        if DEBUG_byte_table: print header, '%3d: 9999, my_lineOUT_list[-1]\t(%s)'%(line_idx, my_lineOUT_list[-1])
        line_idx += 1

    if DEBUG_byte_table:
        for str2 in my_lineOUT_list: print header, 'str2(%r)'%(str2)
    return my_lineOUT_list
    
def fix_lineIN_list_space_only(org_lineIN_list):
    # Remove the space from a space-only line
    new_lineIN_list = []

    for line_idx in range(len(org_lineIN_list) ):
        DEBUG_space_only = False
        if DEBUG_space_only: header = '>>>DEBUG_space_only:\t'
        if DEBUG_space_only: 
            if re.search('^ +$', org_lineIN_list[line_idx]):
                tmp_len = len(org_lineIN_list[line_idx].rstrip('\n'))
                print header, 'line_idx-1(%d)len(%d)(%s)'%(line_idx-1, tmp_len, org_lineIN_list[line_idx-1].rstrip('\n'))
                print header, 'line_idx(%d)len(%d)(%s)'%(line_idx, tmp_len, org_lineIN_list[line_idx].rstrip('\n'))
                print header, 'line_idx+1(%d)len(%d)(%s)'%(line_idx+1, tmp_len, org_lineIN_list[line_idx+1].rstrip('\n'))
                print 

        new_lineIN_list.append(re.sub('^ +$', '', org_lineIN_list[line_idx]))

    return new_lineIN_list

def fix_lineIN_list_table_10(org_lineIN_list):

    new_lineIN_list = []

    # Fix missing the line for specifying TABLE 10 
    in_table_10 = False
    in_table_9 = False
    need_table_10_header = True
    tab_within_cell_list = [
        'channel',
        'High',
        ]

    for line_idx in range(len(org_lineIN_list) ):
        # Fix the text files before we process it
        # details: TBD
        if False:
            if org_lineIN_list[line_idx].startswith('TABLE 9'):
                print '>>>> org_lineIN_list[line_idx]', org_lineIN_list[line_idx]

        if org_lineIN_list[line_idx].startswith('TABLE'):
            if org_lineIN_list[line_idx].startswith('TABLE 9'):
                in_table_9 = True
            else:
                in_table_9 = False
            #new_lineIN_list.append(org_lineIN_list[line_idx])

        if False: #True:
            if in_table_9: print '>>>> org_lineIN_list[line_idx]', org_lineIN_list[line_idx]
        if in_table_9 and re.search('^8\t', org_lineIN_list[line_idx]):
            new_lineIN_list.append(org_lineIN_list[line_idx])
            new_lineIN_list.append('\n')
            new_lineIN_list.append('TABLE 10 - CHANNEL MONITOR INTERRUPT FLAGS (PAGE 00H BYTES 9-21)\n')
            #print '>>>> new_lineIN_list[-1]', new_lineIN_list[-1]
            new_lineIN_list.append('\n')
            in_table_10 = True
            continue

        # For table 10, we take only 1 header and ignore blank lines within the table
        if in_table_10:
            if re.search('^Byte\t', org_lineIN_list[line_idx]):
                if need_table_10_header:
                    new_lineIN_list.append(org_lineIN_list[line_idx]) # append the header once
                    need_table_10_header = False
            #elif len(org_lineIN_list[line_idx]) == 1:
            elif org_lineIN_list[line_idx].strip() == '':
                pass # ignore the space
            elif re.search('^21\t', org_lineIN_list[line_idx]):
                # Table 10 ends on byte 21
                new_lineIN_list.append(org_lineIN_list[line_idx]) # append the header once
                new_lineIN_list.append('\n')
                in_table_10 = False
            else:
                new_lineIN_list.append(org_lineIN_list[line_idx])
            # Fix unwantted tab in original PDF file: replace unwanted tab into a space
            for tmp_str in tab_within_cell_list:
                new_lineIN_list[-1] = new_lineIN_list[-1].replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

#        if in_table_10 and re.search('^Byte\t', org_lineIN_list[line_idx]):
#            if need_table_10_header:
#                new_lineIN_list.append(org_lineIN_list[line_idx]) # append the header once
#                need_table_10_header = False
#        elif in_table_10 and len(org_lineIN_list[line_idx]) == 1:
#            pass # ignore the space
#        elif in_table_10 and re.search('^21\t', org_lineIN_list[line_idx]):
#            # Table 10 ends on byte 21
#            new_lineIN_list.append(org_lineIN_list[line_idx]) # append the header once
#            new_lineIN_list.append('\n')
#            in_table_10 = False
#        else:
#            new_lineIN_list.append(org_lineIN_list[line_idx])

    if False:
        for line_idx in range(1239, 1350): # len(new_lineIN_list) ):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())

    return new_lineIN_list

def fix_lineIN_list_table_13(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        #if org_lineIN_list[line_idx].startswith('TABLE 13'):
        if 'TABLE 13' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        if '* For the case' in org_lineIN_list[line_idx]:
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if '99\tAll' in new_lineIN_list[-1]:
                # byte 99 is the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                break
            else:
                #NA# the blank line is missing tab
                #NAnew_lineIN_list.append('\t')

                pass # discard the blank line
        elif re.search('\tChannel \d+ MSB', org_lineIN_list[line_idx]):
                # orphaned line in cell3 on certain line when crossing page break

                # remove leading and trailing white space
                # and sequeeze into the 'Tx\t'
                new_lineIN_list[-1] = new_lineIN_list[-1].replace('Tx\t',
                'Tx %s\t'%(org_lineIN_list[line_idx].strip()))
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            #if new_lineIN_list[line_idx].startswith('TABLE 13'):
            if 'TABLE 13' in new_lineIN_list[line_idx]:
                start_line = line_idx
            elif new_lineIN_list[line_idx].startswith('99\tAll'):
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())
            if new_lineIN_list[line_idx].startswith('99\tAll'):
                break

    return new_lineIN_list

def fix_lineIN_list_table_17(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '106\tAll'
    broken_row = [
        '\tFault Mask'
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        #if org_lineIN_list[line_idx].startswith('TABLE 17'):
        if 'TABLE 17' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        DEBUG = False
        if DEBUG:
            print 'YYYY', line_idx, org_lineIN_list[line_idx].strip()

        #NAif '* For the case' in org_lineIN_list[line_idx]:
        #NA    pass # discard this line
        if org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # byte 106 is the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                break
            else:
                #NA# the blank line is missing tab
                #NAnew_lineIN_list.append('\t')

                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                # orphaned line in cell3 on certain line when crossing page break

                # remove leading and trailing white space and sequeeze into the correct cells
                tmp_list = org_lineIN_list[line_idx].strip().split('\t')
                new_lineIN_list[-1] = new_lineIN_list[-1].replace('EQ\t', 'EQ %s\t'%(tmp_list[0]) )
                new_lineIN_list[-1] = new_lineIN_list[-1].replace('TX,\t', 'TX, %s\t'%(tmp_list[1]) )
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def fix_lineIN_list_table_19(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []
    DEBUG = False
    if DEBUG:
        print 'XXXX', 'len(org_lineIN_list)', len(org_lineIN_list)

    last_row = '255\t'
    broken_row = [
    ]

    line_to_be_discarded = [
        'Base ID fields',
        'Extended ID fields',
        #'Vendor Specifid ID fields',
        'Vendor Specific ID Fields',
        '* A value of zero',
        'specified technology',
    ]
    tab_within_cell_list = [
        'side device',
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        #if org_lineIN_list[line_idx].startswith('TABLE 19'):
        if 'TABLE 19' in org_lineIN_list[line_idx]:
            break
        if DEBUG:
            print 'XXXX', line_idx, org_lineIN_list[line_idx].strip()
            if '255\t' in org_lineIN_list[line_idx]:
                break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        DEBUG = False
        if DEBUG:
            print 'YYYY', line_idx, org_lineIN_list[line_idx].strip()

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            DEBUG = False
            if DEBUG: header = '>>>DEBUG_discard:\t'
            if DEBUG: print header, 'Discarded(%s)'%(org_lineIN_list[line_idx])
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                #NA# the blank line is missing tab
                #NAnew_lineIN_list.append('\t')

                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                # orphaned line in cell3 on certain line when crossing page break
                pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

        for tmp_str in tab_within_cell_list:
            new_lineIN_list[-1] = new_lineIN_list[-1].replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            #if new_lineIN_list[line_idx].startswith('TABLE 19'):
            if 'TABLE 19' in new_lineIN_list[line_idx]:
                start_line = line_idx
            elif new_lineIN_list[line_idx].startswith('255\t'):
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())
            #if new_lineIN_list[line_idx].startswith('255\t'):
            #    break

    return new_lineIN_list

def fix_lineIN_list_table_22(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []
    DEBUG = False
    if DEBUG:
        print 'XXXX', 'len(org_lineIN_list)', len(org_lineIN_list)

    last_row = '138\t'
    broken_row = [
    ]

    line_to_be_discarded = [
        '10/40G/100G Ethernet Compliant Codes',
        'SONET Compliant codes',
        'SAS/SATA Compliant codes',
        'Gigabit Ethernet Compliant codes',
        'Fibre Channel link length',
        'Fibre Channel Transmitter Technology',
        'Fibre Channel transmission media'
        'Fibre Channel Speed'
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 22' in org_lineIN_list[line_idx]:
            break
        if DEBUG:
            print 'XXXX', line_idx, org_lineIN_list[line_idx].strip()
            if '255\t' in org_lineIN_list[line_idx]:
                break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        DEBUG = False
        if DEBUG:
            print 'YYYY', line_idx, org_lineIN_list[line_idx].strip()

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                #NA# the blank line is missing tab
                #NAnew_lineIN_list.append('\t')

                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                pass
                # orphaned line in cell3 on certain line when crossing page break
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

        DEBUG = False
        if DEBUG:
            print 'ZZZZ', len(new_lineIN_list), new_lineIN_list[-1].strip()

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def fix_lineIN_list_table_23(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []
    DEBUG = False
    if DEBUG:
        print 'XXXX', 'len(org_lineIN_list)', len(org_lineIN_list)

    last_row = '141\t'
    broken_row = [
    ]

    line_to_be_discarded = [
        'This functionality is different from SFF-8472 and SFF-8431.',
        'Note: See',

    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 23' in org_lineIN_list[line_idx]:
            break
        if DEBUG:
            print 'XXXX', line_idx, org_lineIN_list[line_idx].strip()
            if '255\t' in org_lineIN_list[line_idx]:
                break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        DEBUG = False
        if DEBUG:
            print 'YYYY', line_idx, org_lineIN_list[line_idx].strip()

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                #NA# the blank line is missing tab
                #NAnew_lineIN_list.append('\t')

                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                pass
                # orphaned line in cell3 on certain line when crossing page break
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

        DEBUG = False
        if DEBUG:
            print 'ZZZZ', len(new_lineIN_list), new_lineIN_list[-1].strip()

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def fix_lineIN_list_table_24(org_lineIN_list):
    """ Add a column 'Bytes' before the column for 'Bits' """

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '1: Transmitter tuneable'

    broken_row = [
    ]

    line_to_be_discarded = [
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 24' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                # orphaned line on certain line when crossing page break
                pass
        else:
            if '\t' in org_lineIN_list[line_idx]:
                if org_lineIN_list[line_idx].startswith('Bits'):
                    new_lineIN_list.append('Byte\t' + org_lineIN_list[line_idx])
                else:
                    new_lineIN_list.append('147\t' + org_lineIN_list[line_idx])
            else:
                new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            if 'TABLE 24' in new_lineIN_list[line_idx]:
                start_line = line_idx
                end_line = start_line +200 # arbitrary
            #elif 'Transmitter tuneable' in new_lineIN_list[line_idx]:
            elif 'ter tuneable' in new_lineIN_list[line_idx]:
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())
            #if new_lineIN_list[line_idx].startswith('255\t'):
            #    break

    return new_lineIN_list

def fix_lineIN_list_table_26(org_lineIN_list):
    """ ' """

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '164\t0'

    broken_row = [
    ]

    line_to_be_discarded = [
        'Infiniband Data Rate codes',
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 26' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
            # orphaned line on certain line when crossing page break
            pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            if 'TABLE 26' in new_lineIN_list[line_idx]:
                start_line = line_idx
                end_line = start_line +200 # arbitrary
            elif 'Transmitter tuneable' in new_lineIN_list[line_idx]:
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())
            #if new_lineIN_list[line_idx].startswith('255\t'):
            #    break

    return new_lineIN_list

def fix_lineIN_list_table_31(org_lineIN_list):
    """ """

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '131+2*TL\t'
    broken_row = [
    ]

    line_to_be_discarded = [
        'Other Table Entries',
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 31' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
            # orphaned line on certain line when crossing page break
            pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            if 'TABLE 31' in new_lineIN_list[line_idx]:
                start_line = line_idx
                end_line = start_line +200 # arbitrary
            #elif 'Transmitter tuneable' in new_lineIN_list[line_idx]:
            elif 'ter tuneable' in new_lineIN_list[line_idx]:
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())
            #if new_lineIN_list[line_idx].startswith('255\t'):
            #    break

    return new_lineIN_list

def fix_lineIN_list_table_33(org_lineIN_list):

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []
    DEBUG = False
    if DEBUG:
        print 'XXXX', 'len(org_lineIN_list)', len(org_lineIN_list)

    last_row = '254-255\t'
    broken_row = [
    ]

    line_to_be_discarded = [
    ]
    tab_within_cell_list = [
        'output',
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 33' in org_lineIN_list[line_idx]:
            break
        if DEBUG:
            print 'XXXX', line_idx, org_lineIN_list[line_idx].strip()
            if '254-255\t' in org_lineIN_list[line_idx]:
                break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
                # orphaned line in cells on certain line when crossing page break
                pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

        for tmp_str in tab_within_cell_list:
            new_lineIN_list[-1] = new_lineIN_list[-1].replace('%s\t'%(tmp_str), '%s '%(tmp_str), 1)

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = False
    if DEBUG:
        for line_idx in range(len(new_lineIN_list)):
            if 'TABLE 33' in new_lineIN_list[line_idx]:
                start_line = line_idx
            elif new_lineIN_list[line_idx].startswith('254-255\t'):
                end_line = line_idx+1
                break
        for line_idx in range(start_line, end_line+10):
        #for line_idx in range(len(new_lineIN_list)):
            print '>>>>>>>>>>>>>>', '%d(%s)'%(line_idx, new_lineIN_list[line_idx].rstrip())

    return new_lineIN_list

def fix_lineIN_list_table_34(org_lineIN_list):
    """ remove blank line within this table when the table crosses page break on original PDF file"""

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '0\tRX output amplitude support\tAmplitude code 0000 supported'

    broken_row = [
    ]

    line_to_be_discarded = [
    ]
    broken_row2 = [
        '248-',
        '250-',
        '252-',
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 34' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
            # orphaned line on certain line when crossing page break
            pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def fix_lineIN_list_table_35(org_lineIN_list):
    """ remove blank line within this table when the table crosses page break on original PDF file"""

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = 'Page 00h Byte 193 bit 3)\t'

    broken_row = [
    ]

    line_to_be_discarded = [
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 35' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
            # orphaned line on certain line when crossing page break
            pass
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def fix_lineIN_list_table_39(org_lineIN_list):
    """ remove blank line within this table when the table crosses page break on original PDF file"""

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")

    line_idx = -1
    new_lineIN_list = []

    last_row = '253\tAll'

    broken_row = [
    ]

    broken_row2 = [
        '248-',
        '250-',
        '252-',
    ]

    line_to_be_discarded = [
    ]

    # get lines before seeing this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])
        if 'TABLE 39' in org_lineIN_list[line_idx]:
            break

    # process the lines in this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1

        if any (str2 in org_lineIN_list[line_idx] for str2 in line_to_be_discarded):
            pass # discard this line
        elif org_lineIN_list[line_idx].rstrip('\n') == '':
            if last_row in new_lineIN_list[-1]:
                # the end of this table
                new_lineIN_list.append(org_lineIN_list[line_idx])
                new_lineIN_list.append('\n') # insert a blank line here to terminate this table

                # discard any extra line within the table until we see a blank line
                while org_lineIN_list[line_idx+1].strip() != '':
                    line_idx += 1
                break
            else:
                pass # discard the blank line
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row):
            # orphaned line on certain line when crossing page break
            pass
        elif any(re.search(str2, org_lineIN_list[line_idx]) for str2 in broken_row2):
            # orphaned line on certain line it is wider than cell width
            new_lineIN_list.append(org_lineIN_list[line_idx].replace('\n', '')+ org_lineIN_list[line_idx+1])
            line_idx += 1
        else:
            new_lineIN_list.append(org_lineIN_list[line_idx])

    DEBUG = True
    if DEBUG:
        for tmp_line in new_lineIN_list:
            print '>>>DEBUG_39:\t', tmp_line

    # get lines after this table
    while line_idx < len(org_lineIN_list)-1:
        line_idx += 1
        new_lineIN_list.append(org_lineIN_list[line_idx])

    return new_lineIN_list

def convert_pdf_into_csv(source_file, target_subdir):
    """ For QSFP PDF conly
        CSV file(s) are created,
        based on TABLE nn, where nn is: TBD

        Parameter: default arguments from calling this program
        Return: a list of CSV file name
    """
    DEBUG = False
    if DEBUG: header = '>>>DEBUG:\t'
    #if DEBUG: print header

    regexp_table = re.compile(r"TABLE\s+(\d+\w?)\s")
    fileIN = open( source_file, "r")
    lineIN_list = fileIN.readlines()

    # To create csv file for tables, we need to fix the lines within the table because
    # 1. the table cross page boundary that created many blank line(s)
    # 2. the text has embedded tab which should be removed
    # 3. others: see each "fix_..." for details
    lineIN_list = fix_lineIN_list_space_only(lineIN_list)
    lineIN_list = fix_lineIN_list_table_10(lineIN_list)
    lineIN_list = fix_lineIN_list_table_13(lineIN_list)
    lineIN_list = fix_lineIN_list_table_17(lineIN_list)
    lineIN_list = fix_lineIN_list_table_19(lineIN_list)
    lineIN_list = fix_lineIN_list_table_22(lineIN_list)
    lineIN_list = fix_lineIN_list_table_23(lineIN_list)
    lineIN_list = fix_lineIN_list_table_24(lineIN_list)
    lineIN_list = fix_lineIN_list_table_26(lineIN_list)
    lineIN_list = fix_lineIN_list_table_31(lineIN_list)
    lineIN_list = fix_lineIN_list_table_33(lineIN_list)
    lineIN_list = fix_lineIN_list_table_34(lineIN_list)
    lineIN_list = fix_lineIN_list_table_35(lineIN_list)
    lineIN_list = fix_lineIN_list_table_39(lineIN_list)

    csv_filename_list = []
    head, tail = os.path.split(source_file)
    file_name, file_extension = os.path.splitext(tail)

    # Every table
    #target_file_all_table = target_subdir.replace('.csv', '_all_table.csv')
    target_file_all_table = os.path.join(target_subdir, file_name + '_all_table.csv')
    print '>>>Creating', '({target_file_all_table})'.format(**locals())

    fileOUT_all_table = open( target_file_all_table, "w+")

    # Every byte table
    #target_file_byte_table = target_subdir.replace('.csv', '_byte_table.csv')
    target_file_byte_table = os.path.join(target_subdir, file_name + '_byte_table.csv')
    print '>>>Creating', '({target_file_byte_table})'.format(**locals())
    fileOUT_byte_table = open( target_file_byte_table, "w+")

    # memory map table
    #target_file_map_table = target_subdir.replace('.csv', '_map_table.csv')
    target_file_map_table = os.path.join(target_subdir, file_name + '_map_table.csv')
    print '>>>Creating', '({target_file_map_table})'.format(**locals())
    fileOUT_map_table = open( target_file_map_table, "w+")

    for line_idx in range( len(lineIN_list) ):
        #if DEBUG and 'TABLE' in  lineIN_list[line_idx]:
        #    print header, lineIN_list[line_idx].strip()
        if regexp_table.search(lineIN_list[line_idx]):
            table_nu = regexp_table.search(lineIN_list[line_idx]).group(1)
            #if DEBUG: print '>>>>>>>>>>>>>>table_nu =', table_nu
            #if DEBUG: print header, 'FOUND', table_nu, '\t',lineIN_list[line_idx].strip()
            csv_filename_list.append(table_nu)

            #if table_nu == '19':
            #    lineOUT_list = extract_table_byte_table(line_idx, lineIN_list)
            if table_nu == '1':  lineOUT_list = extract_table_1(line_idx, lineIN_list)
            elif table_nu =='2': lineOUT_list = extract_table_2(line_idx, lineIN_list)
            elif table_nu =='3': lineOUT_list = extract_table_3(line_idx, lineIN_list)
            elif table_nu =='4': lineOUT_list = extract_table_4(line_idx, lineIN_list)
            elif any( table_nu == z for z in ('5', '6', '8', '9', '10', '11', '12', '13', '17', '18', '19', '22', '23', '24', '26', '27', '28', '29', '30', '32A', '31', '33', '34', '35', '39')): 
                lineOUT_list = extract_table_byte_table(line_idx, lineIN_list)
            #elif table_nu =='7': lineOUT_list = extract_table_7(line_idx, lineIN_list)
            elif any( table_nu == z for z in ('14', '15', '16', '21', '25', '32', '32', '32', '32')): 
                lineOUT_list = extract_table_byte_table(line_idx, lineIN_list)
            else:
                lineOUT_list = []

            DEBUG = False
            if DEBUG and len(lineOUT_list) != 0:
                print header, table_nu, 'lineOUT_list', lineOUT_list
                from pprint import pprint as pp
                pp(lineOUT_list)


            table_name = re.sub('^.*?TABLE ', 'TABLE ', lineIN_list[line_idx]) # Fix this line when it does not start with 'TABLE nn'

            if True:
                #target_file_single_table = target_subdir.replace('.csv', '_table_%s.csv'%(table_nu))
                target_file_single_table = os.path.join(target_subdir, file_name + '_table.csv')
                print '>>>Creating', '({target_file_single_table})'.format(**locals())

                fileOUT_single_table = open( target_file_single_table, "w+")
                fileOUT_single_table.write ('\n'.join(lineOUT_list))
                fileOUT_single_table.close()

            #if len(lineOUT_list) != 0:
            if True:
                if table_nu != '1': fileOUT_all_table.write('\n\n')
                #try:
                #    if not flag_all_table:
                #        fileOUT_all_table.write('\n\n') # add lines between 2 tables
                #except NameError:
                #    flag_all_table = True
                fileOUT_all_table.write('%s'%(table_name))
                fileOUT_all_table.write ('\n'.join(lineOUT_list))

            if len(lineOUT_list)>0 and (re.search('^Byte,', lineOUT_list[0]) or re.search('^Address,Byte,', lineOUT_list[0])):
                #fileOUT_byte_table.write('\n\n')
                try:
                    if flag_byte_table:
                        fileOUT_byte_table.write('\n\n') # add lines between 2 tables
                    #fileOUT_byte_table.write('\n') # add lines between 2 tables
                except NameError:
                    flag_byte_table = True
                fileOUT_byte_table.write('%s'%(table_name))

                # Fix table 3: remove first column about A0h
                if re.search('SINGLE BYTE', table_name):
                    lineOUT_list = [re.sub('^Address.', '', this_line) for this_line in lineOUT_list]
                    lineOUT_list = [re.sub('^A0h.', '', this_line) for this_line in lineOUT_list]

                fileOUT_byte_table.write ('\n'.join(lineOUT_list))

            if len(lineOUT_list)>0 and re.search('MAP', table_name):
                try:
                    if flag_map_table:
                        fileOUT_map_table.write('\n\n') # add lines between 2 tables
                except NameError:
                    flag_map_table = True
                fileOUT_map_table.write('%s'%(table_name))

                ## Fix table 3: remove first column about A0h
                #if re.search('SINGLE BYTE', table_name):
                #    lineOUT_list = [re.sub('^Address.', '', this_line) for this_line in lineOUT_list]
                #    lineOUT_list = [re.sub('^A0h.', '', this_line) for this_line in lineOUT_list]

                fileOUT_map_table.write ('\n'.join(lineOUT_list))




    fileOUT_all_table.close()
    fileOUT_byte_table.close()
    fileOUT_map_table.close()

    return csv_filename_list


#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

if __name__ == '__main__':
    import sys

    for i in range(len(sys.argv)):
        #if sys.argv[i].startswith('--i') and sys.argv[i].upper().endswith('.XML') and "=" in sys.argv[i]:
        if sys.argv[i].startswith('--i') and "=" in sys.argv[i]:
            tmp_list = sys.argv[i].split('=')
            source_file=tmp_list[1]
        elif sys.argv[i].startswith('--o') and "=" in sys.argv[i]:
            # looking for argument in "--output=xxxx" format or "--o=xxxx" format
            tmp_list = sys.argv[i].split('=')
            target_subdir = tmp_list[1]

    # Verify arguments exist
    try:
        # Some message to the console
        print "*** Source is <%s>" % (source_file)
        print "    Target is <%s>" % (target_subdir)

    except:
        print
        print " Error Need two arguments. First, the input file, which should be a .xml file, second the output file"
        print
        sys.exit()

    # Find the formfactor which is part of the input XML file name
    for formfactor_name in formfactor_name_list:
        # Look for file name contains known formfactor key words, "topaz", 'cxp" etc
        # e.g. source_file "Topaz_memory_map_A22.xml"
        if formfactor_name in source_file.lower():
            print 'this_formfactor =', formfactor_name.upper()
            this_formfactor = formfactor_name.upper()
            break

    # Produce a table for processing
    print 'this_formfactor', this_formfactor
    csv_filename_list = convert_pdf_into_csv(source_file, target_subdir )
