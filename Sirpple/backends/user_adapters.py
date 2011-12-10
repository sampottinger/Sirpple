""" Adapter to the database user constructs """

class UserAdapter:
    """ Adapter interface for database-specific user constructs """

    def __init__(self):
        pass
    
    def get_username(self):
        """
        Produces a unique identifier for this user

        @return: Unique value to identify this user by
        @rtype: Python object
        """
        raise NotImplementedError("Must use implementor of this interface")
    
class GAEUserAdapter(self):
    """ Implementor of UserAdapter for Google App Engine's User class """

    def __init__(self, target):
        """
        Creates a new GAEUserAdapter around the given target User

        @param target: The object to adapt
        @type target: Google App Engine User instance
        """
        self.__inner_user = target
    
    def get_username(self):
        
        user_id = self.__inner_user.user_id()

        # If we are using OpenID
        if user_id == None:
            return self.__inner_user.federated_identity()

        # If in normal authentication
        else:
            return user_id