global progress
progress = 0


predictions = {}


class Callback():
    def __init__(self):
        super().__init__()
    
    def on_epoch_begin(self, batch, logs=None):
        global progress
        print("EPOCH: {}".format(batch))
        progress+=10
            
    def send_progress(self):
        pass


import time

while True:
    r = Callback()
    print(progress)
    time.sleep(3)
    r.on_epoch_begin("c")
    