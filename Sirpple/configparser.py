#!/usr/bin/env python

import pyyaml


class ParserAdapter:
    """ Fully abstract parser interface """

    def __init__(self):
        pass

    def loads(self, source):
        """
        Loads the data saved in the provided string

        @param source: The sourceing to load form
        @type source: String
        @return: Dictionary loaded from string
        @rtype: Dictionary
        """
        raise NotImplementedError("Need to use subclass of this interface")

class YamlAdapter(ParserAdapter):
    """ Adapts the pyyaml YAML parser to the generic parser """

    def __init__(self):
        ParserAdapter.__init__(self)
    
    def loads(self, source):
        """
        Loads the data saved in the provided string

        @param source: The string to load form
        @type source: String
        @return: Dictionary loaded from string
        @rtype: Dictionary
        """
        return pyyaml.load(source)

__parsers = {'yaml' : YamlAdapter()}

def get_parser(language):
    if language in __parsers:
        return __parsers[language]
    else
        raise NotImplementedError('This parser is not yey implemented')
