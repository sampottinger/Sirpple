#!/usr/bin/env python

import logging
import os.path
from serialization import loaders
from glob import glob

def load(language = "yaml", location = 'app_config.yaml'):

    # Load up information from config files
    mechanic = loaders.ConfigModelFactoryMechanic.get_instance()
    
    with open(location) as config_file:
        configuration = config_file.read()
    
    factory = mechanic.load_factory_from_config(language, configuration)
    
    # Get newly loaded classes
    models = factory.get_models()
    
    # add all our new models to the global scope
    globals().update(models)
    
    return models
