import re
from PIL import Image, ImageTk
import os
import sys
from tkinter import messagebox

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state='disabled')
        self.widget.see("end")

    def flush(self):
        pass

def validate_url(url):
    url_regex = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' 
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_regex, url) is not None

def validate_output_filename(filename):
    return len(filename.strip()) > 0

def resize_image(image_path, max_size):
    if not os.path.exists(image_path):
        messagebox.showerror("Erreur", f"Le fichier image {image_path} n'existe pas.")
        return None

    image = Image.open(image_path)
    image.thumbnail((max_size, max_size))
    return ImageTk.PhotoImage(image)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
