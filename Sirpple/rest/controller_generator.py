"""
Module contiaining logic to build the REST controllers from config files
"""

import gae_controllers

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

        for definition in class_definitions:
            handlers.extend(self.build_interface(definition))
        
        return handlers

class GAEControllerGenerator(ControllerGenerator):
    """ Generator of Google App Engine controllers """

    def __init__(self):
        ControllerGenerator.__init__(self)
    
    def build_interface(self, class_definition):
        
        handlers = []

        # Get name
        name = class_definition.get_name().lower()

        # Get actuall class
        target_class = class_definition.get_class()

        # Build index controller
        index_controller = gae_controllers.GAEIndexController(target_class)
        handlers.append(("\/project\/(\d+)\/" + name + "s", index_controller))

        # Build individual controller
        individual_controller = gae_controllers.GAEIndividualGetController(target_class)
        handlers.append(("\/" + name + "\/(\d+)", individual_controller))

        # Build creation controller
        creation_controller = gae_controllers.GAECreateController(target_class)
        handlers.append(("\/project\/(\d+)\/" + name, creation_controller))

        return handlers
