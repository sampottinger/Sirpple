#!/usr/bin/env python

import webapp2
import yamlmodels
from page_builder import managers

models = yamlmodels.load()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class AppHandler(webapp2.RequestHandler):

    APP_TEMPLATE = "app.html"

    def get(self):
        composite_template_manager = managers.PageManager.get_instance()
        self.response.out.write(composite_template_manager.render(AppHandler.APP_TEMPLATE))

app = webapp2.WSGIApplication([('/', MainHandler),
                                '/app', AppHandler], debug=True


if __name__ == '__main__':
    main()
