""" Classes for the creation of Google App Engine REST API controllers """

import logging
import webapp2
from google.appengine.api import users
from serialization import model_graph

class GAEController(webapp2.RequestHandler):

    DEFAULT_SERIALIZER = "complex-JSON"
    PROJECT_MODEL_NAME = "Project"
    PROJECT_ID_PARAM = "project_id"
    INSTANCE_ID_PARAM = "id"
    PARENT_PARAM = "parent"

    # TODO: These could pop out into a more generic controller
    NOT_ACCEPTABLE = 406 

    def __init__(self, target_class, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)    
        
        graph = model_graph.ModelGraph.get_current_graph()
        
        self.__target_class_defn = graph.get_class_definition(self.__target_class_name)
        self.__uac_checker = platform_manager.PlatformManager.get_instance().get_uac_checker()
    
    def write_serialized_response(self, target):
        """
        Write out target as a serialized object to response

        @param target: The object or list of objects to serialize
        @type target: Model instance from class loaded from config file
        """
        pass
    
    def has_access(self, target):
        """
        Determines if current user has access to target

        @param target: The target object to load
        @type target: Instance of model from class loaded from config file
        """
        pass
    
    def get_by_id(self, class_name, target_id):
        """ Gets the instance of the given class by id

        @param target_class The class to look for the given instance in
        @type target_class: Name of the class to look for
        @param target_id: The id of the instance to look for
        @type target_id: int
        """
        pass
    
    def get_current_username(self):
        """
        Gets the unique username of the current user

        @return: Unique username to the current request's sender
        @rtype: String
        """
        pass
    
    def get_target_class_definition(self):
        """
        Gets the definition of the class that this handler services

        @return: The definition of the class that this handler supports
        @rtype: ClassDefinition
        """
        return self.__target_class_defn
    
    def get_target_instance_by_id(self):
        """
        Gets the instance with the id passed as a parameter in this request

        @return: Target instance or None if id not specified
        @rtype: Instance of the class this handler services
        """ 
        pass

class GAEIndexHandler(GAEController):
    """ Google App Engine handler for listing objects """

    def __init__(self, target_class, *args, **kwargs):
        GAEController.__init__(target_class, *args, **kwargs)
    
    def get(self):
        graph = model_graph.ModelGraph.get_current_graph()
        target_class_defn = self.get_target_class_definition()
        target_class_name = target_class_defn.get_name()
        target_class = target_class_defn.get_class()
        parent_class_name = target_class_defn.get_parent_field().get_field_type_name()
        parent_class = graph.get_class_definition(parent_class_name).get_class()

        # Get the parent from the request
        parent_id_str = self.get(GAEController.PARENT_PARAM)
        if parent == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for index of " + target_class_name + " without specifying parent")
            return
        parent_id = int(parent_id_str)
        parent = parent_class.get_by_id(parent_id)
        
        # Check user access
        if not self.has_access(parent):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)

        # Query for children
        query = Query(target_class)
        query.filter("parent =", parent)

        # Serialize and return
        results = list(query)
        self.write_serialized_response(results)

class GAEIndividualGet(GAEController):
    """ Handler for a GET request on a specific instance """

    def get(self):
        servicing_class_name = self.get_class_definition().get_name()

        # Get the instance in question
        target = self.get_target_instance_by_id()
        if target == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for " + servicing_class_name + " but no ID was provided")
        
        # Check that the user is authorized
        if not self.has_access(target):
             self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)
        
        # Serialize and send back
        self.write_serialized_response(target)
