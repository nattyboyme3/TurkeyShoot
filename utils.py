import os, sys


def resource_path(*parts):
    """
    Return path to resource whether running from source or from PyInstaller --onefile.
    Usage: resource_path('assets','sprites','player.png')
    """
    base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base, *parts)