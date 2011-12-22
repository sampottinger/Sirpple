"""
Module contiaining logic to build the REST controllers from config files
"""

import gae_controllers
from serialization import model_graph

class ControllerGenerator:
    """ Abstract class for db-specific REST API builders """

    def __init__(self):
        pass

    def build_interface(self, class_definition):
        """
        Create the controller for the given class definined the given definition

        @param class_definition: Descriptor of the class to build a controller for
        @type class_definition: ClassDefinition
        @return: DB-specific controllers and their URLs
        @rtype: List of Tuple of (URL, controller)
        """
        raise NotImplementedError("Must use implementor of this abstract class")
    
    def build_interfaces(self, class_definitions):
        """
        Create interfaces for the given set of class definitions

        @param class_defintions: Descriptors of the classes to build controllers for
        @type class_definitions: Iterable over ClassDefinition
        @return: List of tuples of URL patterns and the controller
        @rtype: List of (url pattern, db specific handler / controller)
        """
        handlers = []

        for definition in class_definitions.values():
            handlers.extend(self.build_interface(definition))
        
        return handlers
    
    # TODO: Not sure if this should be here
    def build_all_interfaces(self):
        """
        Builds all the interfaces for the current model graph

        @return: List of tuples of URL patterns and the controller
        @rtype: List of (url pattern, db specific handler / controller)
        """
        graph = model_graph.ModelGraph.get_current_graph()
        return self.build_interfaces(graph.get_class_definitions())

class GAEControllerGenerator(ControllerGenerator):
    """ Generator of Google App Engine controllers """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this GAEControllerGenerator singleton

        @return: Shared GAEControllerGenerator instance
        @rtype: GAEControllerGenerator
        """
        if GAEControllerGenerator.__instance == None:
            GAEControllerGenerator.__instance = GAEControllerGenerator()
        
        return GAEControllerGenerator.__instance

    def __init__(self):
        ControllerGenerator.__init__(self)
    
    def build_interface(self, class_definition):
        
        handlers = []

        # Get names
        name = class_definition.get_name().lower()
        parent_name = class_definition.get_db_parent_name()
        
        if parent_name:
            # Build index controller
            index_controller = gae_controllers.GAEIndexController(class_definition)
            handlers.append(("\/" + parent_name.lower() + "\/(\d+)\/" + name + "s", index_controller))

        # Build individual controller
        individual_controller = gae_controllers.GAEIndividualController(class_definition)
        handlers.append(("\/" + name + "\/(\d+)", individual_controller))

        # Build creation controller
        creation_controller = gae_controllers.GAECreateController(class_definition)
        handlers.append(("\/project\/(\d+)\/" + name, creation_controller))

        return handlers
