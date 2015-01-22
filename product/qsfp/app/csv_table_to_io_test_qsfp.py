#///////////////////////////////////////////////////////////////////
# Produce io test scripts form template and from a fixed memory CSV file, which is from a memory map XLS/XLSX file 
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
                                        
                                                                                                                                                                                                                                                
def create_memory_bit_property_csv(source_dir, formfactor, category, memory_map, memory_attribute_dict, target_dir ):
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


def create_io_test_script_list(source_dir, formfactor, category, memory_map, memory_attribute_dict, target_dir ):
    #
    DEBUG_create_io_test_script_list = True
    if DEBUG_create_io_test_script_list: header = '>>>DEBUG_create_io_test_script_list:\t'
#NA_FOR_IO    memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
#NA_FOR_IO    memory_attribute_dict_key.sort()
#NA_FOR_IO    lineOUT_list = []
#NA_FOR_IO    for pp_nnn in memory_attribute_dict_key:
#NA_FOR_IO        
#NA_FOR_IO        print 'pp_nnn %-12s'%(pp_nnn), memory_attribute_dict[pp_nnn]
#NA_FOR_IO        if False:
#NA_FOR_IO            lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
#NA_FOR_IO        else:
#NA_FOR_IO            # Check if this line and the previous line has the overlapped address. They can differ only by 1
#NA_FOR_IO            if len(lineOUT_list) == 0:
#NA_FOR_IO                lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
#NA_FOR_IO            else:
#NA_FOR_IO                curr_pp_nnn = pp_nnn
#NA_FOR_IO                prev_pp_nnn = lineOUT_list[-1].split(',')[0]
#NA_FOR_IO                prev_pp, prev_nnn = prev_pp_nnn.split('_')
#NA_FOR_IO                curr_pp, curr_nnn = curr_pp_nnn.split('_')
#NA_FOR_IO                try:
#NA_FOR_IO                    prev_start, prev_end = prev_nnn.split('-')
#NA_FOR_IO                    prev_start = int(re.sub('^0{0-2}', '', prev_start)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO                    prev_end = int(re.sub('^0{0-2}', '', prev_end)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO                except ValueError:
#NA_FOR_IO                    prev_start = prev_end = int(re.sub('^0{0-2}', '', prev_nnn)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO                
#NA_FOR_IO                try:
#NA_FOR_IO                    curr_start, curr_end = curr_nnn.split('-')
#NA_FOR_IO                    curr_start = int(re.sub('^0{0-2}', '', curr_start)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO                    curr_end = int(re.sub('^0{0-2}', '', curr_end)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO                except ValueError:
#NA_FOR_IO                    curr_start = curr_end = int(re.sub('^0{0-2}', '', curr_nnn)) # remove 0, 1 or 2 leading 0 in the string
#NA_FOR_IO
#NA_FOR_IO                #prev_pp = int(re.sub('^0', '', prev_pp[1:])) # remove single leading 0 in the string
#NA_FOR_IO                #curr_pp = int(re.sub('^0', '', curr_pp[1:])) # remove single leading 0 in the string
#NA_FOR_IO                #prev_pp = int(prev_pp[2:]) # remove 'p" and single leading 0 in the string
#NA_FOR_IO                #curr_pp = int(curr_pp[2:]) # remove 'p" and single leading 0 in the string
#NA_FOR_IO
#NA_FOR_IO                DEBUG_csv = False
#NA_FOR_IO                if DEBUG_csv: header = '>>>DEBUG_csv:\t'
#NA_FOR_IO                if DEBUG_csv: print 
#NA_FOR_IO                if DEBUG_csv: print header, 
#NA_FOR_IO                if DEBUG_csv: print memory_map, 'prev_pp_nnn(%r)'%(prev_pp_nnn)
#NA_FOR_IO                if DEBUG_csv: print memory_map, 'prev_pp(%r),\t curr_pp(%r),\t curr_start(%r),\t prev_end(%r)'%(prev_pp,curr_pp,curr_start,prev_end),
#NA_FOR_IO                if DEBUG_csv: print 'xxx'*4, (prev_pp[1:] == curr_pp and curr_start - prev_end == 1)
#NA_FOR_IO                #if prev_pp[1:] == curr_pp and curr_start - prev_end == 1:
#NA_FOR_IO                    #lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
#NA_FOR_IO            
#NA_FOR_IO                if prev_pp[1:] != curr_pp:
#NA_FOR_IO                    # page changed: add it
#NA_FOR_IO                    lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
#NA_FOR_IO                elif curr_start - prev_end == 1:
#NA_FOR_IO                    # same page changed, and contiguous: add it
#NA_FOR_IO                    lineOUT_list.append('p%s,%s\n'%(pp_nnn, memory_attribute_dict[pp_nnn]))
#NA_FOR_IO        if DEBUG_create_io_test_script_list: print header, memory_map, 'lineOUT_list[-1]', lineOUT_list[-1]

    print '>>>JUNK', source_dir, formfactor, category, memory_map, memory_attribute_dict, target_dir
    print '>>>JUNK', 'source_dir(%r), formfactor(%r), category(%r), memory_map(%r), memory_attribute_dict(%r), target_dir(%r)'%(source_dir, formfactor, category, memory_map, memory_attribute_dict, target_dir)
    source_file = source_dir.replace('.csv', '_bit_property_%s.csv'%memory_map)
    if DEBUG_create_io_test_script_list: print header, 'open source_file(%r)'%(source_file)
    fileIN = open(source_file, 'r')
    #lineIN_list = fileIN.read()
    lineIN_list = fileIN.readlines()
    fileIN.close()
    #if DEBUG_create_io_test_script_list: print header, 'lineIN_list', lineIN_list
    #if DEBUG_create_io_test_script_list: print header, 'len(lineIN_list', len(lineIN_list)

    cntl_bit_list = [
        # page, byte, nu_of_bit, name
        [0, 86, 1, 'tx_dis'],
        [0, 87, 2, 'rx_rate_sel'],
        [0, 88, 2, 'tx_rate_sel'],
        [0, 89, 8, 'rx_app_sel'],
        [0, 90, 8, 'rx_app_sel'],
        [0, 91, 8, 'rx_app_sel'],
        [0, 92, 8, 'rx_app_sel'],
        [0, 93, 1, 'hi_pwr_class',        'pwr_set', 'pwr_override'], #
        [0, 94, 8, 'tx_app_sel'],
        [0, 95, 8, 'tx_app_sel'],
        [0, 96, 8, 'tx_app_sel'],
        [0, 97, 8, 'tx_app_sel'],
        [0, 98, 1, 'tx_cdr',              'rx_cdr'],
        [0, 100, 1, 'mask_tx_los',        'mask_rx_los'],
        [0, 101, 1, 'mask_tx_adp_eq_flt', 'mask_tx_trans_flt'],
        [0, 102, 1, 'mask_tx_cdr_lol',    'mask_rx_cdr_lol'],
        [0, 103, 1, 'mask_temp'],
        [0, 104, 1, 'mask_vcc'],
        [3, 234, 4, 'tx_ipt_eq'], # start ch1
        [3, 235, 4, 'tx_ipt_eq'], # start ch1
        [3, 236, 4, 'rx_opt_emph'], # start ch1
        [3, 237, 4, 'rx_opt_emph'], # start ch1
        [3, 238, 4, 'rx_opt_amp'], # start ch1
        [3, 239, 4, 'rx_opt_amp'], # start ch1
        [3, 240, 1, 'rx_sq_dis',          'tx_sq_dis'],
        [3, 241, 1, 'rx_opt_dis',         'tx_adaptive_eq'],
        [3, 242, 1, 'mask_rx_pwr'], # start ch1
        [3, 243, 1, 'mask_rx_pwr'], # start ch3

        [3, 244, 1, 'mask_tx_bias'], # start ch1
        [3, 245, 1, 'mask_tx_bias'], # start ch3

        [3, 246, 1, 'mask_tx_pwr'], # start ch1
        [3, 247, 1, 'mask_tx_pwr'], # start ch3

    ]

    new_cntl_bit_list = cntl_bit_list[:] # make a copy
    # merge the first 2 element into pxx_yyy format
    for idx in range(len(new_cntl_bit_list)):
        new_cntl_bit_list[idx][0] = 'p%02d_%03d'%(new_cntl_bit_list[idx][0], new_cntl_bit_list[idx][1])
        #new_cntl_bit_list[idx] = new_cntl_bit_list[idx].pop(1) # discard the first elemente (byte nu)
        del new_cntl_bit_list[idx][1] # discard the elemente (byte nu)
    #position_by_bit =    ['p%02d_%03d'%(z[0], z[1]) for z in cntl_bit_list]
    position_by_bit = [z[0] for z in new_cntl_bit_list]

    for lineIN in lineIN_list:
        lineIN = lineIN.strip()
        #print '\n', 'lineIN', lineIN
        lineIN_token_list = lineIN.split(',')
        #if ',C' in lineIN or ',M' in lineIN:
        if 'C' in lineIN_token_list or 'M' in lineIN_token_list:
        #if 'C' in lineIN_token_list: # exclude mask, which is already seperate FRT
            #if DEBUG_create_io_test_script_list: print header, 'lineIN', lineIN
            position = lineIN_token_list[0] # e.g. p00_127
            
            #if any( position == str2 for str2 in position_by_bit):
            for this_cntl_bit_list in new_cntl_bit_list:
                if position == this_cntl_bit_list[0]: 
                    # Found the line that match our list
                    if this_cntl_bit_list[1] == 1: 
                        for idx in range(7, -1, -1):
                            #if DEBUG_create_io_test_script_list: print header, 'lineIN_token_list[7-idx+4]', lineIN_token_list[7-idx+4], 7-idx+4, idx
                            if lineIN_token_list[7-idx+4] == 'C' or lineIN_token_list[7-idx+4] == 'M':
                                try:
                                    # pick the correct name when bit 7-4 and 3-0 are for different control type
                                    name = this_cntl_bit_list[3] if idx <=3 else this_cntl_bit_list[2]
                                except IndexError: 
                                    name = this_cntl_bit_list[2]
                                    pass

                                target_file = '{position}_bit{idx}_{name}'.format(**locals())
                                target_file = os.path.join(target_dir, target_file)
                                if DEBUG_create_io_test_script_list: print header, 'creating file {target_file}'.format(**locals())
                    elif this_cntl_bit_list[1] == 2: 
                        for idx in ['7_6', '5_4','3_2', '1_0']:
                            name = this_cntl_bit_list[2]
                            target_file = '{position}_bit{idx}_{name}'.format(**locals())
                            target_file = os.path.join(target_dir, target_file)
                            if DEBUG_create_io_test_script_list: print header, 'creating file {target_file}'.format(**locals())
                    elif this_cntl_bit_list[1] == 4: 
                        for idx in ['7_4', '3_0']:
                            name = this_cntl_bit_list[2]
                            target_file = '{position}_bit{idx}_{name}'.format(**locals())
                            target_file = os.path.join(target_dir, target_file)
                            if DEBUG_create_io_test_script_list: print header, 'creating file {target_file}'.format(**locals())
                    elif this_cntl_bit_list[1] == 8: 
                        #if not '-' in position: # skip the line with multiple byte, e.g. p0_105-1-6
                        #if DEBUG_create_io_test_script_list: print header, 'position {position}'.format(**locals())
                        if any( str2 in position for str2 in ['-', '119', '123', '127']):
                            pass
                        else:
                            # skip the line with multiple byte, e.g. p0_105-1-6
                            idx = '7_0'
                            name = this_cntl_bit_list[2]
                            target_file = '{position}_bit{idx}_{name}'.format(**locals())
                            target_file = os.path.join(target_dir, target_file)
                            if DEBUG_create_io_test_script_list: print header, 'creating file {target_file}'.format(**locals())

        #elif 'W' in lineIN_token_list:
        #    lineIN_token_list = lineIN.strip().split(',')
        #    position = lineIN_token_list[0] # e.g. p00_127
        #    if True:
        #            idx = '7_0'
        #            target_file = '{position}_bit{idx}'.format(**locals())
        #            target_file = os.path.join(target_dir, target_file)
        #            if DEBUG_create_io_test_script_list: print header, 'creating file {target_file}'.format(**locals())



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


