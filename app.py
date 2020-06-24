# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 04:14:37 2020

@author: ThermoDev
"""
# TODONE: Create a function that creates a folder if it doesn't exist.
# TODO: Try and get rid of session['images'] and use session['unique_folder'] instead to gather all images in the folder.
# TODO: Determine how the files should be saved. UNIQUE_FOLDER.csv, or UNIQUE_FOLDER/sub/results.csv

import os, uuid, sys
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_from_directory,
    abort,
    session,
)
from werkzeug.utils import secure_filename
from git.repo.base import Repo

# Test Image Plot
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

IMAGE_FOLDER = "brain_images/"
DEEP_SLICE_FOLDER = "deep_slice/"
SUB_FOLDER = "sub/"
RESULTS_FILE = "Results"
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
app.config["IMAGE_FOLDER"] = IMAGE_FOLDER
app.config["DEEP_SLICE_FOLDER"] = DEEP_SLICE_FOLDER
app.config["SUB_FOLDER"] = SUB_FOLDER
app.config["RESULTS"] = RESULTS_FILE


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    print("Home Hit!")
    if "images" in session and session["images"] is not None:
        print(session["images"])
        print(get_some())
        return render_template("public/index.html", images=session["images"])
    return render_template("public/index.html")


@app.route("/get-image/<image_name>")
def get_image(image_name):
    try:
        return send_from_directory(session["unique_folder"] + "/" + app.config["SUB_FOLDER"], filename=image_name,)
    except TypeError:  # Occurs when session["unique_folder"] is not set.
        abort(404)
    except FileNotFoundError:  # Occurs when the file is not found in the directory listed.
        abort(404)


@app.route("/clear-session", methods=["GET", "POST"])
def clear_session():
    session["images"] = None
    session["unique_folder"] = None
    session.modified = True
    return redirect(url_for("home"))


@app.route("/process-image", methods=["POST"])
def process_image():
    image_names = []
    if request.method == "POST" and "images" in request.files:
        # print('len: ' + str(len(request.files.getlist('images'))))
        create_folder(app.config["IMAGE_FOLDER"])

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
                    create_folder(app.config["IMAGE_FOLDER"] + unique_str)
                    create_folder(app.config["IMAGE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"])
                    image.save(
                        os.path.join(
                            app.config["IMAGE_FOLDER"] + unique_str + "/" + app.config["SUB_FOLDER"], filename,
                        )
                    )
                    image_names.append(filename)
            session["images"] = image_names
            session["unique_folder"] = app.config["IMAGE_FOLDER"] + unique_str
    return redirect(url_for("home"))


def create_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def get_deep_slice():
    if not os.path.exists(app.config["IMAGE_FOLDER"]):
        Repo.clone_from(
            "https://github.com/PolarBean/DeepSlice", app.config["DEEP_SLICE_FOLDER"],
        )


def get_some():
    try:
        sys.path.insert(0, os.getcwd() + "/deep_slice")
        from deep_slice.DeepSlice import DeepSlice

        # print(session["unique_folder"])
        Model = DeepSlice(app.config["DEEP_SLICE_FOLDER"] + "Synthetic_data_final.hdf5")
        Model.Build(app.config["DEEP_SLICE_FOLDER"] + "xception_weights_tf_dim_ordering_tf_kernels.h5")
        Model.predict(session["unique_folder"])  # Folder Name
        Model.Save_Results(session["unique_folder"])  # FileName + CSV / XML
        return "Completed"
    except ImportError as e:
        print("NO WAY!")
        print(e)
        get_deep_slice()


if __name__ == "__main__":

    app.run(debug=True, port=5000, use_reloader=True)
