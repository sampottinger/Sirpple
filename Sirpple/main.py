#!/usr/bin/env python

import webapp2
import yamlmodels
from page_builder import managers
import re
import backends
import testcontrollers

models = yamlmodels.load()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class TestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        module_name = self.request.get('module')
        module_name = re.sub('\.+','.',module_name.lstrip('.'))
        test_name = self.request.get('test')
        
        driver = testcontrollers.TestDriver()
        driver.run_test(module_name, test_name, self.response.out)

class AppHandler(webapp2.RequestHandler):

    APP_TEMPLATE = "app.html"

    def get(self):
        composite_template_manager = managers.PageManager.get_instance()
        self.response.out.write(composite_template_manager.render(AppHandler.APP_TEMPLATE))

platform = backends.platform_manager.PlatformManager.get_instance()
generator = platform.get_controller_generator()
rest_controllers = generator.build_all_interfaces()

controllers = [('/', MainHandler),
               ('/test', TestHandler),
               ('/app', AppHandler)]

controllers.extend(rest_controllers)

app = webapp2.WSGIApplication(controllers, debug=True)


if __name__ == '__main__':
    main()