#NA_FOR_IO    # Create a dictionary for each byte or each range of byte that is spf byte that is specifiied in the memory table
#NA_FOR_IO    ## e.g. '00_000': R0,W3,V,X,X,X,X,X,X,X,X
#NA_FOR_IO    # e.g. '00_000': R0,W3,N,X,X,X,X,X,X,X,X
#NA_FOR_IO    memory_attribute_dict = create_memory_map_dictionary ( source_dir, formfactor, category)
#NA_FOR_IO    template_full_path = r'C:\Workspace2\frt_auto_gen\product\qsfp\app_input\template_memory'
#NA_FOR_IO
#NA_FOR_IO#################
#NA_FOR_IO    # Check the above function covers the whole mem range (128 byte each page)
#NA_FOR_IO
#NA_FOR_IO    DEBUG_show_mem_map = True
#NA_FOR_IO    if DEBUG_show_mem_map: header_show_mem_map = '>>>DEBUG_show_mem_map:\t'
#NA_FOR_IO    if DEBUG_show_mem_map:
#NA_FOR_IO        for k, v in memory_attribute_dict.items():
#NA_FOR_IO            print header_show_mem_map, 'here', 'k', k ,'v', v
#NA_FOR_IO
#NA_FOR_IO    if DEBUG_show_mem_map:
#NA_FOR_IO        memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
#NA_FOR_IO        memory_attribute_dict_key.sort()
#NA_FOR_IO
#NA_FOR_IO        for key in memory_attribute_dict_key:
#NA_FOR_IO            print header_show_mem_map, 'memory_attribute_dict_key(%r)'%(key)
#NA_FOR_IO
#NA_FOR_IO    if True:
#NA_FOR_IO        memory_attribute_dict_key = sorted(memory_attribute_dict, key=memory_attribute_dict.get)
#NA_FOR_IO        memory_attribute_dict_key.sort()
#NA_FOR_IO        memory_test_coverage_dict = {}
#NA_FOR_IO        total_page_nu = 4 # QSFP has page 0, 1, 2, 3
#NA_FOR_IO        for page_nu in range(total_page_nu):
#NA_FOR_IO            memory_test_coverage_dict[page_nu] = [0 for z in range(256)] # '0'*256 # 0 means not defined
#NA_FOR_IO        for key in memory_attribute_dict_key:
#NA_FOR_IO           # e.g. '00_070-071'
#NA_FOR_IO           page_nu, this_byte_range = key.split('_')
#NA_FOR_IO           if len(this_byte_range.split('-')) == 1:
#NA_FOR_IO               this_first_byte = this_byte_range.split('-')[0]
#NA_FOR_IO               this_last_byte = this_first_byte
#NA_FOR_IO           else:
#NA_FOR_IO               this_first_byte, this_last_byte = this_byte_range.split('-')
#NA_FOR_IO
#NA_FOR_IO           #if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu(%r)'%(page_nu)
#NA_FOR_IO           #if DEBUG_show_mem_map: print header_show_mem_map, 'this_first_byte(%r)'%(this_first_byte)
#NA_FOR_IO           #if DEBUG_show_mem_map: print header_show_mem_map, 'this_last_byte(%r)'%(this_last_byte)
#NA_FOR_IO
#NA_FOR_IO           page_nu = int(page_nu)
#NA_FOR_IO           this_first_byte = int(this_first_byte)
#NA_FOR_IO           this_last_byte = int(this_last_byte)
#NA_FOR_IO           
#NA_FOR_IO           for this_byte in range(this_first_byte, this_last_byte+1):
#NA_FOR_IO                if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu(%r)'%(page_nu), 'this_byte(%r)'%(this_byte)
#NA_FOR_IO                if DEBUG_show_mem_map: print header_show_mem_map, 'memory_test_coverage_dict[{page_nu}][{this_byte}]='.format(**locals()), memory_test_coverage_dict[page_nu][this_byte], 'BEFORE'
#NA_FOR_IO                memory_test_coverage_dict[page_nu][this_byte] = 1 # 1 means this byte of this page was defined
#NA_FOR_IO                if DEBUG_show_mem_map: print header_show_mem_map, 'memory_test_coverage_dict[{page_nu}][{this_byte}]='.format(**locals()), memory_test_coverage_dict[page_nu][this_byte], 'AFTER'
#NA_FOR_IO           if DEBUG_show_mem_map: print header_show_mem_map, '-'*80
#NA_FOR_IO
#NA_FOR_IO        for page_nu in range(total_page_nu):
#NA_FOR_IO            if DEBUG_show_mem_map: print header_show_mem_map, 'page_nu', page_nu, memory_test_coverage_dict[page_nu]
#NA_FOR_IO
#NA_FOR_IO            if page_nu == 0:
#NA_FOR_IO                for this_byte in range(256):
#NA_FOR_IO                    if memory_test_coverage_dict[page_nu][this_byte] == 0:
#NA_FOR_IO                        print '>>>>>ERROR: no memory test for page {page_nu} byte {this_byte}'.format(**locals()) 
#NA_FOR_IO            else: 
#NA_FOR_IO                for this_byte in range(128, 256):
#NA_FOR_IO                    if memory_test_coverage_dict[page_nu][this_byte] == 0:
#NA_FOR_IO                        print '>>>>>ERROR: no memory test for page {page_nu} byte {this_byte}'.format(**locals()) 
#NA_FOR_IO
#NA_FOR_IO
#NA_FOR_IO    
#NA_FOR_IO    # memory map change
#NA_FOR_IO    # LR: Finisar Serial ID page deviated from MSA, i.e. it is set to host password writable, instead of RO, etc
#NA_FOR_IO    # EDR: Finisar Serial ID page deviated from MSA, i.e. it is set to host password writable, instead of RO, and P3 is no longer RO neither, etc.
#NA_FOR_IO
#NA_FOR_IO    #             MSA  MSA-cisco  LR-gen1  LR-gen1 Cisco   EDR  EDR-Cisco
#NA_FOR_IO    # 106 RW      W0   W3         W0       W3              W0   W3 
#NA_FOR_IO    # P0  RO      W3   W3         W3       W3              W1   W1 
#NA_FOR_IO    # P3  RO      W3   W3         W3       W3              W1   W1 
#NA_FOR_IO    # P3  RW      W0   W0         W0       W0              W1   W1 
#NA_FOR_IO
#NA_FOR_IO    #for customer in ('non_cisco', 'cisco'): # Cisco change byte 106, and change polarity of byte2 bit 0
#NA_FOR_IO    saved_memory_attribute_dict = memory_attribute_dict.copy()
#NA_FOR_IO    DEBUG_saved_memory_attribute_dict = True
#NA_FOR_IO    header = '>>>DEBUG_saved_memory_attribute_dict\t'
#NA_FOR_IO    if DEBUG_saved_memory_attribute_dict:
#NA_FOR_IO        #for junk in saved_memory_attribute_dict:
#NA_FOR_IO        for junk, v in saved_memory_attribute_dict.items():
#NA_FOR_IO            if True:
#NA_FOR_IO                if '128' in junk: print header, 'saved_memory_attribute_dict:', junk, v
#NA_FOR_IO            else:
#NA_FOR_IO                print header, 'saved_memory_attribute_dict:', junk, v

    for customer in ('', 'cisco'): # Cisco change byte 106, and change polarity of byte2 bit 0
        DEBUG_memory_map_list = False
