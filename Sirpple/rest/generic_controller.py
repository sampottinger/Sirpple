class SomethingHandler(webapp2.RequestHandler):

    def __init__(self, target_class, *args, **kwargs):
        self.__target_class = target_class

    def get(self):
        result = self.__do_get(self)
        serializer = SerializerFactory.get_serializer("complex-JSON")
        self.response.out.write(serializer.dumps(result))

    def post(self):
        
        # Determine action
        action = self.request.get(BaseHandler.ACTION_PARAM, None)

        # Check to make sure action is available
        if action == None: 
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            return

        # Switch on action
        if action == BaseHandler.POST:
            result = self.__do_post()
        elif action == BaseHandler.PUT:
            result = self.__do_put()
        elif action == BaseHandler.DELETE:
            result = self.__do_delete()
        else:
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
        
        serializer = SerializerFactory.get_serializer("complex-JSON")
        self.response.out.write(serializer.dumps(result))

    def __do_get(self):

        self.set_status(BaseHandler.OK)

    def __do_post(self):

    def __do_put(self):

    def __do_delete(self):