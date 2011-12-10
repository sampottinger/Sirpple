#!/usr/bin/env python

import importlib
import traceback
import sys

try:
    import test
except ImportError:
    test = None

class TestDriver(object):
    
    def run_test(self, module_name, test_name, response_out):
        
        if not test:
            print >>response_out, "No test module found"
            return
        
        if not module_name:
            print >>response_out, 'No test module specified'
            return
        
        try:
            module = importlib.import_module('test.'+module_name)
        except ImportError:
            #TODO: figure out whether this ImportError came from 
            #      immediately above, or from a recursive import
            #      if the problem is deeper then print exc
            #      else print module not found
            exc = traceback.format_exc()
            print >>response_out, exc
            print >>response_out, 'Test module', module_name, 'not found'
            return
        
        if not test_name:
            print >>response_out, 'No test specified'
            return
        
        if not hasattr(module,test_name):
            print >>response_out, 'Test', test_name, 'not found in module', module_name
            return
        
        test_callable = getattr(module,test_name)
        
        stdout = sys.stdout
        sys.stdout = response_out
        
        try:
            result = test_callable()
        except:
            exc = traceback.format_exc()
            print exc
        else:
            print module_name+'.'+test_name,'finished'
            
            if result != None:
                print 'result:'
                print result
        
        sys.stdout = stdout
