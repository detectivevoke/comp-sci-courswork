from datetime import datetime

class Queue():
    def __init__(self):
        self.priority = list()
        self.not_priority = list()
        self.max_length = 20
        
    def enqueue(self, data, priority:bool):
        # Adds the data to the queue, if the queue is not full
        
        if self.is_full():
            return False
        
        if priority:
            self.priority.append(data)
        else:
            self.not_priority.append(data)
        return True
    
    def dequeue(self):
        # Dequeues the first element of data, and returns the data
        if len(self.priority) == 0:
            self.not_priority.pop()
        else:
            self.priority.pop()
        return self.get_queue()
    
    def is_empty(self):
        # Checks if the queue is empty, with nothing inside
        if (len(self.priority) == 0)and (len(self.not_priority) == 0):
            return True
        else:
            return False
    
    def is_full(self):
        # Checks is the queue is full, which is self.max_length
        if (len(self.priority) + len(self.not_priority) == self.max_length):
            return True
        else:
            return False
        
    def get_queue(self):
        #Returns the full queue, not to be used in main code
        return self.priority + self.not_priority
    
class Recognition(Queue):
    def __init__(self):
        # Inherits all functions and variables from Queue class
        super().__init__()
    
    def prepare_data(self, image_link, key):
        # Prepares the data to be queued, with the timestamp to calculate time taken
        return [image_link, key, datetime.now()]

class Dataset(Queue):
    def __init__(self):
        super().__init__()
    
    def prepare_data(self, key):
        return [key, datetime.now()]

class Predict(Queue):
    def __init__(self):
        super().__init__()
        
    