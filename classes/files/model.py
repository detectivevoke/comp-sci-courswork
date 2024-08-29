import random
import json
import string
import time
import numpy as np
import shutil
import os
import tensorflow as tf
from PIL import Image
from tensorflow.keras.preprocessing import image

  
from .. import runqueue
    
    
class Model:
    def __init__(self, key, user_id):
        ## Set all variables that will be used
        self.user_id = user_id
        self.class_names = []
        self.time_taken  = 0
        self.model = tf.keras.Sequential()
        self.data = dict()
        self.key = key
        self.possible_layers = ["conv2d", "flatten", "dense", "maxpooling2d", "rescaling", "dropout"]
        self.layers = []
    
    def load_config(self):
        pass
            
    def get_data(self):
        ## Prepare the data, with the folder names and the paths to all of the images
        print(self.key)
        for path in os.listdir("./datasets/{}/{}".format(self.user_id ,self.key)):
            self.data[path] = []
            for file in os.listdir("./datasets/{}/{}/{}".format(self.user_id, self.key, path)):
                self.data[path].append(file)
        print(self.data)
        return self.data
    
    ## Adds layering to the models, which is customised
    def add_layer(self, option):
        print(option)
        try:
            ## Check if not in possible layers, else add them
            if str(option).lower() not in self.possible_layers:
                return ["Not a valid layer", False]
            
            elif str(option).lower() == "rescaling":
                self.layers.append("Rescaling")
                self.model.add(tf.keras.layers.Rescaling(1./255, input_shape=(256, 256, 3)))
                
            elif str(option).lower() == "conv2d":
                self.layers.append("Conv2D")
                self.model.add(tf.keras.layers.Conv2D(16,3, padding="same", activation="relu"))
                
            elif str(option).lower() == "maxpooling2d":
                self.layers.append("MaxPooling2D")
                self.model.add(tf.keras.layers.MaxPooling2D())
                
            elif str(option).lower() == "flatten":
                self.layers.append("Flatten")
                self.model.add(tf.keras.layers.Flatten())
                
            elif str(option).lower() == "dense":
                self.layers.append("Dense")
                
                self.model.add(tf.keras.layers.Dense(128, activation="relu"))
            elif str(option).lower() == "dropout":
                self.layers.append("Dropout")
                self.model.add(tf.keras.layers.Dropout(0.2))
            else:
                return ["Not a valid layer", False]
            return ["", True]
        except Exception as e:
            print(e)
            return False
    
    ## Loads dataset from the dir, tensorflow
    def load_dataset(self, path):
        dataset = tf.keras.preprocessing.image_dataset_from_directory(path, image_size=(256,256), batch_size=100, label_mode='int')
        return dataset
 
    def train(self, path, layers, optimizer, metrics, save_path):
        try:
            ## Load dataset
            dataset = self.load_dataset(path)

            ## Add a rescaling layer, which may not have been added at the end. All models should end in a rescaling layer
            self.model.add(tf.keras.layers.Rescaling(1./255, input_shape=(256, 256, 3)))
            ## Add custom layers
            for i in str(layers).split(", "):
                self.add_layer(i.strip())

            ## Get the class names
            labels = []
            for x, label in dataset:
                labels.extend(label.numpy())
            
            ## Compile into one file, train with the data, and save the file to the save path
            self.model.summary()
            self.model.compile(optimizer=optimizer, loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), metrics=metrics)
            self.model.fit(dataset, epochs=10, callbacks=[runqueue.Callback()])
            self.model.save(save_path)

            test_loss, test_acc = self.model.evaluate(dataset)

            return [[test_loss, test_acc], True]
        except:
            return False

    ## Loads the model file from a path
    def load_model(self, path):
        model = tf.keras.models.load_model(path + "model.h5")
        return model

    def classify(self, model_path, image_path):
        ## Loads model and reshapes and changes to RGB to be compatable with model
        model = self.load_model(model_path)
        img = Image.open(image_path)
        img = image.load_img(image_path, target_size=(256, 256))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        
        
        ## Predict and return biggest possibility
        prediction = model.predict(img_array)
        return np.argmax(prediction[0])
    
   