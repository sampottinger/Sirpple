#!/usr/bin/env python

import importlib
import traceback

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
            print >>response_out, 'Test module', module_name, 'not found'
            return
        
        if not test_name:
            print >>response_out, 'No test specified'
            return
        
        if not hasattr(module,test_name):
            print >>response_out, 'Test', test_name, 'not found in module', module_name
            return
        
        test_callable = getattr(module,test_name)
        
        try:
            result = test_callable(response_out)
        except:
            exc = traceback.format_exc()
            print >>response_out, exc
        else:
            print >>response_out, module_name+'.'+test_name,'finished'
            
            if result != None:
                print >>response_out, 'result:'
                print >>response_out, result
