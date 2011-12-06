"""
Adaptable model that fills in the gaps for the backend in use
"""

try:
    from google.appengine.ext import db
except ImportError:
    db = None # dont fail for on-the-ground testing

# TODO: Fully unified interface for adaptable models . . . see backends.DatabaseManager

class GAEAdaptedModel(db.Model):
	"""
	Model that fills in database-specific gaps in GAE implementation
	"""

	def get_children(self, child_class, **kwargs):
		""" 
		Get all of the children of this model

		@param 
		@return: Iterator over this model's children
		@rtype: Iterator
		"""

		query = Query(child_class)
		query.ancestor(self)

		for arg in kwargs.items():
			query.filter(arg(0) + " =", arg(1))

		# TODO: Ensure only immediate children

		return query