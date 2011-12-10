""" Classes for the creation of Google App Engine REST API controllers """

import logging
import webapp2
from google.appengine.api import users
from serialization import model_graph
from serialization import dto
from backends import platform_manager
from configparser import get_parser

class GAEController(webapp2.RequestHandler):

    DEFAULT_SERIALIZER = "complex-JSON"
    PROJECT_MODEL_NAME = "Project"
    PROJECT_ID_PARAM = "project_id"
    INSTANCE_ID_PARAM = "id"
    PARENT_PARAM = "parent"
    ACTION_PARAM = "action"
    DATA_PARAM = "payload"

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
        target_dto = dto.DTOBuilder.create_dto(target)
        serializer = get_parser("json")
        self.response.out.write(serializer.dumps(target))
    
    def has_access(self, target):
        """
        Determines if current user has access to target

        @param target: The target object to load
        @type target: Instance of model from class loaded from config file
        """
        current_user = users.get_current_user()
        platform = platform_manager.PlatformManager.get_instance()
        checker = platform.get_uac_checker()
        return checker.is_authorized(target, current_user)
    
    def get_current_username(self):
        """
        Gets the unique username of the current user

        @return: Unique username to the current request's sender
        @rtype: String
        """
        adapted_user = platform.get_adapted_user(users.get_current_user())
        return adapted_user.get_username()
    
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
        if not GAEController.INSTANCE_ID_PARAM in self.arguments():
            return None

        target_id = int(self.get(GAEController.INSTANCE_ID_PARAM))

        target_class = self.__target_class_defn.get_class()
        return target_class.get_by_id(target_id)

class GAEIndexController(GAEController):
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
            return

        # Query for children
        query = Query(target_class)
        query.filter("parent =", parent)

        # Serialize and return
        results = list(query)
        self.write_serialized_response(results)

class GAEIndividualGetController(GAEController):
    """ Handler for a GET request on a specific instance """

    def get(self):
        servicing_class_name = self.get_class_definition().get_name()

        # Get the instance in question
        target = self.get_target_instance_by_id()
        if target == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for " + servicing_class_name + " but no ID was provided")
            return
        
        # Check that the user is authorized
        if not self.has_access(target):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)
            return
        
        # Serialize and send back
        self.write_serialized_response(target)

class GAEModifyController(GAEController):
    """ Handler for a DELETE, POST, or PUT on a resource """

    DELETE_ACTION = "delete"
    PUT_ACTION = "put"

    def post(self):
        servicing_class_name = self.get_class_definition().get_name()

        # Determine desired action
        action = self.get(GAEController.ACTION_PARAM)
        if action == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to modify " + servicing_class_name + " without specifying action")
            return

        # Route accordingly
        if action == GAEModifyController.DELETE_ACTION:
            self.__do_delete()
        elif action == GAEModifyController.PUT_ACTION:
            self.__do_put()
        else:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to modify " + servicing_class_name + " but given invalid action " + action)
            return
    
    def __do_delete(self):
        
        target = self.get_target_instance_by_id()
        if target == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for " + servicing_class_name + " but no ID was provided")
            return

        # Check that the user is authorized
        if not self.has_access(target):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)
            return
        
        target.delete()
    
    def __do_put(self):

        arguments = self.arguments()
        
        target = self.get_target_instance_by_id()
        if target == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for " + servicing_class_name + " but no ID was provided")
            return

        # Check that the user is authorized
        if not self.has_access(target):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)
            return
        
        # Get the payload
        if not GAEController.DATA_PARAM in arguments:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to modify " + servicing_class_name + " but no payload provided")
            return
        payload = self.get(GAEController.DATA_PARAM)
        
        # Load it into target
        dto_builder = dto.DTOBuilder.get_instance()
        parser = get_parser("json")
        payload_parsed = parser.loads(parser)
        dto_builder.read_dto(payload_parsed, self.get_target_class_definition(), target=target)

        # Save
        target.put()

        # Render out new state
        self.write_serialized_response(target)

class GAECreateController(GAEController):
    """ Handler for a POST request on a resource """

    def post(self):
        """ Creates a new resource on the server """
        target_class_name = self.get_target_class_definition().get_name()

        # Get the payload
        if not GAEController.DATA_PARAM in arguments:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to build " + servicing_class_name + " but no payload provided")
            return
        payload = self.get(GAEController.DATA_PARAM)

        # Decode payload
        # TODO: not a fan of straight get_parser
        payload_parsed = get_parser("json").loads(payload)

        # Build new instance
        builder = dto.DTOBuilder.get_instance().create_dto(payload)
        new_instance = builder.read_dto(payload_parsed)
        
        # Check that the user is authorized
        if not self.has_access(new_instance.get_parent()):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to get parent for a " + target_class_name)
            return
        
        # Save
        new_instance.put()

        # Build new object
        self.write_serialized_response(new_instance)
