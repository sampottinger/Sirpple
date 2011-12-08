import logging
import webapp2
from google.appengine.api import users
from google.appengine.ext.db import Query
from ..serialization import config_model
from ..serialization import backends

class GAEController(webapp2.RequestHandler):

    DEFAULT_SERIALIZER = "complex-JSON"
    PROJECT_MODEL_NAME = "Project"
    PROJECT_ID_PARAM = "project_id"
    INSTANCE_ID_PARAM = "id"

    def __init__(self, target_class, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)    
        
        model_factory = config_model.ConfigModelFactory.get_instance()
            
        self.__target_class = target_class
        self.__target_class_name = target_class.__name__
        self.__target_class_defn = model_factory.get_class(self.__target_class_name)
        self.__project_model = model_factory.get_class(GAEController.PROJECT_MODEL_NAME)
        self.__uac_checker = backends.DatabaseManager.get_instance().get_uac_checker()

    def get(self):
        result = self.__do_get(self)
        serializer = SerializerFactory.get_serializer(GAEController.DEFAULT_SERIALIZER)
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
        arguments = self.arguments()

        # TODO: Limit query by __limit__ argument

        # Try to determine the project_id
        project = self.__get_project()

        # See if we can short-cut by looking up using an ID
        if GAEController.INSTANCE_ID_PARAM in arguments:
            instance = self.__get_instance_by_id()
            if instance == None:
                self.error(BaseHandler.METHOD_NOT_ALLOWED)
                return
            instances = [instance]

        # If not, build a query from the given parameters
        else:
            fields = self.__target_class_defn.get_fields()

            # NOTE: Query class handles sql injection
            query = Query(self.__target_class)

            # Build query with filters
            for field_name in filter(lambda x: x.is_exposed(), fields.keys()):

                if field_name in arguments:
                    query.filter(field_name + " =", self.get(field_name))
            
            instances = list(query)
        
        # Write out response for 
        check_security = lambda x: self.__is_authorized(x)
        self.__write_seralized_response(filter(check_security, instances))

        self.set_status(BaseHandler.OK)

    def __is_authorized(self, target):
        """ Checks to see if the current user can operate on target """
        user = users.get_current_user()
        return self.__uac_checker.is_authorized(x, user)
    
    def __get_project(self):
        """ Get the project referenced by this REST API call """
        if not GAEController.PROJECT_ID_PARAM in self.arguments():
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            logging.debug("Request reject b/c missing project_id")
        return self.__project_model.get_by_id(GAEController.PROJECT_ID_PARAM)
    
    def __get_instance_by_id(self):
        if GAEController.INSTANCE_ID_PARAM in self.arguments():
            return self.__target_class.get_by_id(int(self.get(GAEController.INSTANCE_ID_PARAM)))
        else:
            return None

    def __do_post(self):

        # Get the instance
        instance = self.__get_instance_by_id()
        if instance == None:
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            return
        
        # Check authorization
        if not self.__is_authorized(instance):
            self.error(BaseHandler.FORBIDDEN)
            return

        fields = self.__target_class_defn.get_fields()

        # Make changes
        for field_name in filter(lambda x: x.is_exposed(), fields.keys()):

            if field_name in arguments:
                new_val_raw = self.get(field_name)
                new_val = self.__interpret_foreign_value(new_val_raw)
                setattr(instance, field_name, new_val)
        
        # Save back
        instance.put()

        # Report on success
        self.__write_seralized_response(instance)
        self.set_status(BaseHandler.UPDATED)

    def __do_put(self):
        pass

    def __do_delete(self):
        pass
    
    def __write_serialized_response(self, target):
        pass