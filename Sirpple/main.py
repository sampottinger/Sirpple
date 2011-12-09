#!/usr/bin/env python

import webapp2
import yamlmodels
from page_builder import managers
import test

models = yamlmodels.load()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class TestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        module_name = self.request.get('module')
        test_name = self.request.get('test')
        
        if not module_name:
            print >>self.response.out, 'No test module specified'
            return
        
        if not hasattr(test,module_name):
            print >>self.response.out, 'Test module', module_name, 'not found'
            return
        
        module = getattr(test,module_name)
        
        if not test_name:
            print >>self.response.out, 'No test specified'
            return
        
        if not hasattr(module,test_name):
            print >>self.response.out, 'Test', test_name, 'not found in module', module_name
            return
        
        test_callable = getattr(module,test_name)
        
        test_callable(self.response.out)

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
