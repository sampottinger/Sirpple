"""
Module contiaining logic to build the REST controllers from config files
"""

import rest.gae_controllers

class ControllerGeneratorFactory:
    """ Factory that chooses the generator specific to the requested DB """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ControllerGeneratorFactory singleton

        @return: Shared ControllerGeneratorFactory instance
        @rtype: ControllerGeneratorFactory
        """
        if ControllerGeneratorFactory.__instance == None:
            ControllerGeneratorFactory.__instance = ControllerGeneratorFactory()
        
        return ControllerGeneratorFactory.__instance
    
    def __init__(self):
        """ Constructor that loads the available generator strategies """
        # TODO: Break this off into config file or single loc.
        self.__available_generators = {"GAE" : GAEControllerGenerator.get_instance()}
    
    def get_generator(self, db):
        """
        Get the generator corresponding to the given db

        @param db: The name of the backend currently being target
        @type db: String
        @return: Generator corresponding to the given database
        @rtype: ControllerGenerator implementor
        """
        if not db in self.__available_generators:
            raise KeyError("Controller generator not available for the given backend")
        
        return self.__available_generators[db]

class ControllerGenerator:
    """ Abstract class for db-specific REST API builders """

    def __init__(self):
        pass

    def build_interface(self, class_definition):
        """
        Create the controller for the given class definined the given definition

        @param class_definition: Descriptor of the class to build a controller for
        @type class_definition: ClassDefinition
        @return: DB-specific controller
        @rtype: Controller class / function
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
        retlist = []

        def build_tuple(definition):
            return (definition, self.build_interface(definition))

        return list(build_tuple(definition) for definition in class_definitions)

class GAEControllerGenerator(ControllerGenerator):
    """ Generator of Google App Engine controllers """

    def __init__(self):
        ControllerGenerator.__init__(self)
    
    def build_interface(self, class_definition):
        return gae_controllers.GAEController(class_definition.get_class())
