""" Any utility functions for paths, images, etc. """

import os
import platform

def get_default_directory():
    system = platform.system()

    if system == "Windows":
        path = os.path.join(os.getenv("APPDATA"), "Catnip")
    elif system == "Linux":
        path = os.path.join(os.sep, "var", "lib", "catnip")
    elif system == "Darwin":
        path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Catnip")
    else:
        path = os.path.join(os.getcwd(), "appdata")
    
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    
    return path
