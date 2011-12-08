"""
Classes that can build templates containing sub-templates
"""

import os
import re

class PageBuilder:
    """ 
    Class that load and combine template files by pre-processing, caching the result

    Mechanism to combine template files before sending them to the current template
    rendering library. Also supports caching the results.
    """

    def __init__(self, target, templates_dir, tag="{* %s *}"):
        """
        Create a new page builder to operate on the given target page

        @param target: The file name of the page to fill in with other templates
        @type target: String
        @param templates_dir: The local directory where templates are stored
        @type templates_dir: String
        @keyword tag: The tag to look for that indicates another template
                      should be loaded in its place. Defaults to {* %s *}
        @type tag: String
        """
        self.__templates_dir = templates_dir
        self.__tag = tag
        self.__tag_regex = re.compile(self.__tag % "(?<=[\w\.\/]+)")
        self.__cache = None

        with open(self.__get_file_loc(target)) as f:
            self.__target_contents = f.read()
    
    def render(self):
        """
        Loads all of the sub-templates and returns this template pre-processed
        
        @return: The original template file contents with sub-templates loaded
        @rtype: String
        """
        if self.__cache == None:
            for match in self.__tag_regex.findall(self.__target_contents):
                self.__target_contents = self.__replace_tag(self.__target_contents, match.group(0))
            
            self.__cache = self.__target_contents
        
        return self.__cache
    
    def __replace_tag(self, overall_contents, filename):
        """
        Replace the tag for the given subtemplate file

        @param overall_contents: The string to find and replace the tags in
        @type overall_contents: String
        @param filename: The name of the file to load to replace its stubbed tag
        @type filename: String
        @return: Updated overall template contents
        @rtype: String
        """
        loc = self.__get_file_loc(filename)
        target_tag = self.__tag % filename

        with open(loc) as f:
            sub_template = f.read()

        return overall_contents.replace(target_tag, sub_template)

    def __get_file_loc(self, target):
        """
        Determines the expected full path to the given filename

        @param target: The name of the file to locate
        @type target: String
        @return: The full path to the specified file
        @rtype: String
        """
        return os.path.join(self.__templates_dir, target)
