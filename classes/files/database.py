import sqlite3
import random
import time

from . import key
from . import encryption
import json


class Database:
    def __init__(self):
        self.db = sqlite3.connect("database.db")
        self.cursor = self.db.cursor()
        self.encryption = encryption.Encrypt()
        self.key_generation = key.Key()
        
        
class User_Database(Database):
    
    def __init__(self):
        super().__init__()
    ## Add the user to the database, generate the key and their model keys
    def register(self, username, password):
        ## Check if username is already in use
        if (len(self.cursor.execute("SELECT username FROM User WHERE username=:name", {"name": username}).fetchall())) == 0:
            self.cursor.execute("INSERT INTO User VALUES (:username, :password, :model_keys, :UserID);",{"UserID": self.key_generation.generate_user_id(),"username": username,"password": self.encryption.encrypt(password),"model_keys": json.dumps([])})
            self.db.commit()
            return True
        else:
            return False
    ## Gets the user's ID from their username
    def get_id(self, username):
        r = self.cursor.execute(
            "SELECT user_id FROM User WHERE username=:username",
            {"username": username},
        ).fetchall()[0][0]
        return r
    ## Gets the user's ID from a model key
    def get_user_id(self, model_key):
        query = "SELECT user_id FROM User WHERE model_keys LIKE :model_key"
        model_key_pattern = f"%{model_key}%"

        r = self.cursor.execute(query, {"model_key": model_key_pattern})

        c = r.fetchone()
        
        return c
    ## Updates a user's password
    def update_password(self, userid, password):
        self.cursor.execute(
            "UPDATE User SET password = :password WHERE user_id=:UserID",
            {"UserID": userid, "password": password},
        )
        self.db.commit()
        return True
    
    ## Pushes all updates to any data
    def update(self, data):
        username = data["username"]
        password = data["password"]
        model_keys = data["model_keys"]
        user_id = data["user_id"]
        
        r = self.cursor.execute(
            "SELECT * FROM User WHERE user_id=:user_id",
            {"user_id": user_id}).fetchall()
        
        prev = r[0]
        if username == None:
            pass
        else:
            if username != prev[0]:
                self.cursor.execute("UPDATE User SET username = :username WHERE user_id=:UserID",{
                    "UserID": user_id,
                    "username": username})
        if password == None:
            pass
        else:
            if self.encryption.encrypt(password) != prev[1]:
                self.cursor.execute("UPDATE User SET password = :password WHERE user_id=:UserID",{
                    "UserID": user_id,
                    "password": self.encryption.encrypt(password)
                })
        if list(model_keys) == []:
            pass
        else:
            if model_keys != prev[2]:
                l = eval(prev[2])
                for key in model_keys:
                    if key not in l:
                        l.append(key)
                self.cursor.execute("UPDATE User SET model_keys = :model_keys WHERE user_id=:UserID",{
                    "UserID": user_id,
                    "model_keys": str(l) 
                })
            else:
                return False
        
        self.db.commit()
        
        return True
    
    ## Login for user, returns False if there is an error
    def login(self, username, password):
        try:
            info = self.cursor.execute(
                "SELECT * FROM User WHERE username=:username", {"username": username}
            ).fetchall()[0]
            if len(info) != 0:
                print(info[1], self.encryption.encrypt(password))
                if self.encryption.encrypt(password) == info[1]:
                    self.db.commit()

                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(e)
            return False