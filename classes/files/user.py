import json
import random
import string
from . import database

class User:
    def __init__(self, username=None, password = None, user_id = None, model_keys = []):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.model_keys = model_keys
        self.user_database = database.User_Database()
        
    def add_model(self, key):
        # Adds a model to a user's models
        if key not in self.model_keys:
            user_id = self.user_database.get_id(username=self.username)
            self.user_id = user_id
            self.model_keys.append(key)
            print(self.model_keys)
            self.update_changes()
            return True
        else:
            return "Key already in list."
        
    def remove_model(self, key):
        # Remove a model from a user's models
        if key in self.model_keys:
            self.model_keys.remove(key)
            self.update_changes()
            return True
        else:
            return "Key not in list."
    
    def get_keys(self):
        return self.model_keys
    
    def change_username(self, username):
        # Changes the username within the User class and then saves into the database
        self.username = username
        self.update_changes()
        return True
    
    def change_password(self, password):
        #Changes password within the class and then saves it to database
        self.password = password
        self.update_changes()
        return True
    
    def update_changes(self):
        # Commits all changes done into the database
        self.user_database.update(
            {
                "user_id": self.user_id,
                "username": self.username,
                "password": self.password,
                "model_keys": self.model_keys
            }
        )
        
    ## Register the user in the database
    def register(self, username, password):
        if self.user_database.register(username, password):
            return True
        else:
            return False
        
    ## Log the user in 
    def login(self, username, password):
        print(username, password)
        if self.user_database.login(username, password):
            
            return True
        else:
            return False
    
    def get_id(self):
        return self.user_database.get_id(username=self.username)
        