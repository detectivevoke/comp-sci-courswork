import random
import string


class Key:
    def __init__(self):
        pass
    
    def generate_user_id(self):
        return "-".join(self.generate_chars() for x in range(4))
    
    def generate_chars(self):
        return "".join(random.choice(string.ascii_letters) for x in range(5))
    
    def generate_model_key(self):
        return "".join(self.generate_chars() for x in range(5))