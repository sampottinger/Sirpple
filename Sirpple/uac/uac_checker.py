"""
Module containing logic to check that a user is authorized to view / edit an entity
"""

# TODO: Factory currently sitting serialization.backends

class UACChecker:
    """
    High level strategy interface to check to see if a user can view / edit a model instance
    """
    
    def __init__(self):
        pass
    
    def is_authorized(self, target, user):
        """
        Determines if the given user has read / write access to target

        @param target: The model that the user wants to access
        @type target: Any instance of the subclass of AdaptedModel currently in use
        @param user: The user that wishes to access the model instance in question
        @type user: The backend-specific user representation
        """
        raise NotImplementedError("Must use implmentor of this interface")
    
class GAEUACChecker(UACChecker):
    """
    Google App Engine specific implemention of UACChecker
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this GAEUACChecker singleton

        @return: Shared GAEUACChecker instance
        @rtype: GAEUACChecker
        """
        if GAEUACChecker.__instance == None:
            GAEUACChecker.__instance = GAEUACChecker()
        
        return GAEUACChecker.__instance
    
    def is_authorized(self, target, user):
        return True # TODO: After authentication, this ought to be filled in
        # NOTE: user or target might be null