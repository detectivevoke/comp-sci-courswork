from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from classes.files import custom_queue, model, user, key, database

from .forms import *
from .forms import UserCreationForm

import os
import zipfile

import requests
recog = custom_queue.Recognition()
datasets = custom_queue.Dataset()
gen_key = key.Key()
## Returns the main home page
def main(request):
    return render(request, 'main/home.html')

## Training Function
@csrf_exempt
def train(request):
    if request.method == "POST":
        ## Uses custom layers if there is some, else it uses default layers
        layers = request.POST.get("layers")
        if layers == "":
            layering = "rescaling, conv2d, maxpooling2d, conv2d, maxpooling2d, conv2d, maxpooling2d, dropout, flatten, dense, dense"
        else:
            layering = layers
        ## Generate Model key to be used
        model_key = gen_key.generate_model_key()
        ## Create form and check if its valid
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if user is logged in, if not, return a message to ask them to log in
            try:
                r = request.COOKIES["logged_in"]
            except:
                return render(request, "main/train.html", {"msg": "Log in or sign up to continue"})
            if request.COOKIES["logged_in"]:
                ## Get User ID
                username = request.COOKIES["username"]
                id = user.User(username=username).get_id()
                ## Create dataset file to download the files to
                directory = "./datasets/{}/{}".format(id, model_key)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                ## Extract files into the directory
                with zipfile.ZipFile(request.FILES["file"], 'r') as zip_ref:
                    zip_ref.extractall(directory)
                ## Gets the class count and the names of the classes
                class_count = 0
                folders = []
                for root, dirs, files in os.walk(directory):
                    class_count += len(dirs)
                    folders.extend(dirs)
                    
        ## Check if user is logged in to get priority, if not, they are not priority
        try:
            logged_in = request.COOKIES['logged_in']
            if logged_in:
                priority = True
                current_user = user.User(username=username)
                current_user.add_model(model_key)    
        except KeyError:
            priority = False
        # Return with all the information for user to check
        return render(request, "main/train.html", {"upload": True, "classes": class_count, "class_names": folders, "dirs": directory, "model_key": model_key, "priority": priority, "layers": layering})
    
    return render(request, "main/train.html")

@csrf_exempt
def start_training(request):
    if request.method == "POST":
        ## Get the data from the post request to start training
        class_names = request.POST.get("class_names")
        dirs = request.POST.get("dirs")
        priority = request.POST.get("priority")
        model_key = request.POST.get("model_key")
        layers = request.POST.get("layers")
        ## Send the data to the API, to train
        req = requests.post("http://127.0.0.1:4999/add", json={
            "class_names": class_names,
            "dirs": dirs,
            "model_key": model_key,
            "priority": priority,
            "layers": layers,
            "predict": False
        })
        ## Return page
        return render(request, "main/training_loading.html")

def register(request):
    if request.method == "POST":
        ## Check if form is valid and get the data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password2"]
            user_class = user.User()
            ## Register the user and set the cookie and return to home
            if user_class.register(username=username, password=password):
                response = redirect("/")
                response.set_cookie("username", username)
                response.set_cookie("logged_in", True)
            else:
                ## Return to register page with error if the registration failed
                return render(request, "main/register.html", {"msg": "An error has occurred, contact admin."})
            return response
    else:
        ## Create form if not a post request
        form = UserCreationForm()
    return render(request, "main/register.html", {"form": form})

def login(request):
    if request.method == "POST":
        ## Check if form is valid and get the data from the request
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            ## If the database returns the login as true, return to home page with cookies set
            if user.User().login(username=username, password=password):
                response = redirect("/")
                response.set_cookie("logged_in", True)
                response.set_cookie("username", username)
                return response
            else:
                ## Return to login page saying incorrect credentials
                return render(request, "main/login.html", {"msg": "Incorrect credentials, try again."})
    else:
        ## Create form if not a post request
        form = LoginForm()
    return render(request, "main/login.html", {"form": form})

def classify(request):
    if request.method == "POST":
        ## Get the correct arguements
        model_key = request.POST.get("model_key")
        username = request.COOKIES["username"]
        user_id = user.User(username=username).get_id()

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            ## Get the image and write into a file in the model's directory
            file = request.FILES["file"]
            path = os.path.join("./datasets/{}/{}/{}".format(user_id, model_key, file))
            open(path, "a")
            with open(path, "wb") as file:
                for chunk in request.FILES["file"].chunks():
                    file.write(chunk)

            ## Send request to the API to predict
            r = requests.post("http://127.0.0.1:4999/add", json= {
                "model_key": model_key,
                "user_id": user_id,
                "predict": True,
                "priority": True,
                "model_path": "./datasets/{}/{}/".format(user_id, model_key),
                "image_path": path
            })
        ## Return loading screen
        return render(request, "main/prediction_loading.html", {"model_key": model_key})
    ## Checked if the user is logged in
    try:
        username = request.COOKIES["username"]
    except:
        return render(request, "main/predict.html", {"msg": "Please log in or sign up."})
    
    ## Get the possible model keys that can be inputted
    user_id = user.User(username=username).get_id()
    folders = []
    for folder in os.listdir("./datasets/{}".format(user_id)):
        if os.path.isdir(os.path.join("./datasets/{}".format(user_id), folder) ):
            folders.append(folder)
    

    form = UploadFileForm()
    return render(request, "main/predict.html", {"folders": folders, "form": form} )