#!/usr/bin/env python
# Copyright 2013-present Barefoot Networks, Inc. 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This sript works around limitations of the automake tests
# by generating a portion of the makefile.
# The problem is that the makefiles do not allow passing any
# arguments to the test programs, so there is no way we can
# run the same test program twice with different arguments.
# We generate a separate little custom script for each
# program that we need to test, and we add that script to the makefile
# as a target.
#
# For example, `gen-tests.py dir pre command a b
# generates on stdout:
# TESTS += \
#	 prea.test \
#	 preb.test 
# CLEANFILES += \
#	 prea.test \
#	 preb.test
# and two scripts prea.test and preb.test.  The contents of prea.test is just:
# command dir a

from __future__ import print_function
import sys
import os
import stat

def usage(exe):
    print(exe, ": Generate part of Makefile and supporting scripts for testing")
    print("Please read the python file for usage");

def filename(prefix, testname):
    test = prefix + '/' + testname + ".test"
    return test

extra = False
    
def generate(exe, srcdir, prefix, command, test_args, test_names):
    print("## Generated by ", exe)
    if extra:
        print("EXTRA_TESTS += \\")
    else:
        print("TESTS += \\")
    for i in range(0, len(test_names)):
        test = filename(prefix, test_names[i])
        print("\t", test, "\\" if (i < (len(test_names) - 1)) else "")

    print
    print("CLEANFILES += \\")
    for i in range(0, len(test_names)):
        test = filename(prefix, test_names[i])
        print("\t", test, "\\" if (i < (len(test_names) - 1)) else "")

    print
    for i in range(0, len(test_names)):
        test = filename(prefix, test_names[i])
        print(test, ": ", test_names[i])
        print("\t@mkdir -p", os.path.dirname(test))
        print("\t@echo \"cd $$PWD\" >$@")
        print("\t@echo '"+command, srcdir, " ".join(test_args),
              srcdir+"/"+test_names[i]+"' >>$@")
        print("\t@chmod +x $@")
        print
        
def main(argv):
    if argv[1] == '-extra':
        global extra
        extra = True
        argv[1:] = argv[2:]
    if len(argv) < 5:
        usage(argv[0])
        return
    srcdir = argv[1]
    prefix = argv[2]
    command = argv[3]
    test_args = []
    test_names = argv[4:]
    while test_names[0][0] == '-':
        test_args.append(test_names[0])
        test_names = test_names[1:]
    # This $* may be handy when running the test by hand.
    test_args.append("$$*");
    test_names = [name for name in test_names if os.path.isfile(name)]
    for i in range(0, len(test_names)):
        if test_names[i].startswith(srcdir):
            test_names[i] = test_names[i][len(srcdir):]
            if test_names[i].startswith('/'):
                test_names[i] = test_names[i][1:]
    generate(argv[0], srcdir, prefix, command, test_args, test_names)
    
if __name__ == "__main__":
    main(sys.argv)

