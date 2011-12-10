""" Classes for the creation of Google App Engine REST API controllers """

import logging
import webapp2
from google.appengine.api import users
from google.appengine.ext.db import Query
from ..serialization import config_model
from ..backends import platform_manager

class GAEController(webapp2.RequestHandler):

    DEFAULT_SERIALIZER = "complex-JSON"
    PROJECT_MODEL_NAME = "Project"
    PROJECT_ID_PARAM = "project_id"
    INSTANCE_ID_PARAM = "id"
    PARENT_PARAM = "parent"

    def __init__(self, target_class, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)    
        
        model_factory = config_model.ConfigModelFactory.get_instance()
            
        self.target_class = target_class
        self.target_class_name = target_class.__name__
        self.target_class_defn = model_factory.get_class(self.__target_class_name)
        self.project_model = model_factory.get_class(GAEController.PROJECT_MODEL_NAME)
        self.uac_checker = platform_manager.PlatformManager.get_instance().get_uac_checker()
    
    def get_instance_by_id(self, instance_id):
        return self.__target_class.get_by_id(instance_id)
    
    def write_serialized_response(self, target):
        """ Write out target as a serialized object """
        pass
    
    def interpret_foreign_value(self, field_name, target):
        """ Take in a user-provided value and provide a corresponding pure python value with inferred type """
        pass
    
    def is_authorized(self, target):
        """ Checks to see if the current user can operate on target """
        user = users.get_current_user()
        return self.uac_checker.is_authorized(x, user)

class GAEAccessController(GAEController):

    def get(self, instance_id):
        result = self.get_instance_by_id(instance_id)
        serializer = SerializerFactory.get_serializer(GAEController.DEFAULT_SERIALIZER)
        self.response.out.write(serializer.dumps(result))

    def post(self, instance_id):
        
        # Determine action
        action = self.request.get(BaseHandler.ACTION_PARAM, None)

        # Check to make sure action is available
        if action == None: 
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            return

        # Switch on action
        elif action == BaseHandler.POST:
            result = self.__do_post(instance_id)
        elif action == BaseHandler.DELETE:
            result = self.__do_delete(instance_id)
        else:
            self.error(BaseHandler.METHOD_NOT_ALLOWED)

    def __do_post(self, instance_id):

        # Get the instance
        instance = self.get_instance_by_id(instance_id)
        if instance == None:
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            return
        
        # Check authorization
        if not self.is_authorized(instance):
            self.error(BaseHandler.FORBIDDEN)
            return

        fields = self.target_class_defn.get_fields()

        # Make changes
        for field_name in filter(lambda x: x.is_exposed(), fields.keys()):

            if field_name in arguments:
                new_val_raw = self.get(field_name)
                new_val = self.interpret_foreign_value(field_name, new_val_raw)
                setattr(instance, field_name, new_val)
        
        # Save back
        instance.put()

        # Report on success
        self.__write_seralized_response(instance)
        self.set_status(BaseHandler.UPDATED)

    def __do_delete(self, instance_id):
        
        # Get the instance
        instance = self.get_instance_by_id(instance_id)
        if instance == None:
            self.error(BaseHandler.METHOD_NOT_ALLOWED)
            return
        
        # Check authorization
        if not self.is_authorized(instance):
            self.error(BaseHandler.FORBIDDEN)
            return
        
        # Write out soon to be deleted contents
        self.write_serialized_response(instance)

        # Delete
        instance.delete()

        # Confirm
        self.set_status(BaseHandler.DELETED)
