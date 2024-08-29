class Encrypt:
    def __init__(self):
        self.shift = 5
        self.ord_a = 97
        self.ord_A = 65
    
    def encrypt(self, text):
        completed = ""
        for char in text:
            if char.isalpha():
                uni = ord(char)
                if char.islower():
                    shifted = (uni - self.ord_a + self.shift) % 26 + self.ord_a
                else:
                    shifted = (uni - self.ord_A + self.shift) % 26 + self.ord_A
                    
                completed += chr(shifted)
            else:
                completed += char

        return completed
                
    def decrypt(self, text):
        completed  = ""
        
        for char in text:
            if char.isalpha():
                uni = ord(char)
                if char.islower():
                    shifted = (uni - self.ord_a - self.shift) % 26 + self.ord_a
                else:
                    shifted = (uni - self.ord_A - self.shift) % 26 + self.ord_A
                    
                completed += chr(shifted)
            else:
                completed += char

        return completed