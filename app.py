# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 04:14:37 2020

@author: ThermoDev
@description:
    This is the FLASK based Python web app for the DEEP_SLICE library.

    Each image uploaded will be saved in the FILE_FOLDER and SUBFOLDER, 
        e.g., FILE_FOLDER/SUB_FOLDER/{images}
    The results will then be saved in the FILE_FOLDER:
        e.g., FILE_FOLDER/results.csv
    User will then be able to download those results by clicking on "Download CSV" or "Download XML"

"""
# TODONE: Create a function that creates a folder if it doesn't exist.
# TODONE: Try and get rid of session['images'] and use session['unique'] instead to gather all images in the folder.
# TODONE: Determine how the files should be saved. unique.csv, or unique/sub/results.csv
# TODONE: Change Brain_Images folder to Brain_Files
# TODONE: Remove app.config["FILE_FOLDER"] leading folder in unique. Simplify?
# TODONE: Try and parse the unique folder as a string to the url
# TODONE: Make a query parameter for the unique folder - Then set the new session to be that unique folder
# TODONE: Set the session as the folder (Can't be done until we remove FILE_FOLDER from session['unique'])
# TODONE: Clear session entirely. Remove button from Index.html. UPDATE: Keep session as users may want to return to the homepage and still view their results.
# TODONE: Check if it is currently predicting, wait until it finished - Syncrhonous?
# TODO: Deploy to server 
# TODO: Change Threading to USWGI lock once deployed to server
# TODO: Create User Registration, Login Page
# TODO: Create Database for Users
# TODO: Hook up Registration and Login with Database
# TODO: Create a Dashboard for Users

import os, uuid, sys, threading
sys.path.insert(0, "/home/Thermodev/DeepSliceFlask")
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_from_directory,
    send_file,
    abort,
    session,
)
from werkzeug.utils import secure_filename
from git.repo.base import Repo

# Test Image Plot
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

FILE_FOLDER = "brain_files/"
DEEP_SLICE_FOLDER = "deep_slice/"
SUB_FOLDER = "images/"
FOLDER_NAME = SUB_FOLDER[:-1]
RESULTS_FILE = "results"
ALLOWED_EXTENSIONS = {
    "tiff",
    "pjp",
    "jfif",
    "pjpeg",
    "tif",
    "gif",
    "svg",
    "bmp",
    "svgz",
    "webp",
    "ico",
    "xbm",
    "dib",
    "png",
    "jpg",
    "jpeg",
}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["FILE_FOLDER"] = FILE_FOLDER
app.config["DEEP_SLICE_FOLDER"] = DEEP_SLICE_FOLDER
app.config["SUB_FOLDER"] = SUB_FOLDER
app.config["FOLDER_NAME"] = FOLDER_NAME
app.config["RESULTS"] = RESULTS_FILE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

sem = threading.Semaphore()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def call_get_data(unique):
    completed = get_data(unique)
    # Run it once more as the necessary files should be downloaded.
    if not completed:
        completed = get_data(unique)
    if completed:
        return True
    else: 
        return False

# Route for not yet or about to be processed brain images
@app.route("/", methods=["GET"])
def home():
    print("HOME")
    # If session["unique"] is here, just redirect them to a route of their previously processed info
    if "unique" in session and session["unique"] is not None:
        unique = session["unique"]
        success_call = call_get_data(unique)
        print(success_call)
        return redirect(url_for("home_unique", unique=session["unique"]))

    # Return index template along with error
    return render_template("public/index.html")

# Route for already processed brain images
@app.route("/<unique>", methods=["GET"])
def home_unique(unique):
    success_call = call_get_data(unique)
    print(success_call)
    set_session(unique)
    return render_template("public/index.html", unique=unique)

@app.route("/get-results/<path:unique>/<type>")
def get_results(unique, type):
    print(app.config["FILE_FOLDER"] + unique + app.config["RESULTS"] + "." + type)
    try:
        return send_from_directory(
            app.config["FILE_FOLDER"] + unique, filename=app.config["RESULTS"] + "." + type, as_attachment=True
        )
    except TypeError:  # Occurs when session["unique"] is not set.
        abort(404)
    except FileNotFoundError:  # Occurs when the file is not found in the directory listed.
        abort(404)

@app.route("/clear-session", methods=["GET", "POST"])
def clear_session():
    session["unique"] = None
    session.modified = True
    return redirect(url_for("home"))

@app.route("/setup-images", methods=["POST"])
def setup_images():
    session["unique"] = str(uuid.uuid4().hex)
    unique_str = session["unique"] 
    create_folder(app.config["FILE_FOLDER"])
    create_folder(app.config["FILE_FOLDER"] + unique_str)
    create_folder(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"])
    return "DONE"

@app.route("/upload-image", methods=["POST"])
def upload_image():
    unique_str = ""
    print(request.files)

    if request.method == "POST" and "image" in request.files:
        # print('len: ' + str(len(request.files.getlist('images'))))

        unique_str = session["unique"] 

        if "image" in request.files:
            print("Hello World")

        print(request.files['image'])
        image = request.files['image']
        filename = secure_filename(image.filename) 
        image.save(os.path.join(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"], filename))
        #session["unique"] = unique_str
        # Check first occurrence to see if there actually is a file
        # Probably a better way to check if user submitted form without a file
        # if request.files.getlist("images")[0].filename != "":
        #     for image in request.files.getlist("images"):
        #         if image.filename == "":
        #             flash("No selected image")
        #             return redirect(redirect(url_for("home")))
        #         if image and allowed_file(image.filename):
        #             filename = secure_filename(image.filename)
        #             create_folder(app.config["FILE_FOLDER"] + unique_str)
        #             create_folder(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"])
        #             image.save(
        #                 os.path.join(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"], filename)
        #             )
        #             image_names.append(filename)
        #     session["unique"] = unique_str
    return url_for("home_unique", unique=unique_str)

def set_session(unique):
    print(unique)
    session["unique"] = unique

def create_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        print("Dir already exists at: " + dir)

def get_deep_slice():
    if not os.path.exists(app.config["DEEP_SLICE_FOLDER"]):
        Repo.clone_from(
            "https://github.com/PolarBean/DeepSlice", app.config["DEEP_SLICE_FOLDER"],
        )

def get_data(unique):
    if not os.path.exists(app.config["FILE_FOLDER"] + unique + "/" + app.config["RESULTS"] + ".csv"):
        try:
            sys.path.insert(0, os.getcwd() + "/deep_slice")
            from deep_slice.DeepSlice import DeepSlice
            sem.acquire()  # Initiate Lock

            if "MODEL" not in app.config:
                Model = DeepSlice(
                    app.config["DEEP_SLICE_FOLDER"] + "Synthetic_data_final.hdf5",
                    web=True,
                    folder_name=app.config["FOLDER_NAME"])
                Model.Build(app.config["DEEP_SLICE_FOLDER"] + "xception_weights_tf_dim_ordering_tf_kernels.h5")
                app.config["MODEL"] = Model

            Model = app.config["MODEL"]
            Model.predict(app.config["FILE_FOLDER"] + unique)  # Folder Name
            Model.Save_Results(app.config["FILE_FOLDER"] + unique + "/" + app.config["RESULTS"])  # FileName + CSV / XML

            sem.release()  # Release lock
            return True
        except ImportError as e:
            sem.release()
            # Need to download the Deep_Slice files from github to perform processing.
            print("Could not import Deep Slice, or a library in Deep Slice. Importing...")
            print(e)
            get_deep_slice()
            return False
        except Exception as e:
            sem.release()
            return False
    else:
        # File already exists. Already performed processing.
        return True

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)

def create_app():
    return app