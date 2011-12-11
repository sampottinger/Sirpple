#!/usr/bin/env python

import webapp2
import yamlmodels
from page_builder import managers
import re
import testcontrollers

models = yamlmodels.load()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class TestHandler(webapp2.RequestHandler):
    def get(self):
        content_type = self.request.get('format')
        
        self.response.headers['Content-Type'] = str(content_type) or 'text/plain'
        
        def string_convert(item):
            return str(item[0]),item[1]
            
        request_dict = dict(map(string_convert, self.request.GET.items()))
        
        module_name = self.request.get('module')
        module_name = re.sub('\.+','.',module_name.lstrip('.'))
        test_name = self.request.get('test')
        
        for key in ['format','module','test']:
            if key in request_dict:
                del request_dict[key]
        
        driver = testcontrollers.TestDriver()
        driver.run_test(module_name, test_name, self.response.out, request_dict)

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