#NA_FOR_IO        if DEBUG_memory_map_list:
#NA_FOR_IO            memory_map_list = ['msa']
#NA_FOR_IO        else:
#NA_FOR_IO            memory_map_list = ['msa', 'lr', 'edr']

        memory_map_list = ['msa']

        for memory_map in memory_map_list:
#NA_FOR_IO            memory_attribute_dict = saved_memory_attribute_dict.copy()
#NA_FOR_IO            if memory_map == 'msa':
#NA_FOR_IO                pass # no change to change the protection type of any page
#NA_FOR_IO            elif memory_map == 'lr':
#NA_FOR_IO                # Finisar change proection of serial ID
#NA_FOR_IO                page_nu_serial_id = 0
#NA_FOR_IO                for pp_nnn in memory_attribute_dict:
#NA_FOR_IO                    if int(pp_nnn.split('_')[0]) == page_nu_serial_id and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
#NA_FOR_IO                        # Change Serial ID page to W1, and to 'Nonvolatile'
#NA_FOR_IO                        DEBUG_memory_map_lr = True
#NA_FOR_IO                        if DEBUG_memory_map_lr: header = '>>>DEBUG_memory_map_lr:\t'
#NA_FOR_IO                        if DEBUG_memory_map_lr: print header, pp_nnn, 'Before change: memory_attribute_dict[pp_nnn]', memory_attribute_dict[pp_nnn]
#NA_FOR_IO                        memory_attribute_dict[pp_nnn] = re.sub('^R.,W.,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
#NA_FOR_IO                        if DEBUG_memory_map_lr: print header, pp_nnn, 'After  change: memory_attribute_dict[pp_nnn]', memory_attribute_dict[pp_nnn]
#NA_FOR_IO            elif memory_map == 'edr':
#NA_FOR_IO                # Finisar change proection of serial ID
#NA_FOR_IO                page_nu_serial_id = 0
#NA_FOR_IO                for pp_nnn in memory_attribute_dict:
#NA_FOR_IO                    if int(pp_nnn.split('_')[0]) == page_nu_serial_id and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
#NA_FOR_IO                        # Change Serial ID page to W1, and to 'Nonvolatile'
#NA_FOR_IO                        memory_attribute_dict[pp_nnn] = re.sub('^R.,W.,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
#NA_FOR_IO                # page 3 protection was changed in EDR
#NA_FOR_IO                page_nu_3 = 3
#NA_FOR_IO                for pp_nnn in memory_attribute_dict:
#NA_FOR_IO                    if int(pp_nnn.split('_')[0]) == page_nu_3 and int(pp_nnn.split('_')[1].split('-')[0]) >= 128:
#NA_FOR_IO                        # Change Page 3 from W3 to W1
#NA_FOR_IO                        memory_attribute_dict[pp_nnn] = re.sub('^R0,W3,.,', 'R0,W1,N,', memory_attribute_dict[pp_nnn] )
#NA_FOR_IO                        # Change page 3 from W0 to W1?
#NA_FOR_IO                        memory_attribute_dict[pp_nnn] = re.sub('^R0,W0,.,', 'R0,W1,V,', memory_attribute_dict[pp_nnn] )


            #target_root = os.path.join(target_dir, memory_map)
            target_root = target_dir

