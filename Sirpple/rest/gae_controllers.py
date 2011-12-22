""" Classes for the creation of Google App Engine REST API controllers """

import logging
import webapp2
from google.appengine.api import users
from serialization import model_graph
from serialization import dto
import backends
from configparser import get_parser

class GAEController(webapp2.RequestHandler):

    DEFAULT_SERIALIZER = "complex-JSON"
    PROJECT_MODEL_NAME = "Project"
    PROJECT_ID_PARAM = "project_id"
    INSTANCE_ID_PARAM = "instid"
    PARENT_PARAM = "parent"
    ACTION_PARAM = "action"
    DATA_PARAM = "payload"

    # TODO: These could pop out into a more generic controller
    NOT_ACCEPTABLE = 406 
    UNAUTHORIZED = 401

    __instance = None

    def __init__(self, target_class):
        self.__target_class_name = target_class.get_name()   
        
        graph = model_graph.ModelGraph.get_current_graph()

        self.__target_class_defn = target_class
        self.__uac_checker = backends.platform_manager.PlatformManager.get_instance().get_uac_checker()
    
    def __call__(self, request, *args, **kwargs):
        self.initialize(request, request.response)
        return self.dispatch()
    
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
        platform = backends.platform_manager.PlatformManager.get_instance()
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
    
    def get_target_instance_by_id(self, target_id_str = None):
        """
        Gets the instance with the id passed as a parameter in this request
        
        @param target_id_str: The database id of the target
        @type target_id_str: string
        
        @return: Target instance or None if id not specified
        @rtype: Instance of the class this handler services
        """
        
        if not target_id_str:
            return None
        
        target_id = int(target_id_str)
        
        target_class = self.__target_class_defn.get_class()
        return target_class.get_by_id(target_id)

class GAEIndexController(GAEController):
    """ Google App Engine handler for listing objects """
    
    def get(self, parent_id_str):
        graph = model_graph.ModelGraph.get_current_graph()
        target_class_defn = self.get_target_class_definition()
        target_class_name = target_class_defn.get_name()
        target_class = target_class_defn.get_class()
        parent_class_name = target_class_defn.get_parent_field().get_field_type_name()
        parent_class = graph.get_class_definition(parent_class_name).get_class()

        # Get the parent from the request
        parent_id = int(parent_id_str)
        parent = parent_class.get_by_id(parent_id)
        if parent == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for index of " + target_class_name + " without specifying parent")
            return
        
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

class GAEIndividualController(GAEController):
    """ Handler for a GET, DELETE, and PUT request on a specific instance """
    
    DELETE_ACTION = "delete"
    PUT_ACTION = "put"

    def get(self, target_id_str):
        servicing_class_name = self.get_class_definition().get_name()

        # Get the instance in question
        target = self.get_target_instance_by_id(target_id_str)
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

    def post(self, target_id_str):
        servicing_class_name = self.get_class_definition().get_name()

        # Determine desired action
        action = self.get(GAEController.ACTION_PARAM)
        if action == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to modify " + servicing_class_name + " without specifying action")
            return
        
        # Get the instance in question
        target = self.get_target_instance_by_id(target_id_str)
        if target == None:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Asked for " + servicing_class_name + " but no ID was provided")
            return

        # Check that the user is authorized
        if not self.has_access(target):
            self.error(GAEController.UNAUTHORIZED) # TODO: Should conform to standards
            logging.error(self.get_current_username() + " attempted unauthorized access to " + target_class_name)
            return
        
        # Route accordingly
        if action == GAEIndividualController.DELETE_ACTION:
            self.__do_delete(target)
        elif action == GAEIndividualController.PUT_ACTION:
            self.__do_put(target)
        else:
            self.error(GAEController.NOT_ACCEPTABLE) # TODO: Should provide acc. characteristics
            logging.error("Went to modify " + servicing_class_name + " but given invalid action " + action)
            return
    
    def __do_delete(self, target):
        
        target.delete()
    
    def __do_put(self, target):

        arguments = self.arguments()
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

    def post(self, project_id_str):
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
