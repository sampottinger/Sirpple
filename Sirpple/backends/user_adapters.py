""" Adapter to the database user constructs """

from google.appengine.api import users

class UserAdapter:
    """ Adapter interface for database-specific user constructs """

    @classmethod
    def get_by_username(self, username):
        """ Gets the user with the given unique username """
        raise NotImplementedError("Must use implementor of this interface")

    def __init__(self):
        pass
    
    def get_username(self):
        """
        Produces a unique identifier for this user

        @return: Unique value to identify this user by
        @rtype: Python object
        """
        raise NotImplementedError("Must use implementor of this interface")
    
class GAEUserAdapter():
    """ Implementor of UserAdapter for Google App Engine's User class """

    @classmethod
    def get_by_username(self, username):
        # Handle OpenID
        if username.startswith("openid:"):
            identifier = username.partition("openid:")[2]
            return user.User(federated_identity=identifier)

        # Handle regular
        else:
            return users.User(email = username)

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
            identity = self.__inner_user.federated_identity()
            return "openid:" + identity

        # If in normal authentication
        else:
            return self.__inner_user.email()
