#///////////////////////////////////////////////////////////////////
# Produce memory test scripts form template and from a fixed memory CSV file, which is from a memory map XLS/XLSX file 
#///////////////////////////////////////////////////////////////////
# Description:
#  Create memory test scripts based on a fixed CSV file and uses a group of memory test templates
#  The fixed CSV file was extracted from XLS memory map, and was "fixed" based on certain rules when the XLS has error(s)
#
# Below are rule(s) to create memory test based on attribute:
#  RO: fixed, latched, changing
#  RW: protected or un-protected. Volatile or Non-Volatile
#  119-122: used as password change
#  123-126: used as password entry
#  127: Used as page selector
#
# Below are sample of first few row in the the XLS/XLSX file
# Note that the first 2 lines are from the first row, which is the header row:
#
#  Type      Name            Page  Size  Start    End      Bits    Read/Write    Volatile /    Description
#                                        Address  Address  Offset  Permissions   Non Volatile
#  Register  module_id       Low   1     0        0                RO            Volatile      Module Identifier (00h)
#  Field     module_id             8                       All                                 Module Identifier (00h)
#  Register  num_tx_channel  Low   1     1        1                RO            Volatile      Number of Tx Channels
#  Field     num_tx_channel        6                       0                                   TX POD=0x18, RX POD=0x00
#  Register  num_rx_channel  Low   1     2        2                RO            Volatile      Number of Rx Channels
#  Field     num_rx_channel        6                       0                                   TX POD=0x00, RX POD=0x18
#  Register  state           Low   1     3        3                RO            Volatile
#  Field     i2c_pin_state         2                       6                                   TX POD ('00' = 0xA0, '01' = 0xA2, '10' = 0xA4, 0xA6 = '11')                               RX POD ('00' = 0xA8, '01' = 0xAA, '10' = 0xAC, 0xAE = '11')
#  Field     reserved              1                       5                                   Reserved
#  Field     ext_ctrl_page         1                       4                                   '1' - Extended Controls page in factory default state, '0' - Extended Controls non-volatile page controls have changed from factory default state.
#  Field     paging_support        1                       3                                   '0' - Paging supported, '1' - Flat Memory
#  Field     hw_tx_disable         1                       2                                   Hardware TxDisable State, read from hardware pin - '0' if not asserted.
#  Field     interrupt_status      1                       1                                   Interrupt Status - '0' if Interrupt is not asserted.  The logical OR of all unmasked Fault, Alarm, Warning and Status flags.
#  Field     data_not_ready        1                       0                                   Data Not Ready - '0' when DOM data is correct and can be read
#
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
#if True:
#    DEBUG = True
#    if DEBUG: print '>>>DEBUG', 'in csv_table'

formfactor_name_list = [ 'xfp', 'sfp', 'qsfp', 'cxp', 'topaz', 'cfp', 'boa_25', ]

import os
import sys
import re

#NOT_USEDdef main(input_file, output_file):
#NOT_USED    """
#NOT_USED    TBD
#NOT_USED    """
#NOT_USED
#NOT_USED    dir_full_path = os.path.dirname( os.path.abspath(sys.argv[0]))
#NOT_USED    file_full_path = dir_full_path + "\\" + input_file
#NOT_USED    print '*** Full file path:', file_full_path

#NOT_USEDdef fix_translation_error_from_memory_template_to_py(lineIN_list, file_name):
#NOT_USED    """
#NOT_USED        TODO list:
#NOT_USED                   test location of "addr_vendor_name_p00" and page number 2-255, etc.
#NOT_USED
#NOT_USED        Fix in-compatiblity errors when translating memory .tst template to .py
#NOT_USED        Paramenters: lineIN_list
#NOT_USED                     file_name: output Python file name
#NOT_USED        return lineOUT_list
#NOT_USED    """
#NOT_USED    lineOUT_list = []
#NOT_USED
#NOT_USED
#NOT_USED    idx = 0
#NOT_USED    max_idx = len(lineIN_list)
#NOT_USED
#NOT_USED    remove_leading_blank_line = True
#NOT_USED    while idx < max_idx:
#NOT_USED
#NOT_USED        if False:
#NOT_USED            pass
#NOT_USED
#NOT_USED        elif ('DEBUG_TEMPLATE' in lineIN_list[idx]):
#NOT_USED            pass # Remove this line in template.template. Not put it on the output .py file
#NOT_USED
#NOT_USED        else:
#NOT_USED            lineOUT_list.append ( lineIN_list[idx] )
#NOT_USED        idx += 1
#NOT_USED
#NOT_USED    # Reduce double blank line
#NOT_USED    lineOUT_list2 = []
#NOT_USED    max_idx = len( lineOUT_list)
#NOT_USED
#NOT_USED    for idx in range ( max_idx):
#NOT_USED        if idx + 1 < max_idx and len (lineOUT_list[idx].strip()) == 0 and len (lineOUT_list[idx + 1].strip()) == 0: 
#NOT_USED            pass
#NOT_USED        else:
#NOT_USED            lineOUT_list2.append ( lineOUT_list[idx] )
#NOT_USED            
#NOT_USED    # Remove leading blank lines from the list
#NOT_USED    while True:
#NOT_USED        if len(lineOUT_list2) == 0 or len(lineOUT_list2[0].strip()) != 0:
#NOT_USED            break
#NOT_USED        else:
#NOT_USED            del lineOUT_list2[0] # Del the leading blank line and repeat checking 
#NOT_USED
#NOT_USED    del lineOUT_list
#NOT_USED    return lineOUT_list2

