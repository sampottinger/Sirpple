#!/usr/bin/env python

import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)

def main():
    # main never used by appengine python27
    pass


if __name__ == '__main__':
    main()
