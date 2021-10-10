""" Any utility functions for paths, images, etc. """

import os

def get_default_directory():
    if os.name == "nt":
        path = os.path.join(os.getenv("APPDATA"), "Catnip")
    elif os.name in {"linux", "linux2"}:
        path = os.path.join(os.sep, "var", "lib", "catnip")
    elif os.name in "darwin":
        path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Catnip")
    
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    
    return path
