""" 
Classes to determine if a user has access to a top level object

Module containing logic to determine if a user has access to
objects that do not have parents (top level objects)
"""

from serialization import model_graph

from google.appengine.ext.db import Query

class ToplevelUACFacade:
    """ Interface for UAC facades that handle toplevel objects """

    def is_authorized(self, target, user):
        """
        Tests to see if the provided user can access target and its children

        @param target: Top level model instance
        @type target: Model instance
        @param user: Database-specific user construct
        @type user: DB-specific User object
        @return: True if the user is authorized to edit target and its children
                 and False otherwise
        @rtype: Boolean
        """
        raise NotImplementedError("Must use implementor of this interface")

class GAEToplevelUACFacade:
    """ Facade to check that a user has access to a toplevel object """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ToplevelUACFacade singleton

        @return: Shared ToplevelUACFacade instance
        @rtype: ToplevelUACFacade
        """
        if ToplevelUACFacade.__instance == None:
            ToplevelUACFacade.__instance = ToplevelUACFacade()
        
        return ToplevelUACFacade.__instance
    
    def __init__(self):
        """ Constructor for ToplevelUACFacade that contains a mapping to checking strategies """
        ToplevelUACFacade.__init__(self)
        self.__straegies = {"Project": GAEProjectUACChecker}
    
    def is_authorized(self, target, user):
        """
        Tests to see if the provided user can access target and its children

        @param target: Top level model instance
        @type target: Model instance
        @param user: Database-specific user construct
        @type user: DB-specific User object
        @return: True if the user is authorized to edit target and its children
                 and False otherwise
        @rtype: Boolean
        """
        # Get the name of the class we are operating on
        target_class_name = target.__class__.__name__

        strategy = self.__strategies[target_class_name].get_instance()
        return strategy.is_authorized(target, user)

class ToplevelUACChecker:
    """ Interface for strategies to verify access to toplevel objects """

    def __init__(self):
        pass
    
    def is_authorized(self, target, user):
        """
        Tests to see if the provided user can access target and its children

        @param target: Top level model instance
        @type target: Model instance
        @param user: Database-specific user construct
        @type user: DB-specific User object
        @return: True if the user is authorized to edit target and its children
                 and False otherwise
        @rtype: Boolean
        """
        raise NotImplementedError("Must use implementor of this interface")
    
class GAEProjectUACChecker(ToplevelUACChecker):
    """ Implementor of ToplevelUACChecker for checking projects """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this GAEProjectUACChecker singleton

        @return: Shared GAEProjectUACChecker instance
        @rtype: GAEProjectUACChecker
        """
        if GAEProjectUACChecker.__instance == None:
            GAEProjectUACChecker.__instance = GAEProjectUACChecker()
        
        return GAEProjectUACChecker.__instance

    def __init__(self):
        TopLevelUACChecker.__init__(self)
    
    def is_authorized(self, target, user):
        return True
        # get the model graph
        #graph = model_graph.get_current_graph()

        # Get the membership class
        #membership_class = graph.get_class_definition("Membership").get_class()
        
        # Make query for the given project and user
        #q = Query(membership_class)
        #q.filter("user =", user)
        #q.filter("parent =", target)

        # Test for existance
        #return q.get() != None
