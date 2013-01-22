#!/usr/bin/python

import os
import sys
import types
import imp
import serial
import fdpexpect
import traceback

from time import gmtime, strftime
from optparse import OptionParser

#Defining some runstp constants and variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #runstp root folder. Folder where runstp is located
TEST_SUITES_DIR = os.path.join(ROOT_DIR, 'test_suites') #runstp test suites directory. Folder where runstp test suites are located relative to ROOT_DIR
PLATFORMS_DIR = os.path.join(ROOT_DIR, 'platforms') #runstp platform info directory. Folder where runstp keeps files containing information related to the platforms like architecture, interfaces, etc
TEST_BIN_ROOT = os.path.join(ROOT_DIR, '..','binary') #compiled test binaries location
LOGS_ROOT_DIR = os.path.join(ROOT_DIR,'logs') #logs root folder

#Function to parse comma separated arguments
def runstp_parser(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

#Function to obtain possible test case candidates from the existing test cases
def get_test_case_candidates(root_folder, test_cases=None):
    result = []
    for folder in root_folder:
        for root, dirs, files in os.walk(folder):
            if root != os.path.join(TEST_SUITES_DIR,'templates'):
                for item in files:
                    if test_cases:
                        if item in test_cases:
                            result.append(os.path.join(root,item))
                    elif item.endswith('.py'):
                        result.append(os.path.join(root, item))
    
    return result

# Function to import templates in test cases with access to runstp object within the module. Python built-in import can not be used since modules are imported 
# in their one environment and runstp objects like platform will not be recognized by the imported module
def runstp_import(module_path):
    exec(compile(open(os.path.join(ROOT_DIR,module_path)).read(), module_path, 'exec'),None,None)
    
def print_message_and_exit(message):
    print (message)
    sys.exit(1)

#Defining the command line options for runstp
parser = OptionParser()

#Options to pass folder (test suites)
parser.add_option("-f", "--folders", 
          dest="folders", action="callback", callback=runstp_parser, type="string",
                  help="Execute runstp testsuites (comma separated)", metavar="FILE")
#Option to pass test cases
parser.add_option("-t", "--testcases",
                  action="callback", callback=runstp_parser, dest="testcases", type="string",
                  help="Execute runstp testcases (comma separated)")
#Option to pass platform
parser.add_option("-p", "--platform",
                  action="store", dest="platform", type="string",
                  help="Platform being used in the tests (mandatory)")
#Option to pass bench file
parser.add_option("-b", "--bench",
                  action="store", dest="bench_path", type="string", default=os.path.join(ROOT_DIR,'bench.py'),
                  help="File containing equipment connectivity and setup info (defaults to <runstp folder>/bench.py)")

#Option to pass bench file
parser.add_option("-c", "--compiler",
                  action="store", dest="compiler", type="string", default='gcc',
                  help="Compiler user to generate test case binaries (gcc,cgt_ccs,etc)")
          


#Parsing commad line arguments
(options, args) = parser.parse_args()

if not options.platform:
    print "Plaform -p/--plaform is mandatory"
    parser.print_help()
    sys.exit(1)
    
test_case_candidates = [] #test case candidates set
test_suite_candidates = [] #test suite candidates set

#Setting the folder to be searched for test case candidates
if options.folders:
    for folder in options.folders:
        test_suite_candidates.append(os.path.join(TEST_SUITES_DIR,folder))
else:	
    test_suite_candidates = [TEST_SUITES_DIR]

#Obtaining the test cases candidates if no options are passed or if -f is passed in the command line
if  not options.testcases or options.folders:
    test_case_candidates.extend(get_test_case_candidates(test_suite_candidates))

#Obtaining the test cases candidates if -t is passed in the command line
if options.testcases:
    test_case_candidates.extend(get_test_case_candidates([TEST_SUITES_DIR], options.testcases))

#Eliminating duplicate test cases from the list of candidates
test_case_candidates = set(test_case_candidates)

#Obtaining the platform specific information
try:
    platform_info = imp.load_source(options.platform,os.path.join(PLATFORMS_DIR, options.platform + '.py'))
    platform_features = []
    for item_string in dir(platform_info):
        if item_string not in ['__builtins__', '__doc__', '__file__', '__name__', '__package__']:
            item = getattr(platform_info, item_string)
            if isinstance(item,list):
                platform_features.extend(item)
            else:
                platform_features.append(item)
except Exception, e:
    print e
    print_message_and_exit ('Problem occurred while trying to obtain platform information for ' + options.platform +
                                          '. Make sure that a ' + options.platform + '.py file exists in ' + PLATFORMS_DIR + 
                                          ' and that no errors are present in the file.')

#Obtaining the physical setup of the board
from src.equipment_info import *
from src.site_info import *

try:
    exec(compile(open(options.bench_path).read(), options.bench_path, 'exec'), None, None)
except:
    print_message_and_exit ('Problem occurred while trying to parse ' + options.bench_path +
               '. Make sure that ' + options.bench_path + ' exists and that no errors are present in the file.')

#Verifying that ther is an entry for the platform in the bench file specified
if not platforms_list.has_key(options.platform):
    print_message_and_exit ('No entry found for ' + options.platform + ' in ' + options.bench_path)

# Creating link or copying in tftp root directory test binaries
cp_src = os.path.join(TEST_BIN_ROOT,platform_info.arch,options.compiler)

# Comment out the Link option section and uncomment the Copy option section 
# if copying of test binaries is preferred
# Link option
tftp_link = os.path.join(SITE_INFO['tftp_server_root'],options.compiler)
if os.path.exists(tftp_link):
    if os.readlink(tftp_link) != cp_src:
        print_message_and_exit ('Folder ' + tftp_link + ' already exists and it is not pointing to ' +  cp_src)
else:
    os.symlink(cp_src, os.path.join(SITE_INFO['tftp_server_root'],options.compiler))
# End of Link option
"""
#Copy option
#Copying test binaries to the tftpboot root directory
import shutil

for root, dirs, files in os.walk(cp_src):
    current_dst_dir = os.path.join(SITE_INFO['tftp_server_root'],root.replace(os.path.join(TEST_BIN_ROOT,platform_info.arch,''),''))
    if not os.path.exists(current_dst_dir):
        os.mkdir(current_dst_dir)
    for current_file in files:
        if not os.path.exists(os.path.join(current_dst_dir,current_file)):
            shutil.copy(os.path.join(root,current_file),current_dst_dir)
#End of Copy option
"""
tftp_base_path = options.compiler + '/' + platform_info.soc + '/' + platform_info.platform

#Running the appropriate test cases
test_results = {} #Results Dictionary

# Depending on compiler, setting appropriate go offset
go_offset = 0x854
if options.compiler == 'cgt_ccs':
    go_offset = 0x22d4

test_case_defs = os.path.join(TEST_SUITES_DIR,'templates','test_defaults.py')
exec(compile(open(test_case_defs).read(),test_case_defs, 'exec'),None,None)  #Importing the test case default values

serial_params = platforms_list[options.platform].serial_params
session_start_time = strftime("%a_%d_%b_%Y_%H.%M.%S", gmtime())
for testcase in test_case_candidates:
    try:
        requires = None
        exec(compile(open(testcase).read(), testcase, 'single'),None,None)
        if set(requires) <= set(platform_features):
            #Creating logs folder and log file
            test_case_log_folder = os.path.join(LOGS_ROOT_DIR,platform_info.arch,options.compiler,platform_info.soc,platform_info.platform,session_start_time) + testcase.replace(TEST_SUITES_DIR,'').replace('.py','')
            os.makedirs(test_case_log_folder)
            test_log_file = open(os.path.join(test_case_log_folder, platforms_list[options.platform].name + '_' + platforms_list[options.platform].buildId + '.log'), 'w+')
            #Initializing common vairables
            testresult = None
            load_address = default_load_address
            go_address = default_go_address
            print 'Running ' + testcase + ' at ' + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            #'port':'/dev/ttyUSB8', 'baudrate':19200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0
            serial_connection = serial.Serial(serial_params['port'])
            if serial_params['baudrate']:
                serial_connection.baudrate = serial_params['baudrate']
            if serial_params['bytesize']:
                serial_connection.bytesize = serial_params['bytesize']
            if serial_params['parity']:
                serial_connection.parity = serial_params['parity']
            if serial_params['stopbits']:
                serial_connection.stopbits = serial_params['stopbits']
            if serial_params['timeout']:
                serial_connection.timeout = serial_params['timeout']
            if serial_params['xonxoff']:
                serial_connection.xonxoff = serial_params['xonxoff']
            if serial_params['rtscts']:
                serial_connection.rtscts = serial_params['rtscts']
            platform = fdpexpect.fdspawn(serial_connection)
            platform.logfile = test_log_file
            exec(compile(open(testcase).read(), testcase, 'exec'),None,None)
            test_results[testcase.replace(TEST_SUITES_DIR,'')] = testresult 
            test_log_file.close
        else: 
            print 'Test ' + testcase + ' can not be run because platform ' + options.platform + ' does not have required interfaces '
    except Exception, e:
        print traceback.format_exc()
        test_results[testcase.replace(TEST_SUITES_DIR,'')]  = e 
        
print "\n\nResults summary"
for key, val in test_results.items():
    sys.stdout.write(key)
    sys.stdout.write('     ')
    sys.stdout.write("%r"%val)
    print('')
     
print '\n\nLogs for this session can be found at file://'+os.path.join(LOGS_ROOT_DIR,platform_info.arch,options.compiler,platform_info.soc,platform_info.platform,session_start_time) 

