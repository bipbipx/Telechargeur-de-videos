import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import sys
from PIL import Image, ImageTk
import os

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

def download_video():
    url = url_entry.get()
    output = output_entry.get()

    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL.")
        return

    if not output:
        messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier de sortie.")
        return

    def run_yt_dlp():
        ydl_opts = {
            'outtmpl': output,
            'progress_hooks': [progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                messagebox.showinfo("Succès", f"Téléchargement terminé. Enregistré sous {output}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")

    thread = threading.Thread(target=run_yt_dlp)
    thread.start()

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d['_percent_str']
        p = p.replace('%', '')
        progress_var.set(float(p))
        app.update_idletasks()
    elif d['status'] == 'finished':
        progress_var.set(100)
        app.update_idletasks()

def browse_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video files", "*.mp4")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)

# Redimensionner le logo
def resize_image(image_path, max_size):
    if not os.path.exists(image_path):
        messagebox.showerror("Erreur", f"Le fichier image {image_path} n'existe pas.")
        return None

    image = Image.open(image_path)
    image.thumbnail((max_size, max_size))
    return ImageTk.PhotoImage(image)

# Obtenir le chemin du fichier image et icône
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Chemin de l'image
logo_path = resource_path("image.png")
icon_path = resource_path("icon.ico")

# Configurer l'application principale
app = tk.Tk()
app.title("Téléchargeur de vidéos")
app.configure(bg="#f0f0f0")

# Ajouter un titre
title_label = tk.Label(app, text="Téléchargeur de vidéos", bg="#f0f0f0", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# Charger et afficher le logo redimensionné
logo = resize_image(logo_path, 150)  # Redimensionne le logo à une taille maximale de 150x150 pixels
if logo:
    logo_label = tk.Label(app, image=logo, bg="#f0f0f0")
    logo_label.pack(pady=10)

# Cadre pour les entrées URL et fichier de sortie
input_frame = tk.Frame(app, bg="#f0f0f0", bd=2, relief="groove")
input_frame.pack(pady=10, padx=20, fill=tk.X)

tk.Label(input_frame, text="URL de la vidéo :", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
url_entry = tk.Entry(input_frame, width=50, font=("Arial", 12))
url_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Nom du fichier de sortie :", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(input_frame, width=50, font=("Arial", 12))
output_entry.grid(row=1, column=1, padx=10, pady=5)

browse_button = tk.Button(input_frame, text="Parcourir...", command=browse_output, bg="#4CAF50", fg="white", font=("Arial", 12))
browse_button.grid(row=1, column=2, padx=10, pady=5)

download_button = tk.Button(app, text="Télécharger", command=download_video, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
download_button.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

log_frame = tk.Frame(app, bg="#f0f0f0", bd=2, relief="groove")
log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

log_text = tk.Text(log_frame, state='disabled', width=70, height=10, font=("Arial", 10))
log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

sys.stdout = TextRedirector(log_text)

# Ajuster automatiquement la taille de la fenêtre
app.update_idletasks()
app.geometry(f"{app.winfo_width()}x{app.winfo_height()}")

# Rendre la fenêtre non redimensionnable
app.resizable(False, False)

# Définir l'icône de l'application
app.iconbitmap(icon_path)

app.mainloop()