def create_memory_map_dictionary ( source_file, formfactor, category):
    """
       Create 1 python test script based on template.template and memory map
       
       Assumption 0 : Default memory map file is provided through argument of __main__
       Assumption 1 : template subdirectory of the source_dir exists
       e.g. 
          if source_dir is 'output\memory\topaz'
          template subidirectory should exist as 'output\memory\topaz\template'
          
       Assumption 2: a template.template is already in each subdirectory 
          e.g. 'output\memory\topaz\template\rd_only\fixed\template.template' exists
          
       Assumption 3: the template.template contains keyword "NEW_????"
          e.g. NEW_addr, NEW_byte_count
          
       This funciton creates on .py,
       (1) The subdirectory is concatinated from input parameters:
          e.g. source_dir is 'output\memory\topaz'
               category is 'msa'
               then the subdirectory is 'output\memory\topaz\msa'
       (2). Then the reset of full path and file name is from memory map. 
          Its subdirectory is based on R/W, volatility, and from the name (flags, latched, monitor, etc. 
          e.g. 'read_only\fixed'
          Its file name is based on page, starting address and ending address 
          e.g. 'p000_byte_212_217.py'
          hence the full file name is 'output\memory\topaz\msa\read_only\fixed\p000_byte_212_217.py'
         Windows Grep Search Results

        known:
        low:    variety of measurement, diagnostic and control functions 
        page 0: Serial ID and is used for read only identification information.
        page 1: conditional on the state of bit 2 in byte 221
        page 2: User EEPROM
                Page 02 is optionally provided as user writable EEPROM. The fixed side may read or
                write this memory for any purpose. If bit 4 of Page 00h byte 129 is set, however,
                the first 10 bytes of Table 02h, bytes 128-137 will be used to store the CLEI code for the free side device.
        page 3: free side device thresholds, channel thresholds and masks, and optional channel controls.

       Outpur CSV row format, generic terms:
          bit_loc, attr_rd,  attr_wr,  attr_volatility, attr_default
          pp_nnn_bb, R<0|1|3>, W<0|1|3>, <N| >,           <X|R|1| >
          pp=00-03
          nnn=000-255
          bb=07-00
          R0 or W0: no pwd protected
          R1 or W1: has host pwd protected
          R3 or W3: has host pwd protected
          N or blank: N means non-volatile. blank means volatile
          X, RESERVED, 1 or blank: if X, the value is "don't care", and can be 0 or 1
                           if RESERVED, the value is "reserved", and must be 0.
                           if CHANGE, the value is changing if description contains 'Monitors', as in 'Channel Monitors' or 'Free Side Monitors'
                           if COR, the value may change if description contains 'Flags'. Read twice
                           if 1, the value is 1,
                           if blank, the value is 0

       Outpur CSV row format, possible terms:
             bit_loc, attr_rd,  attr_wr,  attr_volatility, default
          1. pp_nnn: R<0|1>,W<0|1>,V,<R| >
          2. pp_nnn: R<0|1>,W<0|1>,N,X
          3. pp_nnn: R3,    W0,    V,<1|0>
          4. pp_nnn: R0,    W3,    N,<R|1|X|D|C|0>

       case 1: for writable bit and volatile, either with or without host pwd; the default is Reserved or 0
               value after reset is 0. 
       case 2: for writable bit and non-volatile, either with or without host pwd; the default is "don't care"
               value after reset is non-volatile.
       case 3: for write-only bit. either with or without host password
               the <?> means the default must be all 1s or all 0s consistently on all the following cases:
               - pp=00, and
               - nnn=119 thru 126, and
               - bb=07 thru 00.
       case 4: for read-only bit, without host password

       Parameter: source_dir
                  formfactor
                  category
    """
    # Define variables
    
    import csv
    row_list = []
    # Scan the whole csv 
    #memory_map_csv_file = input_file
    #with open(source_file, 'rb') as csvfile:

    DEBUG_file = False

    with open(source_file, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for cell_list in reader:
            row_list.append(cell_list)

    DEBUG_2 = False
    if DEBUG_2:
        # Scan every row to extract a table
        row_nu = -1
        while row_nu < len(row_list)-1:
        #while row_nu < 15:
            row_nu += 1
            cell_list = row_list[row_nu]
            if len(row_list[row_nu]) == 0: break
            if len(row_list[row_nu]) > 0:
                print row_nu, 'row_list[row_nu][0](%s)'%(row_list[row_nu][0])
            if len(row_list[row_nu]) > 0 and row_list[row_nu][0].startswith('TABLE'):
                print '*'*40
                print row_nu, 'row_list[row_nu][0](%s)'%(row_list[row_nu][0])
                print '*'*40

    row_nu = -1
    table_list = []
    while row_nu < len(row_list)-1:
        row_nu += 1
        #if row_list[row_nu][0].startswith('TABLE '):
        if len(row_list[row_nu]) > 0 and row_list[row_nu][0].startswith('TABLE'):
            #table_nu   = re.search('TABLE\s+(\w+)\s+-\s+(.*)', row_list[row_nu][0]).group(1)
            #table_name = re.search('TABLE\s+(\w+)\s+-\s+(.*)', row_list[row_nu][0]).group(2)
            table_name = row_list[row_nu][0]
            table_content = []
            for row_nu in range(row_nu+1, len(row_list)):
                #if row_list[row_nu].strip() == '':
                if len(row_list[row_nu]) == 0:
                    break
                table_content.append(row_list[row_nu])
            table_list.append([table_name, table_content])
    for table_name, table_content in table_list:
        print table_name
        DEBUG = False
        if DEBUG and '34' in table_name:
            print '>>>DEBUG_tbl34', table_content

    # extract row for each of the memory map table
    # e.g TABLE 5 - LOWER PAGE 00H MEMORY MAP
    #     TABLE 33 - UPPER PAGE 03H MEMORY MAP

    regexp_page  = re.compile('[LOWER|UPPER]\s+PAGE.*?(\d+)H')
    regexp_byte  = re.compile('PAGE\s+(\d+)H\s+BYTE')

    memory_attribute_dict = {}
    memory_attribute_page_dict = {}
    #for name in table_dict.keys():

    # Page 1 is 
    pp = '01'
    starting_addr = 128
    ending_addr = 255
    nnn = '%03d-%03d'%(starting_addr, ending_addr)
    pp_nnn = '{pp}_{nnn}'.format(**locals())
    #memory_attribute_dict[pp_nnn] = 'R0,W3,V' + ',X' * 8
    memory_attribute_dict[pp_nnn] = 'R0,W3,N' + ',X' * 8
                        
    # Page 2 is non-volatile. No memory map
    pp = '02'
    starting_addr = 128
    ending_addr = 255
    nnn = '%03d-%03d'%(starting_addr, ending_addr)
    pp_nnn = '{pp}_{nnn}'.format(**locals())
    memory_attribute_dict[pp_nnn] = 'R0,W1,N' + ',X' * 8
                        
    DEBUG_byte_148 = True
    if DEBUG_byte_148: header_byte_148 = '>>>DEBUG_byte_148:\t'

    for table_name, table_content in table_list:
        # Process table specically for memory page (name contains 'MAP')
        # Note:
        #  Use keyword in description to decide the nature of the bit
        #  e.g. TABLE 5 byte 3-21 descrtion is "Interrupt Flags" - it means they are latched
        # Table 5 (page low)
        #  Key word                bit property
        #  Flags                   L for latched
        #  Monitors                D for DDM monitor
        #  Control                 C for control
        #  Masks                   M for mask
        #  Properties              P for Property (use X, i.e any value,  instead)
        #  (tmp:Assigned )         P for Property (use X, i.e any value,  instead)
        #  Reserved                R for Rerseved
        #  Password                W for WO write only
        #  Page                    C for control (page is control)
        # Table 19 (page 0
        #  any                     P for Property (use X, i.e any value,  instead)
        # Table 31 (page 1)
        #  any                     P for Property (use X, i.e any value,  instead)
        # Table 33 (page 3)
        #  Thresholds              T for Threshold
        #  Control                 C for control
        #  Masks                   M for mask
        #  Reserved                R for Rerseved

        if regexp_page.search(table_name):
            pp = regexp_page.search(table_name).group(1)
            for col in table_content:
                if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'col(%r)'%(col)
                if not re.search('^\d+', col[0].strip()): continue # skip the header line
                tmp_list = col[0].strip().split('-')
                if len(tmp_list) == 1:
                    # this row has starting address only
                    if int(pp) == 1 and tmp_list[0] == '130':
                        # For the rol with "130,131"...
                        starting_addr = 130
                        ending_addr = 255
                        pp_col = '{pp}_%03d-%03d'.format(**locals())%(starting_addr, ending_addr)
                    elif int(pp) == 1 and re.search('^13\d\+', tmp_list[0]):
                        # ignore "130+2*TL" or "131+2*TL"
                        pass
                    else:
                        starting_addr = int(tmp_list[0])
                        ending_addr = starting_addr
                        pp_col = '{pp}_%03d'.format(**locals())%(starting_addr)
                else:
                    # this row has starting and ending address
                    # e.g. 128-175
                    starting_addr = int(tmp_list[0])
                    ending_addr = int(tmp_list[1])
                    pp_col = '{pp}_%03d-%03d'.format(**locals())%(starting_addr, ending_addr)

                # for individual byte
                TEST_NEW = True
                for addr in range(starting_addr, ending_addr+1):
                    nnn = '%03d'%(addr)
                    pp_nnn = '{pp}_{nnn}'.format(**locals())
                    if int(pp) == 0 and addr >= 128: 
                        # p0 high
                        #attribute = ['R0,W3,V', 'X']
                        attribute = ['R0,W3,N', 'X']
                        #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',X' * 8
                        if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',X' * 8
                    elif int(pp) == 1 and addr >= 128:
                        # p1 high
                        #attribute = ['R0,W3,V', 'X']
                        attribute = ['R0,W3,N', 'X']
                        #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',X' * 8
                        if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',X' * 8
                    elif int(pp) == 2 and addr >= 128:
                        # p2 high
                        attribute = ['R0,W1,N', 'X']
                        if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W1,N' + ',X' * 8
                    else:
                        # page low and p3 high
                        if col[2] == 'Read-Only':
                            if False:
                               pass
                            elif re.search('Flags$', col[1], re.I):
                                #attribute = ['R0,W3,V', 'L'] # Flags, must read twice
                                attribute = ['R0,W3,N', 'L'] # Flags, must read twice
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',L' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',L' * 8
                            elif re.search('Monitors$', col[1], re.I):
                                #attribute = ['R0,W3,V', 'D'] # Changing
                                attribute = ['R0,W3,N', 'D'] # Changing
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',D' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',D' * 8
                            elif re.search('Thresholds$', col[1], re.I):
                                #attribute = ['R0,W3,V', 'T'] # Changing
                                attribute = ['R0,W3,N', 'T'] # Changing
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',T' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',T' * 8
                            elif re.search('^Reserved', col[1], re.I):
                                #attribute = ['R0,W3,V', 'R'] # Reserved
                                attribute = ['R0,W3,N', 'R'] # Reserved
                                #memory_attribute_dict[pp_col] = 'R0,W3,V' + ',R' * 8
                                memory_attribute_dict[pp_col] = 'R0,W3,N' + ',R' * 8
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',R' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',R' * 8
                            else:
                                #attribute = ['R0,W3,V', 'X']
                                attribute = ['R0,W3,N', 'X']
                                memory_attribute_page_dict[pp_nnn] = attribute
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',X' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',X' * 8
                        elif col[2] == 'Read/Write':
                            if 119 <= addr <= 126:
                                col[2] == 'Write-Only'
                                #attribute = ['R0,W3,V', 'W']
                                attribute = ['R0,W3,N', 'W']
                                memory_attribute_dict[pp_col] = 'R3,W0,V' + ',W' * 8
                                #if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,V' + ',W' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W3,N' + ',W' * 8
                            if addr == 127:
                                attribute = ['R0,W0,V', 'C']
                                memory_attribute_dict[pp_col] = 'R0,W0,V' + ',C' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W0,V' + ',C' * 8
                                if False:
                                    if DEBUG_byte_148 and starting_addr == 127: 
                                        print header_byte_148,'memory_attribute_dict[{pp_col}](%r)'.format(**locals())%(memory_attribute_dict[pp_col]), 3500
                            #elif re.search('^Controls$', col[1], re.I) or re.search('^Control$', col[1], re.I):
                            elif re.search('Controls', col[1], re.I) or re.search('Control', col[1], re.I):
                                attribute = ['R0,W0,V', 'C'] # volatile, init to 0
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W0,V' + ',C' * 8
                            elif re.search('Masks', col[1], re.I):
                                attribute = ['R0,W0,V', 'M'] # volatile, init to 0
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W0,V' + ',M' * 8
                            elif re.search('^Reserved$', col[1], re.I) or re.search('^Reserved ', col[1], re.I): # For the case 'Reserved (2 Bytes)'
                                attribute = ['R0,W0,V', 'R']
                                memory_attribute_dict[pp_col] = 'R0,W0,V' + ',R' * 8
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W0,V' + ',R' * 8
                            else:
                                attribute = ['R0,W0,V', ' ']
                                if TEST_NEW and addr == starting_addr: memory_attribute_dict[pp_col] = 'R0,W0,V' + ', ' * 8
                    memory_attribute_page_dict[pp_nnn] = attribute
                    if False:
                        if addr == starting_addr:
                            memory_attribute_dict[pp_col] = attribute

                    if False:
                        if DEBUG_byte_148:
                            try:
                                print header_byte_148,'memory_attribute_dict["00_127"](%r)'%(memory_attribute_dict['00_127']), 3600
                            except KeyError:
                                pass

                # Fix missing location
                #if int(pp) == 0: 
                #    if starting_addr >= 128:
                #        # page high
                #        #memory_attribute_dict[pp_col] = 'R0,W3,V' + ',X' * 8
                #        memory_attribute_dict[pp_col] = 'R0,W3,N' + ',X' * 8
                #    else:
                #        # page low
                #        #memory_attribute_dict[pp_col] = 'R0,W3,V' + ',X' * 8
                #        memory_attribute_dict[pp_col] = 'R0,W3,N' + ',X' * 8

                if True:
                    if False:
                        if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'pp_nnn(%r)'%(pp_nnn)
                        if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'memory_attribute_page_dict[{pp_nnn}](%r)'.format(**locals())%(memory_attribute_page_dict[pp_nnn]), 4000
                        if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'col(%r)'%(col)
                    else:
                        if DEBUG_byte_148:                     print header_byte_148,'pp_nnn(%r)'%(pp_nnn)
                        if DEBUG_byte_148:                     print header_byte_148,'memory_attribute_page_dict[{pp_nnn}](%r)'.format(**locals())%(memory_attribute_page_dict[pp_nnn]), 4000
                        if DEBUG_byte_148:                     print header_byte_148,'col(%r)'%(col)

##################
                if False:
                    if DEBUG_byte_148 and starting_addr == 127: 
                        print header_byte_148,'memory_attribute_dict[{pp_col}](%r)'.format(**locals())%(memory_attribute_dict[pp_col]), 5000
                        
    # Fix missing location
    ##memory_attribute_dict['00_000'] = 'R0,W3,V' + ',X' * 8
    #memory_attribute_dict['00_000'] = 'R0,W3,N' + ',X' * 8
    #memory_attribute_dict['00_127'] = 'R0,W0,V' + ',X' * 8

    DEBUG_fix_missing_location = True
    if DEBUG_fix_missing_location: header_fix_missing_location = '>>>DEBUG_fix_missing_location:\t'
    if DEBUG_fix_missing_location:
        tmp_list = []
        for k,v in memory_attribute_dict.items():
            #print header_fix_missing_location, 'before fix', 'memory_attribute_dict =', k,v
            #tmp_text =  header_fix_missing_location + 'before fix' + 'memory_attribute_dict =' + k + v
            tmp_text = '{k} {v}'.format(**locals())
            tmp_list.append(tmp_text)
        tmp_list.sort()
        for tmp_text in tmp_list:
            print header_fix_missing_location, 'before fix', 'memory_attribute_dict =', tmp_list
  


    for table_name, table_content in table_list:
        if regexp_byte.search(table_name):
        # process individual bit within a byte by extracting then from a table
        # case 1:
        # e.g. TABLE 17 - HARDWARE INTERRUPT PIN MASKING BITS (PAGE 00H BYTES 100-106)
        #      Byte,Bit,Name,Description,PC,AC,AO,SM
        #      100,7,M-Tx4 LOS Mask,Masking Bit for TX LOS indicator, channel 4,C,C,C,C
        #      ,6,M-Tx3 LOS Mask,Masking Bit for TX LOS indicator, channel 3,C,C,C,C
        # case 2:
        #      TABLE 21 - EXTENDED IDENTIFIER VALUES (PAGE 00H BYTE 129)
        #      Bit,Description of Device Type
        #      " 7-6",00: Power Class 1 (1.5 W max.)
        #      ,01: Power Class 2 (2.0 W max. )
        #      ,10: Power Class 3 (2.5 W max. )
        #      ,11: Power Class 4 (3.5 W max. )
        #      5,Reserved

            attribute = [None for z in range(8)]

            pp = regexp_byte.search(table_name).group(1)

            DEBUG = False
            if DEBUG: header = '>>> DEBUG'
            DEBUG_p3_248 = True
            if DEBUG_p3_248: header_p3_248 = '>>>DEBUG_p3_248'
            DEBUG_table6 = False
            if DEBUG_table6: header_table6 = '>>>DEBUG_table6:\t'

            if len(table_content) > 0 and table_content[0][1].startswith('# Bytes'):
                # Change the numober of byte into 'Bit'
                table_content[0][1] = 'Bit'
                for idx in range(1, len(table_content)): # 224/225
                    if table_content[idx][0] == '':
                        pass
                    elif '7-4' in table_content[idx][1]: # 224/225
                        pass
                    else:
                        table_content[idx][1] = '7-0'

            # Fix table 21, where the byte number is not in the table itself
            if len(table_content) > 0 and table_content[0][0].startswith('Bit'):
                nnn = re.search('PAGE.*BYTE\s+([\d-]+)', table_name).group(1)

                # Put the multiple line description into single line descrption
                for idx in range(len(table_content)-1,-1,-1):
                    col = table_content[idx]
                    if col[0] == '':
                        table_content[idx-1][1] += ' ' + col[1]
                        table_content.pop(idx)

                # Put the multiple line description into single line descrption
                for idx in range(len(table_content)):
                    col = table_content[idx]
                    #if col[0].startswith('Bit'):
                    #    col.insert(0, 'Byte')
                    #else:
                    #    col.insert(0, nnn)
                    col.insert(0, 'Byte' if col[0].startswith('Bit') else nnn)
                    table_content[idx] = col

            # Fix Table 13 or any table where the byte number is not shown just once, but repeatedly shown for each row of its bit
            # Also fix Table 18, byte 111-112, where the bit number start 15, make it 7
            for idx in range(len(table_content)):
                col = table_content[idx]
                if not col[0].startswith('Byte'):
                    if re.search('15', col[1]): col[1] = col[1].replace('15', '7')
                    if re.search('\d', col[0]) and re.search('^\s*[6543210]', col[1].split('-')[0]): col[0] = ''
                table_content[idx] = col

            if len(table_content) > 0 and table_content[0][0].startswith('Byte'):
                # case 1: Byte,Bit,Name,Description,PC,AC,AO,SM
                for col in table_content:
                    if DEBUG_table6: print header_table6, 'col(%r)'%(col)
                    if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'col(%r)'%(col)
                    if DEBUG_byte_148: print header_byte_148,'col(%r)'%(col), 20000
                    #if DEBUG_byte_148: print header_byte_148,'col(%r)'%(col)
                    if re.search('\d+', col[0]) or re.search('^$', col[0]):
                        if DEBUG_byte_148: print header_byte_148,'col(%r)'%(col), 30000
                        if re.search('\d+', col[0]):
                            try:
                                nnn = '%03d'%(int(col[0]))
                                nn2 = None
                            except ValueError:
                                nnn = '%03d'%(int( col[0].split('-')[0] ))
                                nn2 = '%03d'%(int( col[0].split('-')[1] ))
                            try: # Fix Table 13 or any table where the byte number is not shown just once, but repeatedly shown for each row of its bit
                                attribute_bit 
                            except NameError:
                                attribute_bit = [None for z in range(8)]
                        tmp_list = col[1].strip().split('-')
                        if DEBUG_table6: print header_table6, 'col[1](%r)'%(col[1])
                        if len(tmp_list) == 1:
                            try:
                                starting_bit = min(int(tmp_list[0]), 7) # Fix table 18, where bit starts at 15 for 111-112
                                ending_bit = starting_bit
                            except ValueError: # 'All', 'Reserved' or others
                                starting_bit = 7
                                ending_bit = 0
                        else:
                            try: # bit in b-b format
                                starting_bit = min(int(tmp_list[0]), 7) # Fix table 18, where bit starts at 15 for 111-112
                                ending_bit = int(tmp_list[1])
                            except ValueError: # 'All', 'Reserved' or others
                                starting_bit = 7
                                ending_bit = 0
                        if DEBUG_table6: print header_table6, 'starting_bit(%r)'%(starting_bit)
                        if DEBUG_table6: print header_table6, 'ending_bit(%r)'%(ending_bit)
                        pp_nnn = '{pp}_{nnn}'.format(**locals())
                        attribute_rw = memory_attribute_page_dict[pp_nnn] 
                        #memory_attribute_dict[pp_nnn] = attribute_rw[0]

                        for bit in range(starting_bit, ending_bit-1,-1):
                            if DEBUG_table6: print header_table6, 'bit(%r)'%(bit)
                            attribute_bit[bit] = 'R' if re.search('^RESERVED', col[2], re.I) else attribute_rw[1]

                        if DEBUG_table6: print header_table6, 'attribute_bit(%r)'%(attribute_bit)
                        try:
                            attribute_rw = memory_attribute_page_dict[pp_nnn]
                        except KeyError:
                            # key not match, look for pp_xxx-xxx format
                            for key in memory_attribute_page_dict.keys():
                                matchobj1 = re.search('(\d\d)_(\d+)-(\d+)', key)
                                if matchobj1:
                                    page = int(matchobj1.group(1))
                                    start_addr = int(matchobj1.group(2))
                                    end_addr = int(matchobj1.group(3))
                                    if page == int(pp) and start_addr <= int(nnn) <= end_addr:
                                        attribute_rw = memory_attribute_page_dict[key]
                                        break

                        if DEBUG_table6: print header_table6, 'pp_nnn(%r)'%(pp_nnn)
                        if DEBUG_table6: print header_table6, 'attribute_bit(%r)'%(attribute_bit)
                        if DEBUG_table6: print header_table6, 'len(attribute_bit)(%r)'%(len(attribute_bit))
                        #if DEBUG_table6: print header_table6, 'memory_attribute_dict[pp_nnn](%r)'%(memory_attribute_dict[pp_nnn])

                        pp_col = '{pp}_{nnn}-{nn2}'.format(**locals()) if nn2 != None else pp_nnn

                        memory_attribute_dict[pp_col] = attribute_rw[0]
                        if ending_bit == 0:
                            for bit in range(7,-1,-1):
                                memory_attribute_dict[pp_col] = memory_attribute_dict[pp_col] + ',' + attribute_bit[bit]
                            del attribute_bit 
                        #if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'memory_attribute_dict[pp_col](%r)'%(memory_attribute_dict[pp_col])
                        if DEBUG_byte_148: print header_byte_148,'pp_col(%r). memory_attribute_dict[pp_col](%r)'%(pp_col, memory_attribute_dict[pp_col])
                        if DEBUG_byte_148 and '148' in col[0]: print header_byte_148,'pp_col(%r). memory_attribute_dict[pp_col](%r)'%(pp_col, memory_attribute_dict[pp_col])

    # Post fix: After scanning all the table, fix some
    # - DDM are in pair.  table 11 list them as 2 row, one for MSB, one for LSB
    # - DDM are in pair and 2 byte only.  table 11 list them as 30-33, table 12 too
    DEBUG_ddm = True
    if DEBUG_ddm: header_ddm = '>>>DEBUG_ddm:\t'
    first_ddm_addr = 22
    last_ddm_addr = 81
    for byte in range(first_ddm_addr, last_ddm_addr+1, 2):
        try:
            # the case where MSB and LSB are on different entry
            pp_nnn = '00_%03d'%(byte)
            pp_nn2 = '00_%03d'%(byte+1)
            pp_col = '00_%03d-%03d'%(byte, byte+1)

            # ensure the seperate MSB and LSB
            memory_attribute_dict[pp_nn2]
            memory_attribute_dict[pp_nnn]
            memory_attribute_dict[pp_col] = memory_attribute_dict[pp_nnn]
            del memory_attribute_dict[pp_nn2], memory_attribute_dict[pp_nnn]
        except KeyError:
            if DEBUG_ddm: print header_ddm, 'exception byte(%d)'%(byte)
            # we need to see how many byte were in the pp_nnn-nn2 format
            if byte == 30:
                pp_col = '00_%03d-%03d'%(30, 33)
                for new_byte in range(30, 33, 2):
                    pp_col_new = '00_%03d-%03d'%(new_byte, new_byte+1)
                    memory_attribute_dict[pp_col_new] = memory_attribute_dict[pp_col]
                del memory_attribute_dict[pp_col]
            elif byte == 58:
                pp_col = '00_%03d-%03d'%(58, 65)
                for new_byte in range(58, 65, 2):
                    pp_col_new = '00_%03d-%03d'%(new_byte, new_byte+1)
                    memory_attribute_dict[pp_col_new] = memory_attribute_dict[pp_col]
                del memory_attribute_dict[pp_col]
            elif byte == 66:
                pp_col = '00_%03d-%03d'%(66, 81)
                for new_byte in range(66, 81, 2):
                    pp_col_new = '00_%03d-%03d'%(new_byte, new_byte+1)
                    memory_attribute_dict[pp_col_new] = memory_attribute_dict[pp_col]
                del memory_attribute_dict[pp_col]

    # Post fix: After scanning all the table, fix some
    #  108-109 aer in pair, but table 18 list them as two row
    if True:
        byte = 108
        try:
            # the case where MSB and LSB are on different entry
            pp_nnn = '00_%03d'%(byte)
            pp_nn2 = '00_%03d'%(byte+1)
            pp_col = '00_%03d-%03d'%(byte, byte+1)

            # ensure the seperate MSB and LSB
            memory_attribute_dict[pp_nn2]
            memory_attribute_dict[pp_nnn]
            memory_attribute_dict[pp_col] = memory_attribute_dict[pp_nnn]
            del memory_attribute_dict[pp_nn2], memory_attribute_dict[pp_nnn]
        except KeyError:
            pass

    memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
    memory_attribute_dict_key.sort()

    if DEBUG_ddm:
        for key in memory_attribute_dict_key:
            print header_ddm, 'memory_attribute_dict_key(%r)'%(key)

    
    DEBUG_memory_attribute = False
    if DEBUG_memory_attribute: print '>>>DEBUG_memory_attribute', len(memory_attribute_dict), len(memory_attribute_dict_key), 'BEFORE'
    for idx in range(len(memory_attribute_dict_key)-1, -1, -1):
        # a little tricky: remove the entry that is in both the memory map table and in byte table, but the range in memory map table covered wider ending address that should be removed
        if memory_attribute_dict_key[idx-1] in memory_attribute_dict_key[idx]:
            if memory_attribute_dict_key[idx-1] in memory_attribute_dict_key[idx]:
                if DEBUG_memory_attribute: print '>>>DEBUG_memory_attribute', 'DELETE', memory_attribute_dict_key[idx]
                del memory_attribute_dict[memory_attribute_dict_key[idx]]
                memory_attribute_dict_key.pop(idx)

    if DEBUG_memory_attribute: print '>>>DEBUG_memory_attribute', len(memory_attribute_dict), len(memory_attribute_dict_key), 'AFTER'
    return memory_attribute_dict #, memory_attribute_dict_key

def create_memory_bit_property_csv(source_dir, formfactor, category, memory_map, memory_attribute_dict, template_full_path ):
    #
    DEBUG_create_memory_bit_property_csv = True
    if DEBUG_create_memory_bit_property_csv: header = '>>>DEBUG_create_memory_bit_property_csv:\t'
    memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
    memory_attribute_dict_key.sort()
    lineOUT_list = []
    for pp_nnn in memory_attribute_dict_key:
        
        print 'pp_nnn %-12s'%(pp_nnn), memory_attribute_dict[pp_nnn]
        if False:
            lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
        else:
            # Check if this line and the previous line has the overlapped address. They can differ only by 1
            if len(lineOUT_list) == 0:
                lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
            else:
                curr_pp_nnn = pp_nnn
                prev_pp_nnn = lineOUT_list[-1].split(',')[0]
                prev_pp, prev_nnn = prev_pp_nnn.split('_')
                curr_pp, curr_nnn = curr_pp_nnn.split('_')
                try:
                    prev_start, prev_end = prev_nnn.split('-')
                    prev_start = int(re.sub('^0{0-2}', '', prev_start)) # remove 0, 1 or 2 leading 0 in the string
                    prev_end = int(re.sub('^0{0-2}', '', prev_end)) # remove 0, 1 or 2 leading 0 in the string
                except ValueError:
                    prev_start = prev_end = int(re.sub('^0{0-2}', '', prev_nnn)) # remove 0, 1 or 2 leading 0 in the string
                
                try:
                    curr_start, curr_end = curr_nnn.split('-')
                    curr_start = int(re.sub('^0{0-2}', '', curr_start)) # remove 0, 1 or 2 leading 0 in the string
                    curr_end = int(re.sub('^0{0-2}', '', curr_end)) # remove 0, 1 or 2 leading 0 in the string
                except ValueError:
                    curr_start = curr_end = int(re.sub('^0{0-2}', '', curr_nnn)) # remove 0, 1 or 2 leading 0 in the string

                #prev_pp = int(re.sub('^0', '', prev_pp[1:])) # remove single leading 0 in the string
                #curr_pp = int(re.sub('^0', '', curr_pp[1:])) # remove single leading 0 in the string
                #prev_pp = int(prev_pp[2:]) # remove 'p" and single leading 0 in the string
                #curr_pp = int(curr_pp[2:]) # remove 'p" and single leading 0 in the string

                DEBUG_csv = False
                if DEBUG_csv: header = '>>>DEBUG_csv:\t'
                if DEBUG_csv: print 
                if DEBUG_csv: print header, 
                if DEBUG_csv: print memory_map, 'prev_pp_nnn(%r)'%(prev_pp_nnn)
                if DEBUG_csv: print memory_map, 'prev_pp(%r),\t curr_pp(%r),\t curr_start(%r),\t prev_end(%r)'%(prev_pp,curr_pp,curr_start,prev_end),
                if DEBUG_csv: print 'xxx'*4, (prev_pp[1:] == curr_pp and curr_start - prev_end == 1)
                #if prev_pp[1:] == curr_pp and curr_start - prev_end == 1:
                    #lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
            
                if prev_pp[1:] != curr_pp:
                    # page changed: add it
                    lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
                elif curr_start - prev_end == 1:
                    # same page changed, and contiguous: add it
                    lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
        if DEBUG_create_memory_bit_property_csv: print header, memory_map, 'lineOUT_list[-1]', lineOUT_list[-1]

    target_file = source_dir.replace('.csv', '_bit_property_%s.csv'%memory_map)
    if DEBUG_create_memory_bit_property_csv: print header, 'create target_file(%r)'%(target_file)
    fileOUT = open( target_file, "w+")
    fileOUT.writelines(lineOUT_list )
    fileOUT.close()
    for lineOUT in lineOUT_list:
        print 'lineOUT', lineOUT

#def create_all_python_mem_test_script(source_dir, formfactor, category, target_dir, mict, template_full_path, pending_cdb='fast', twr='40ms', bus_clock='400khz', customer=''):
def create_all_python_mem_test_script(source_dir='',
                                      formfactor='',
                                      category='',
                                      target_dir='',
                                      dict='',
                                      template_full_path='',
                                      pending_cdb='fast',
                                      twr='40ms',
                                      bus_clock='400khz',
                                      customer='',
                                      memory_map='msa',
                                      ):

    """ 
    Parameter:
        source_dir
        formfactor
        category
        target_dir
        memory_attribute_dict
        template_full_path
    return: TBD
    """

    memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
    memory_attribute_dict_key.sort()
    for pp_nnn in memory_attribute_dict_key:
        print 'pp_nnn %-12s'%(pp_nnn), memory_attribute_dict[pp_nnn]

    DEBUG = True
    if DEBUG: print
    if DEBUG: print 'DEBUG_xxx', 'source_dir\t', source_dir
    if DEBUG: print 'DEBUG_xxx', 'formfactor\t', formfactor
    if DEBUG: print 'DEBUG_xxx', 'category\t', category
    if DEBUG: print 'DEBUG_xxx', 'target_dir\t', target_dir
    if DEBUG: print 'DEBUG_xxx', 'memory_attribute_dict\t', memory_attribute_dict
    if DEBUG: print 'DEBUG_xxx', 'template_full_path\t', template_full_path
    if DEBUG: print
    if DEBUG: print 'DEBUG_xxx', os.path.split(template_full_path)
    if DEBUG: print 'DEBUG_xxx', os.path.split(source_dir)
    if DEBUG: print
    #if DEBUG: 
    #    # Build csv output full path
    #    if DEBUG: print 'DEBUG_xxx', 'csv_full_path',  csv_full_path  

    # Create the directory if not exist yet
    try:
        os.mkdir(target_dir)
    except Exception:
        pass

    if DEBUG: print

    DEBUG_yyy = True

    new_target_root = target_dir
    # The order of these lines defines the subdirectories path. The last one is highest in the directory path

    new_target_root = os.path.join(new_target_root, customer)
    if DEBUG_yyy: print 'DEBUG__yyy', 'new_target_root(%r)'%(new_target_root)

    new_target_root = os.path.join(new_target_root, memory_map)
    if DEBUG_yyy: print 'DEBUG__yyy', 'new_target_root(%r)'%(new_target_root)

    new_target_root = os.path.join(new_target_root, bus_clock)
    if DEBUG_yyy: print 'DEBUG__yyy', 'new_target_root(%r)'%(new_target_root)

    new_target_root = os.path.join(new_target_root, pending_cdb)
    if DEBUG_yyy: print 'DEBUG__yyy', 'new_target_root(%r)'%(new_target_root)

    new_target_root = os.path.join(new_target_root, twr)
    if DEBUG_yyy: print 'DEBUG__yyy', 'new_target_root(%r)'%(new_target_root)

    if not os.path.exists(new_target_root):
        print ">>> create directory:", new_target_root
        os.makedirs(new_target_root)

    # On this directory: if not exists yet, add script to this directory to change clock rate and restore clock rate to 400KHZ
    for template_name in ['000_set_i2c_bus.template', 'zzz_set_i2c_400khz.template']:
        target_file_name = template_name.replace('template', 'py')
        target_file = os.path.join(new_target_root, target_file_name)

        if not os.path.exists(target_file): 
            print 'DEBUG_file_path', 'target_file\t(%r)'%( target_file)

            template_full_name = os.path.join(template_full_path, template_name)
            fileIN = open(template_full_name, 'r')
            my_string = fileIN.read()
            fileIN.close()
            my_string = my_string.replace('NEW_i2c_bus_clock_rate', bus_clock.upper())
            print 'Create {target_file}'.format(**locals())
            fileOUT = open(target_file, 'w+')
            fileOUT.write(my_string)
            fileOUT.close()

    for pp_nnn in memory_attribute_dict.keys():
        # Select the correct template
        template_list = []

        if '119' in pp_nnn:
            template_list.append('119_122_rw_pwd0.template')
            template_list.append('119_122_wo_pwd0.template')
        elif '123' in pp_nnn:
            template_list.append('123_126_as_pwd.template')
            template_list.append('123_126_rw_pwd0.template')
            template_list.append('123_126_wo_pwd0.template')
        elif '127' in pp_nnn:
            template_list.append('127_____rw_pwd0.template')
            template_list.append('127_____sel_all_page.template')
            template_list.append('127_____sel_invalid_page.template')
            template_list.append('127_____sel_page.template')
            template_list.append('127_____sel_unique_page.template')
        else:
            if 'R0,W3' in memory_attribute_dict[pp_nnn]:
                if ',D' in memory_attribute_dict[pp_nnn]:
                    template_list.append('ro_changing.template')
                elif ',L' in memory_attribute_dict[pp_nnn]:
                    template_list.append('ro_latched.template')
                else:
                    template_list.append('ro_fixed.template')

                if ',R' in memory_attribute_dict[pp_nnn]:
                    template_list.append('ro_reserved.template')
            elif 'R0,W0' in memory_attribute_dict[pp_nnn]:
                template_list.append('rw_pwd0.template')
                if ',N' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd0_nonvolatile.template')
                elif ',V' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd0_volatile.template')
                if ',R' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd0_reserved.template')
            elif 'R0,W1' in memory_attribute_dict[pp_nnn]:
                template_list.append('rw_pwd1.template')
                if ',N' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd1_nonvolatile.template')
                elif ',V' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd1_volatile.template')
                if ',R' in memory_attribute_dict[pp_nnn]:
                    template_list.append('rw_pwd1_reserved.template')

        # extract address range and byte count
        #print 'pp_nnn %-12s'%(pp_nnn), memory_attribute_dict[pp_nnn]
        str_page, str_addr = pp_nnn.split('_')
        str_start_addr = str_addr.split('-')[0]
        str_end_addr = str_addr.split('-')[1] if len(str_addr.split('-')) == 2 else str_start_addr
        my_count = int(str_end_addr) - int(str_start_addr) + 1

        if ',R' in memory_attribute_dict[pp_nnn]:
            DEBUG = True
            if DEBUG: header = '>>>DEBUG:\t'
            if DEBUG: print header, 'memory_attribute_dict[{pp_nnn}](%r)'.format(**locals())%(memory_attribute_dict[pp_nnn])

            str_bit_pattern = re.sub('^R.,W.,.,', '', memory_attribute_dict[pp_nnn]) # expose only the bit attribute
            #str_bit_pattern = re.sub('[01XC ]', '0', str_bit_pattern)
            str_bit_pattern = re.sub('[01LCMPX ]', '0', str_bit_pattern)
            str_bit_pattern = str_bit_pattern.replace(',', '').replace('R', '1')
            str_bit_pattern = '0b{str_bit_pattern}'.format(**locals())
            str_bit_pattern = '%02X'%(int(str_bit_pattern, 2))
            str_bit_pattern = '0x%0{}X'.format(2*my_count)%(int(str_bit_pattern*my_count, 16)) # if more than 1 byte: make as many 'FF' as necessary
            if DEBUG: print header, 'str_bit_pattern[(%r)'%(str_bit_pattern)
        else:
            str_bit_pattern = '0'

        for template_name in template_list:

            template_full_name = os.path.join(template_full_path, template_name)
            fileIN = open(template_full_name, 'r')

            print 'DEBUG_file_path', 'template_full_name\t(%r)'%( template_full_name )
            print 'DEBUG_file_path', 'template_full_path\t(%r)'%( template_full_path)
            print 'DEBUG_file_path', 'template_name\t(%r)'%( template_name)
            print 'DEBUG_file_path', 'os.path.join(target_dir, template_full_name)\t(%r)'%( os.path.join(target_dir, template_full_name))
            print 'DEBUG_file_path' 

            my_string = fileIN.read()
            fileIN.close()

            # Change all the template keyword
            # The following is for DDM.  If they are same a

            # NEW_ddm_start_addr_1 and NEW_ddm_end_addr_1
            my_string = my_string.replace('NEW_ddm_start_addr_1', '22')
            my_string = my_string.replace('NEW_ddm_end_addr_1', '33')

            # NEW_ddm_start_addr_2 and NEW_ddm_end_addr_2
            my_string = my_string.replace('NEW_ddm_start_addr_2', '34')
            my_string = my_string.replace('NEW_ddm_end_addr_2', '81')

            # NEW_addr
            my_string = my_string.replace('NEW_addr', str(int(str_start_addr))) # address cannot have leading 0

            # NEW_byte_count
            my_string = my_string.replace('NEW_byte_count', str(my_count))

            # NEW_default_page_nu
            my_string = my_string.replace('NEW_default_page_nu', "0") # serial ID page

            # NEW_page_nu
            my_string = my_string.replace('NEW_page_nu', str(int(str_page))) # page number cannot have leading 0

            # NEW_pwd_host
            my_string = my_string.replace('NEW_pwd_host', "0x00001011")
            # NEW_Slv
            my_string = my_string.replace('NEW_Slv', "0xA0")

            # NEW_mask
            if my_count <= 2:
                my_string = my_string.replace('NEW_mask', "0x" + "FF"*my_count)
            else:
                my_string = my_string.replace('NEW_mask', "int('FF'*%d, 16)"%(my_count))

            # NEW_pattern
            if my_count <= 2:
                my_string = my_string.replace('NEW_pattern', "0x" + "5A"*my_count)
            else:
                my_string = my_string.replace('NEW_pattern', "int('5A'*%d, 16)"%(my_count))

            # The following is for non-volatile location. In QSFP, it is page2, 128-255

            # NEW_pwd1_page_nu 
            my_string = my_string.replace('NEW_pwd1_page_nu', '2')

            # NEW_pwd1_addr 
            my_string = my_string.replace('NEW_pwd1_addr', '128')

            # NEW_pwd1_byte_count 
            my_string = my_string.replace('NEW_pwd1_byte_count', '1')

            # NEW_pwd1_mask
            my_string = my_string.replace('NEW_pwd1_mask', '0xFF')

            # NEW_pwd1_pattern
            my_string = my_string.replace('NEW_pwd1_pattern', '0x5A')

            # nu of page high
            # NEW_highest_valid_page_nu
            my_string = my_string.replace('NEW_highest_valid_page_nu', '3')

            #NEW_t_reset_pulse 
            my_string = my_string.replace('NEW_t_reset_pulse', '2us')

            #NEW_reserved 
            my_string = my_string.replace('NEW_reserved', str_bit_pattern)

            # This script is executed with individual CDB or pending CDB
            if pending_cdb == 'no_pending':
                my_string = my_string.replace('dut1.p_run(locals())', '#')
                my_string = my_string.replace('dut1.p_', 'dut1.') # remove the pending command

            # This script is executed with long or short tWR
            twr_value = '0.6uS' if twr == 'short_twr' else '40mS'
            my_string = my_string.replace('NEW_twr', twr_value)

            # output file name in the format of p??_???_???_....py or p??_???_____....py
            if template_name.startswith('1'):
                # these are for 119_122, 123_126 and 127___
                target_file_name = 'p{str_page}_'.format(**locals()) + template_name.replace('template', 'py')
            else:
                if str_start_addr == str_end_addr:
                    target_file_name = 'p{str_page}_{str_start_addr}_____'.format(**locals()) + template_name.replace('template', 'py')
                else:
                    target_file_name = 'p{str_page}_{str_start_addr}_{str_end_addr}_'.format(**locals()) + template_name.replace('template', 'py')

            target_file = os.path.join(new_target_root, target_file_name)
            print 'DEBUG_file_path', 'target_file\t(%r)'%( target_file)

            print 'Create {target_file}'.format(**locals())
            fileOUT = open(target_file, 'w+')
            fileOUT.write(my_string)
            fileOUT.close()

if __name__ == '__main__':
    import sys

    import fnmatch
    import os

    print '*'*40
    for i in range(len(sys.argv)):
        print '*** argv[%d]'%(i), sys.argv[i]
        #if sys.argv[i].startswith('--i') and sys.argv[i].endswith('.csv') and "=" in sys.argv[i]:
        if sys.argv[i].startswith('--i') and "=" in sys.argv[i]:
            # looking for argument in "--input=xxxx.csv" format or "--i=xxxx.csv" format
            tmp_list = sys.argv[i].split('=')
            input_file=tmp_list[1]
        #elif sys.argv[i].startswith('--o') and sys.argv[i].endswith('.py') and "=" in sys.argv[i]:
        elif sys.argv[i].startswith('--o') and "=" in sys.argv[i]:
            # looking for argument in "--output=xxxx.py" format or "--o=xxxx.py" format
            tmp_list = sys.argv[i].split('=')
            output_file=tmp_list[1]

    # Verify arguments exist
    try:
        # Some message to the console
        print "*** Input file is <%s>" % (input_file)
        print "    Output file is <%s>" % (output_file)
        #main(input_file, output_file)

    except:
        print
        print " Error Need two arguments."
        print
        sys.exit()

    ## Define variables
    #memory_map_csv_file = input_file
    
    # Create template
    #(OLD) template_dir = 'input\\io\\template_cxp_tst'
    #(OLD) formfactor = 'topaz'
    #(OLD) create_all_python_mem_test_template (template_dir, formfactor)
    
#############################################################################################################`kkkkkkkkkkkkkkk

    # Find the formfactor which is part of the input XML file name
    #for formfactor_name in formfactor_name_list:
    #    # Look for file name contains known formfactor key words, "topaz", 'cxp" etc
    #    # e.g. source_file "Topaz_memory_map_A22.xml"
    #    if formfactor_name in input_file.lower():
    #        formfactor = this_formfactor = formfactor_name.upper()
    #        break
    formfactor = this_formfactor = 'QSFP'
    print 'this_formfactor =', formfactor


#NA    # verify the output is correct
#NA
#NA    fileIN = open( input_file, "r")
#NA    lineIN = fileIN.readline()
#NA
#NA    # Look for the last line that defines a Register
#NA    print
#NA    #print '*** Verify that "%s" produces correct "%s"' % (sys.argv[0], new_output_file)
#NA    #print '*** Verify that "%s" produces correct "%s"' % (sys.argv[0], new_output_file)
#NA    while lineIN:
#NA        # messy but works: get the last definition for Register
#NA        if lineIN.lower().startswith('register'):
#NA            saved_lineIN = lineIN
#NA        lineIN = fileIN.readline()
#NA    fileIN.close()
#NA

#(DO_NOT_DELETE)    try:
#(DO_NOT_DELETE)        print ">>> Executing execfile( %s)" % (new_output_file )
#(DO_NOT_DELETE)        execfile( new_output_file )
#(DO_NOT_DELETE)
#(DO_NOT_DELETE)        str2 = "*** PASS." if bulk_transfer_page.page == var_page else "*** FAIL."
#(DO_NOT_DELETE)        print str2 + ' The variable "bulk_transfer_page.page" should exist. Observed: %d, expect: %d' % ( bulk_transfer_page.page, var_page)
#(DO_NOT_DELETE)
#(DO_NOT_DELETE)        str2 = "*** PASS." if bulk_transfer_page.count == var_count else "*** FAIL."
#(DO_NOT_DELETE)        print str2 + ' The variable "bulk_transfer_page.count" should exist. Observed: %d, expect: %d' % ( bulk_transfer_page.count, var_count)
#(DO_NOT_DELETE)
#(DO_NOT_DELETE)        str2 = "*** PASS." if bulk_transfer_page.size == var_size else "*** FAIL."
#(DO_NOT_DELETE)        print str2 + ' The variable "bulk_transfer_page.size" should exist. Observed: %d, expect: %d' % ( bulk_transfer_page.size, var_size)
#(DO_NOT_DELETE)
#(DO_NOT_DELETE)    except:
#(DO_NOT_DELETE)        print
#(DO_NOT_DELETE)        print 'Error: The output file %s should have expected variable name %s and have %s.page, %s.count and %s.size' % (new_output_file, var_name, var_name, var_name, var_name)
#(DO_NOT_DELETE)        print
#(DO_NOT_DELETE)        sys.exit()

    # Create individual test scripts
    # Opend a templace, replace NEW_??? into actaul name and write to each .py test script
    print input_file
    # source_file = 'output\\memory\\topaz'
    #csv_file = os.path.join(input_file, "SFF-8636 rev23 QSFP Managemente Interface from docx_all_table.csv")

    source_dir = input_file
    target_dir = output_file # directory to place the template and script

    category = 'msa' # msa, finisar or customer

    print
    print ">>> Creating all python test scripts "

    # copy template to target_dir
    # copy 
    #   C:\Workspace2\frt_auto_gen\product\qsfp\app_input\template_memory
    #    to 
    #   target_dir 
    #   C:\Workspace2\frt_auto_gen\product\qsfp\memory
    #
    import shutil


    # Create a dictionary for each byte or each range of byte that is spf byte that is specifiied in the memory table
    ## e.g. '00_000': R0,W3,V,X,X,X,X,X,X,X,X
    # e.g. '00_000': R0,W3,N,X,X,X,X,X,X,X,X
    memory_attribute_dict = create_memory_map_dictionary ( source_dir, formfactor, category)
    template_full_path = r'C:\Workspace2\frt_auto_gen\product\qsfp\app_input\template_memory'

#################
    # Check the above function covers the whole mem range (128 byte each page)

    DEBUG_show_mem_map = True
    if DEBUG_show_mem_map: header_show_mem_map = '>>>DEBUG_show_mem_map:\t'
    if DEBUG_show_mem_map:
        for k, v in memory_attribute_dict.items():
            print header_show_mem_map, 'here', 'k', k ,'v', v

    if DEBUG_show_mem_map:
        memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
        memory_attribute_dict_key.sort()

        for key in memory_attribute_dict_key:
            print header_show_mem_map, 'memory_attribute_dict_key(%r)'%(key)

    if True:
        memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
        memory_attribute_dict_key.sort()
        memory_test_coverage_dict = {}
        total_page_nu = 4 # QSFP has page 0, 1, 2, 3
        for page_nu in range(total_page_nu):
            memory_test_coverage_dict[page_nu] = [0 for z in range(256)] # '0'*256 # 0 means not defined
        for key in memory_attribute_dict_key:
           # e.g. '00_070-071'
           page_nu, this_byte_range = key.split('_')
           if len(this_byte_range.split('-')) == 1:
               this_first_byte = this_byte_range.split('-')[0]
               this_last_byte = this_first_byte
           else:
               this_first_byte, this_last_byte = this_byte_range.split('-')

           #if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu(%r)'%(page_nu)
           #if DEBUG_show_mem_map: print header_show_mem_map, 'this_first_byte(%r)'%(this_first_byte)
           #if DEBUG_show_mem_map: print header_show_mem_map, 'this_last_byte(%r)'%(this_last_byte)

           page_nu = int(page_nu)
           this_first_byte = int(this_first_byte)
           this_last_byte = int(this_last_byte)
           
           for this_byte in range(this_first_byte, this_last_byte+1):
                if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu(%r)'%(page_nu), 'this_byte(%r)'%(this_byte)
                if DEBUG_show_mem_map: print header_show_mem_map, 'memory_test_coverage_dict[{page_nu}][{this_byte}]='.format(**locals()), memory_test_coverage_dict[page_nu][this_byte], 'BEFORE'
                memory_test_coverage_dict[page_nu][this_byte] = 1 # 1 means this byte of this page was defined
                if DEBUG_show_mem_map: print header_show_mem_map, 'memory_test_coverage_dict[{page_nu}][{this_byte}]='.format(**locals()), memory_test_coverage_dict[page_nu][this_byte], 'AFTER'
           if DEBUG_show_mem_map: print header_show_mem_map, '-'*80

        for page_nu in range(total_page_nu):
            if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu', page_nu, memory_test_coverage_dict[page_nu]

            if page_nu == 0:
                for this_byte in range(256):
                    if memory_test_coverage_dict[page_nu][this_byte] == 0:
                        print '>>>>>ERROR: no memory test for page {page_nu} byte {this_byte}'.format(**locals()) 
            else: 
                for this_byte in range(128, 256):
                    if memory_test_coverage_dict[page_nu][this_byte] == 0:
                        print '>>>>>ERROR: no memory test for page {page_nu} byte {this_byte}'.format(**locals()) 


    
    # memory map change
    # LR: Finisar Serial ID page deviated from MSA, i.e. it is set to host password writable, instead of RO, etc
    # EDR: Finisar Serial ID page deviated from MSA, i.e. it is set to host password writable, instead of RO, and P3 is no longer RO neither, etc.

    #             MSA  MSA-cisco  LR-gen1  LR-gen1 Cisco   EDR  EDR-Cisco
    # 106 RW      W0   W3         W0       W3              W0   W3 
    # P0  RO      W3   W3         W3       W3              W1   W1 
    # P3  RO      W3   W3         W3       W3              W1   W1 
    # P3  RW      W0   W0         W0       W0              W1   W1 

    #for customer in ('non_cisco', 'cisco'): # Cisco change byte 106, and change polarity of byte2 bit 0
    saved_memory_attribute_dict = memory_attribute_dict.copy()
    DEBUG_saved_memory_attribute_dict = True
    header = '>>>DEBUG_saved_memory_attribute_dict\t'
    if DEBUG_saved_memory_attribute_dict:
        #for junk in saved_memory_attribute_dict:
        for junk, v in saved_memory_attribute_dict.items():
            if True:
                if '128' in junk: print header, 'saved_memory_attribute_dict:', junk, v
            else:
                print header, 'saved_memory_attribute_dict:', junk, v

    for customer in ('', 'cisco'): # Cisco change byte 106, and change polarity of byte2 bit 0
        DEBUG_memory_map_list = False
        if DEBUG_memory_map_list:
            memory_map_list = ['msa']
        else:
            memory_map_list = ['msa', 'lr', 'edr']
        #for memory_map in ('msa', 'lr', 'edr'):
        for memory_map in memory_map_list:
            memory_attribute_dict = saved_memory_attribute_dict.copy()
            if memory_map == 'msa':
                pass # no change to change the protection type of any page
            elif memory_map == 'lr':
                # Finisar change proection of serial ID
                page_nu_serial_id = 0
                for pp_nnn in memory_attribute_dict:
                    if int(pp_nnn.split('_')[0]) == page_nu_serial_id and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
                        # Change Serial ID page to W1, and to 'Nonvolatile'
                        DEBUG_memory_map_lr = True
                        if DEBUG_memory_map_lr: header = '>>>DEBUG_memory_map_lr:\t'
                        if DEBUG_memory_map_lr: print header, pp_nnn, 'Before change: memory_attribute_dict[pp_nnn]', memory_attribute_dict[pp_nnn]
                        memory_attribute_dict[pp_nnn] = re.sub('^R.,W.,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
                        if DEBUG_memory_map_lr: print header, pp_nnn, 'After  change: memory_attribute_dict[pp_nnn]', memory_attribute_dict[pp_nnn]
            elif memory_map == 'edr':
                # Finisar change proection of serial ID
                page_nu_serial_id = 0
                for pp_nnn in memory_attribute_dict:
                    if int(pp_nnn.split('_')[0]) == page_nu_serial_id and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
                        # Change Serial ID page to W1, and to 'Nonvolatile'
                        memory_attribute_dict[pp_nnn] = re.sub('^R.,W.,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
                # page 3 protection was changed in EDR
                page_nu_3 = 3
                for pp_nnn in memory_attribute_dict:
                    if int(pp_nnn.split('_')[0]) == page_nu_3 and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
                        # Change Page 3 from W3 to W1
                        memory_attribute_dict[pp_nnn] = re.sub('^R0,W3,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
                        # Change page 3 from W0 to W1?
                        memory_attribute_dict[pp_nnn] = re.sub('^R0,W0,.,', 'R0,W1,V,', memory_attribute_dict[pp_nnn] )

            #target_root = os.path.join(target_dir, memory_map)
            target_root = target_dir

            # Create Python test script (default: pending, tWR=40ms)
            for bus_clock in ['400khz', '100khz']:
                for pending_cdb in ['pending', 'no_pending']:
                    for twr in ['short_twr', 'long_twr']:
                        #create_all_python_mem_test_script (source_dir, formfactor, category, target_dir + '_' + memory_map, memory_attribute_dict, template_full_path, pending_cdb=pending_cdb, twr=twr, bus_clock=bus_clock )
                        #create_all_python_mem_test_script (source_dir, formfactor, category, target_root, memory_attribute_dict, template_full_path, pending_cdb=pending_cdb, twr=twr, bus_clock=bus_clock, customer=customer )
                        create_all_python_mem_test_script (source_dir=source_dir,
                                                           formfactor=formfactor,
                                                           category=category,
                                                           target_dir=target_root,
                                                           dict=memory_attribute_dict,
                                                           template_full_path=template_full_path,
                                                           pending_cdb=pending_cdb,
                                                           twr=twr,
                                                           bus_clock=bus_clock,
                                                           customer=customer,
                                                           memory_map=memory_map,
                                                           )

            # Create complete property bit-by-bit for every bit
            create_memory_bit_property_csv (source_dir, formfactor, category, memory_map, memory_attribute_dict, template_full_path )
