"""
Facades to manage page builders and their cached results
"""

import builders

class PageManager:
    """
    Manager of templates containing sub-templates needed pre-processing
    """

    DEFAULT_TEMPLATES_DIR = "./views"
    DEFAULT_TAG = "{* %s *}"

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this PageManager singleton

        @return: Shared PageManager instance
        @rtype: PageManager
        """
        if PageManager.__instance == None:
            PageManager.__instance = PageManager()
        
        return PageManager.__instance
    
    def __init__(self):

        # TODO: Make this configurable
        self.__templates_dir = PageManager.DEFAULT_TEMPLATES_DIR
        self.__tag = PageManager.DEFAULT_TAG
        self.__builders = {}
    
    def render(self, filename):
        """
        Render out the template at the given filename

        @param filename: The name of the template to render out
        @type filename: String
        @return: The pre-processed template
        @rtype: String
        """
        if not filename in self.__builders:
            self.__builders[filename] = builders.PageBuilder(filename, self.__templates_dir, self.__tag)
        
        return self.__builders[filename].render()