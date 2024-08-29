
from flask import Flask
from .files import custom_queue 
from .files import database
from flask import request
from .files import model
import tensorflow as tf
import time
import threading
import os
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


global progress
progress = 0

recog_queue = custom_queue.Recognition()
dataset_queue = custom_queue.Dataset()
prediction_queue = custom_queue.Predict()

predictions = {}

## Callback to get the % for the progress on prediction
class Callback(tf.keras.callbacks.Callback):
    def __init__(self):
        super().__init__()
    
    def on_epoch_begin(self, batch, logs=None):
        global progress
        requests.post("http://127.0.0.1:4999/update_progress")
        
    def send_progress(self):
        pass
          

def runqueue():
    while True:
        print(dataset_queue.is_empty(), recog_queue.is_empty(), prediction_queue.is_empty())
        ## If the prediction queue is empty, pass, else, predict
        if not prediction_queue.is_empty():
            prediction_queue.dequeue()
            print(prediction_queue.get_queue())
            next_prediction = prediction_queue.get_queue()[0]
            model_key = next_prediction[0]
            user_id = next_prediction[1]
            model_path = next_prediction[2]
            image_path = next_prediction[3]
            ## Load and clasify the model
            current_model = model.Model(user_id=user_id, key=model_key)

            classification = current_model.classify(model_path=model_path, image_path=image_path)
            ## Get class names
            directory = "./datasets/{}/{}/images".format(user_id, model_key)
            folders = []
            for root, dirs, files in os.walk(directory):
                folders.extend(dirs)
            ## Set the prediction within the dictionary, which can then be called for elsewhere
            predictions[model_key] = [folders[classification]]

        
        ## Check if dataset and training queue is empty
        if not dataset_queue.is_empty():
            next_dataset = dataset_queue.get_queue()[0]
            next_recognition = recog_queue.get_queue()[0]
            ## Get arguements
            model_key = next_recognition[0]
            directory = next_dataset[0]
            layers = next_recognition[3]
            
            dataset_queue.dequeue()
            recog_queue.dequeue()
            ## Create the model, and train with the arguements
            user_id = database.User_Database().get_user_id(model_key=model_key)[0]
            current_model = model.Model(key=model_key, user_id=user_id)
            training = current_model.train(path=directory, layers=layers, optimizer="adam", metrics=["accuracy"], save_path="./datasets/{}/{}/model.h5".format(user_id, model_key))

        else:
            time.sleep(10)
    
    
    
@app.route("/")
def main():
    pass
## Adds the user's post request to the queue, based on priority
@app.route("/add", methods=["GET", "POST"])
def add():
    
    if dataset_queue.is_full():
        return [False, "Queue Full"]
    data = request.get_json()
    print("THIS IS DATA: {}".format(data))
    if data["predict"]:
        ## Gets the arguements and queues the request
        model_key = data["model_key"]
        user_id = data["user_id"]
        priority = data["priority"]
        model_path = data["model_path"]
        image_path = data["image_path"]
        prediction_queue.enqueue(data = [model_key, user_id, model_path, image_path], priority=priority)
    else:
        ## Gets the arguements and queues the request
        directory = data["dirs"]
        model_key = data["model_key"]
        class_names = data["class_names"]
        priority = data["priority"]
        layers = data["layers"]
        
        dataset_queue.enqueue(data=[directory], priority=priority)
        
        recog_queue.enqueue(data=[model_key, directory, class_names, layers], priority=priority)
        
    return "True"


## Remove the first item from the queue
@app.route("/pop", methods=["GET", "POST"])
def remove():
    recog_queue.dequeue()
    dataset_queue.dequeue()
    return "True"

## Get the queues
@app.route("/get", methods=["GET", "POST"])
def get_queue():
    return dataset_queue.get_queue(), recog_queue.get_queue(), prediction_queue.get_queue()

## Get the overall progress of the training
@app.route("/get_progress", methods=["GET"])
def get_progress():
    global progress
    return {"progress_percentage": progress}

## Get the classification result
@app.route("/get_classification", methods=["GET"])
def get_class():
    global predictions
    model_key = request.args.get('model_key')
    if model_key in predictions:
        return predictions[model_key]
    else:
        return "loading..."

## Edit the amount of progress to occur, called from inside the callback
@app.route("/update_progress", methods=["POST"])
def update():
    global progress
    progress += 10
    return "True"

if __name__ == "__main__":
    queue_thread = threading.Thread(target=runqueue)
    queue_thread.start()
    app.run(debug=True, port=4999)