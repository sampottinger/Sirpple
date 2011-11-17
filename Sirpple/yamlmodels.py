#!/usr/bin/env python

from google.appengine.ext import db

import os.path
import pyyaml
from glob import glob

def load(location = './models/'):
    
    glob_path = os.path.normpath(os.path.join(location,'*.yaml'))
    filenames = glob(glob_path)
    
    models = {}
    
    for filename in filenames:
        
        with open(filename) as f:
            
            file_models = pyyaml.load(f.read())
            
            for model_name in file_models:
                model_members = file_models[model_name]
                
                # build a new dict of db fields for the class
                class_fields = {}
                for field,value in model_members.items():
                    
                    if value == 'string':
                        class_fields[field] = db.StringProperty(multiline=True)
                    else:
                        # unknown type
                        pass
                    
                    models[model_name] = type(model_name,(db.Model,),
                        class_fields)
    
    # add all our new models to the global scope
    globals().update(models)
    
    return models