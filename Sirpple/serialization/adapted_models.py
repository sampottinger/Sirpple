"""
Adaptable model that fills in the gaps for the backend in use
"""

try:
    from google.appengine.ext import db
    from google.appengine.ext.db import Query
except ImportError:
    # dont fail for on-the-ground testing
    db = None
    Query = None

# TODO: Fully unified interface for adaptable models . . . see backends.DatabaseManager

class GAEAdaptedModel(db.Model):
    """
    Model that fills in database-specific gaps in GAE implementation
    """

    def get_children(self, child_class, **kwargs):
        """ 
        Get all of the children of this model

        @param child_class: The child class to look for children in
        @type child_class: Any model instance
        @return: Iterator over this model's children
        @rtype: Iterator
        """

        query = Query(child_class)
        query.ancestor(self)

        for arg in kwargs.items():
            query.filter(arg(0) + " =", arg(1))

        # TODO: Ensure only immediate children

        return query
    
    def get_id(self):
        """
        Get model specific id global to the application

        @note: This id is only guaranteed to be unqiue for a single model class
        @return: The numerical id of this instance
        @rtype: int
        """
        return self.key().id()
