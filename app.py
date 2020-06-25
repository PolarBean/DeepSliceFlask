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

"""
# TODONE: Create a function that creates a folder if it doesn't exist.
# TODONE: Try and get rid of session['images'] and use session['unique_folder'] instead to gather all images in the folder.
# TODONE: Determine how the files should be saved. UNIQUE_FOLDER.csv, or UNIQUE_FOLDER/sub/results.csv
# TODO: Try and parse the unique folder as a string to the url
# TODONE: Change Brain_Images folder to Brain_Files
# TODO: Make a query parameter for the unique folder - Then set the new session to be that unique folder
# TODO: Remove app.config["FILE_FOLDER"] leading folder in unique_folder. Simplify? <- 

import os, uuid, sys
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
app.config["RESULTS"] = RESULTS_FILE


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    print("HOME")
    if request.args.get("unique_folder"):
        # print(request.args.get("unique_folder"))
        set_session(request.args.get("unique_folder"))
    if "unique_folder" in session and session["unique_folder"] is not None:
        completed = get_some()
        # Run it once more as the necessary files should be downloaded.
        if not completed:
            get_some()
        return render_template("public/index.html", unique=session["unique_folder"])

    return render_template("public/index.html")


@app.route("/get-results/<path:unique>/<type>")
def get_results(unique, type):
    print("Hey")
    print(app.config["FILE_FOLDER"] + unique + app.config["RESULTS"] + "." + type)
    try:
        return send_from_directory(app.config["FILE_FOLDER"] + unique, filename=app.config["RESULTS"] + "." + type, as_attachment=True)
    except TypeError:  # Occurs when session["unique_folder"] is not set.
        abort(404)
    except FileNotFoundError:  # Occurs when the file is not found in the directory listed.
        abort(404)


@app.route("/clear-session", methods=["GET", "POST"])
def clear_session():
    session["unique_folder"] = None
    session.modified = True
    return redirect(url_for("home"))


@app.route("/process-image", methods=["POST"])
def process_image():
    image_names = []
    if request.method == "POST" and "images" in request.files:
        # print('len: ' + str(len(request.files.getlist('images'))))
        create_folder(app.config["FILE_FOLDER"])

        unique_str = str(uuid.uuid4().hex)
        # Check first occurrence to see if there actually is a file.
        # Probably a better way to check if user submitted form without a file
        if request.files.getlist("images")[0].filename != "":
            for image in request.files.getlist("images"):
                if image.filename == "":
                    flash("No selected image")
                    return redirect(redirect(url_for("home")))
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    create_folder(app.config["FILE_FOLDER"] + unique_str)
                    create_folder(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"])
                    image.save(
                        os.path.join(app.config["FILE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"], filename,)
                    )
                    image_names.append(filename)
            session["unique_folder"] = unique_str
    return redirect(url_for("home"))


# TODO: Set the session as the folder (Can't be done until we remove FILE_FOLDER from session['unique_folder'])
def set_session(folder):
    print(folder)
    if os.path.isdir(folder):
        print("It... exists?")


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


def get_some():
    if not os.path.exists(app.config["FILE_FOLDER"] + session["unique_folder"] + "/" + app.config["RESULTS"] + ".csv"):
        try:
            sys.path.insert(0, os.getcwd() + "/deep_slice")
            from deep_slice.DeepSlice import DeepSlice

            # print(session["unique_folder"])
            Model = DeepSlice(app.config["DEEP_SLICE_FOLDER"] + "Synthetic_data_final.hdf5")
            Model.Build(app.config["DEEP_SLICE_FOLDER"] + "xception_weights_tf_dim_ordering_tf_kernels.h5")
            Model.predict(app.config["FILE_FOLDER"] + session["unique_folder"])  # Folder Name
            Model.Save_Results(app.config["FILE_FOLDER"] + session["unique_folder"] + "/" + app.config["RESULTS"])  # FileName + CSV / XML
            return True
        except ImportError as e:
            # Need to download the Deep_Slice files from github to perform processing.
            get_deep_slice()
            return False
    else:
        # File already exists. Already performed processing.
        return True


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)
