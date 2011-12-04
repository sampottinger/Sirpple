#!/usr/bin/env python

from google.appengine.ext import db

import os.path
import serialization
from glob import glob

def load(language = "yaml", location = 'app_config.yaml'):
    
    #glob_path = os.path.normpath(os.path.join(location,'*.yaml'))
    #filenames = glob(glob_path)
    #
    #models = {}
    #
    #for filename in filenames:
    #    
    #    with open(filename) as f:
    #        
    #        file_models = pyyaml.load(f.read())
    #        
    #        for model_name in file_models:
    #            model_members = file_models[model_name]
    #            
    #            # build a new dict of db fields for the class
    #            class_fields = {}
    #            for field,value in model_members.items():
    #                
    #                if value == 'string':
    #                    class_fields[field] = db.StringProperty(multiline=True)
    #                else:
    #                    # unknown type
    #                    pass
    #                
    #                models[model_name] = type(model_name,(db.Model,),
    #                    class_fields)

    mechanic = serialization.ConfigModelFactoryMechanic.get_instance()
    
    with open(location) as config_file:
        configuration = config_file.read()
    
    factory = mechanic.load_factory_from_config(language, configuration)
    
    models = factory.get_classes()
    
    # add all our new models to the global scope
    globals().update(models)
    
    return models
