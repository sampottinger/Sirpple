#!/usr/bin/env python

from glob import glob
from os.path import normpath
from os.path import join as joinpath
import json
import pyyaml


class ParserAdapter:
    """ Fully abstract parser interface """

    def __init__(self, extension):
        """
        init a parser for files with the given extension
        
        @param extension: The file extension for config files targeted by this parser
        @type extension: String
        """
        self.extension = extension
    
    def dumps(self, target):
        """
        Dumps the serializable object target into this parser's supported format

        @param target: The target to serialize
        @type target: Seriazliable class instance
        @return: String formatted in this parser's format
        @rtype: String
        """
        raise NotImplementedError("Need to use subclass of this interface")

    def loads(self, source):
        """
        Loads the data saved in the provided string

        @param source: The source string to load form
        @type source: String
        @return: Dictionary loaded from string
        @rtype: Dictionary
        """
        raise NotImplementedError("Need to use subclass of this interface")

    def load_file(self, filename):
        """
        Loads the data saved in the provided filename

        @param filename: The filename to load form
        @type filename: String
        @return: Dictionary loaded from file
        @rtype: Dictionary
        """
        with open(filename) as f:
            result = f.read()
        return self.loads(result)

    def load_dir(self, directory):
        """
        Loads all data saved in the provided directory

        @param directory: The directory to load form
        @type directory: String
        @return: Dictionary loaded from all files in the directory
        @rtype: Dictionary
        """
        
        result = {}
        glob_path = normpath(joinpath(directory,'*.' + self.extension))
        for path in glob(glob_path):
            result.update(self.load_file(path))
        return result

class YamlAdapter(ParserAdapter):
    """ Adapts the pyyaml YAML parser to the generic parser """

    def __init__(self):
        ParserAdapter.__init__(self, extension='yaml')
    
    def loads(self, source):
        return pyyaml.load(source)
    
    def dumps(self, target):
        return pyyaml.dump(target)

class JSONAdapter(ParserAdapter):
    """ Adapts the built in JSON parser / serializer to the generic parser interface """

    def __init__(self):
        ParserAdapter.__init__(self, extension='json')
    
    def loads(self, source):
        return json.loads(source)
    
    def dumps(self, source):
        return json.dumps(source)

__parsers = {'yaml' : YamlAdapter(),
             'json' : JSONAdapter()}

def get_parser(language):
    if language in __parsers:
        return __parsers[language]
    else:
        raise NotImplementedError('This parser is not yey implemented')
