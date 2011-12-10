#!/usr/bin/env python

import webapp2
import yamlmodels
from page_builder import managers
import importlib
import re
import traceback

try:
    import test
except ImportError:
    test = None
models = yamlmodels.load()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class TestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        if not test:
            print >>self.response.out, "No test module found"
            return
        
        module_name = self.request.get('module')
        module_name = re.sub('\.+','.',module_name.lstrip('.'))
        test_name = self.request.get('test')
        
        if not module_name:
            print >>self.response.out, 'No test module specified'
            return
        
        try:
            module = importlib.import_module('test.'+module_name)
        except ImportError:
            print >>self.response.out, 'Test module', module_name, 'not found'
            return
        
        if not test_name:
            print >>self.response.out, 'No test specified'
            return
        
        if not hasattr(module,test_name):
            print >>self.response.out, 'Test', test_name, 'not found in module', module_name
            return
        
        test_callable = getattr(module,test_name)
        
        try:
            result = test_callable(self.response.out)
        except:
            exc = traceback.format_exc()
            print >>self.response.out, exc
        else:
            print >>self.response.out, module_name+'.'+test_name,'finished'
            
            if result != None:
                print >>self.response.out, 'result:'
                print >>self.response.out, result

class AppHandler(webapp2.RequestHandler):

    APP_TEMPLATE = "app.html"

    def get(self):
        composite_template_manager = managers.PageManager.get_instance()
        self.response.out.write(composite_template_manager.render(AppHandler.APP_TEMPLATE))

app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/test', TestHandler),
                                ('/app', AppHandler)], debug=True)


if __name__ == '__main__':
    main()