#NA_FOR_IO            # Create Python test script (default: pending, tWR=40ms)
#NA_FOR_IO            for bus_clock in ['400khz', '100khz']:
#NA_FOR_IO                for pending_cdb in ['pending', 'no_pending']:
#NA_FOR_IO                    for twr in ['short_twr', 'long_twr']:
#NA_FOR_IO                        #create_all_python_mem_test_script (source_dir, formfactor, category, target_dir + '_' + memory_map, memory_attribute_dict, template_full_path, pending_cdb=pending_cdb, twr=twr, bus_clock=bus_clock )
#NA_FOR_IO                        #create_all_python_mem_test_script (source_dir, formfactor, category, target_root, memory_attribute_dict, template_full_path, pending_cdb=pending_cdb, twr=twr, bus_clock=bus_clock, customer=customer )
#NA_FOR_IO                        create_all_python_mem_test_script (source_dir=source_dir,
#NA_FOR_IO                                                           formfactor=formfactor,
#NA_FOR_IO                                                           category=category,
#NA_FOR_IO                                                           target_dir=target_root,
#NA_FOR_IO                                                           dict=memory_attribute_dict,
#NA_FOR_IO                                                           template_full_path=template_full_path,
#NA_FOR_IO                                                           pending_cdb=pending_cdb,
#NA_FOR_IO                                                           twr=twr,
#NA_FOR_IO                                                           bus_clock=bus_clock,
#NA_FOR_IO                                                           customer=customer,
#NA_FOR_IO                                                           memory_map=memory_map,
#NA_FOR_IO                                                           )

            # Create complete property bit-by-bit for every bit
            memory_attribute_dict = {}
            #template_full_path = r'C:\Workspace2\frt_auto_gen\product\qsfp\app_input\template_memory'
            template_full_path = r'C:\Workspace2\frt_auto_gen\product\qsfp\app_input\template_memory'
            print '>>>JUNK', source_dir, formfactor, category, memory_map, memory_attribute_dict, template_full_path
            create_io_test_script_list (source_dir, formfactor, category, memory_map, memory_attribute_dict, target_dir )
