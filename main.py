import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import sys
from PIL import Image, ImageTk
import os
import re

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
    # Simple URL validation
    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_regex, url) is not None

def validate_output_filename(filename):
    # Basic validation for output filename
    return len(filename.strip()) > 0

def download_video():
    url = url_entry.get()
    output = output_entry.get()

    if not validate_url(url):
        messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
        return

    if not validate_output_filename(output):
        messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier de sortie valide.")
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
                add_to_history(url, output)
        except yt_dlp.utils.DownloadError as e:
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur inattendue est survenue : {e}")

    thread = threading.Thread(target=run_yt_dlp)
    thread.start()

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d['_percent_str']
        p = p.replace('%', '')
        progress_var.set(float(p))
        progress_label.config(text=f"Téléchargement : {p}%")
        app.update_idletasks()
    elif d['status'] == 'finished':
        progress_var.set(100)
        progress_label.config(text="Téléchargement : 100%")
        app.update_idletasks()

def browse_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video files", "*.mp4")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)

def show_about():
    messagebox.showinfo("À propos", "Téléchargeur de vidéos v1.0\nDéveloppé par [Votre Nom]")

def quit_app():
    app.quit()

def add_to_history(url, output):
    history_list.insert(tk.END, f"{url} -> {output}")

def clear_history():
    history_list.delete(0, tk.END)

def export_history():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as f:
            for item in history_list.get(0, tk.END):
                f.write("%s\n" % item)
        messagebox.showinfo("Exportation réussie", f"Historique exporté vers {file_path}")

def search_history(*args):
    search_term = search_var.get().lower()
    history_list.delete(0, tk.END)
    for item in history:
        if search_term in item.lower():
            history_list.insert(tk.END, item)

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
logo_path = resource_path("assets/image.png")
icon_path = resource_path("assets/icon.ico")

# Configurer l'application principale
app = tk.Tk()
app.title("Téléchargeur de vidéos")
app.configure(bg="#e0e0e0")

# Définir l'icône de l'application
app.iconbitmap(icon_path)

# Utiliser un thème
style = ttk.Style(app)
style.theme_use("clam")

# Ajouter un menu
menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Quitter", command=quit_app)
menubar.add_cascade(label="Fichier", menu=filemenu)
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="À propos", command=show_about)
menubar.add_cascade(label="Aide", menu=helpmenu)
app.config(menu=menubar)

# Ajouter un titre
title_label = tk.Label(app, text="Téléchargeur de vidéos", bg="#e0e0e0", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

# Charger et afficher le logo redimensionné
logo = resize_image(logo_path, 150)  # Redimensionne le logo à une taille maximale de 150x150 pixels
if logo:
    logo_label = tk.Label(app, image=logo, bg="#e0e0e0")
    logo_label.pack(pady=10)

# Cadre pour les entrées URL et fichier de sortie
input_frame = tk.Frame(app, bg="#e0e0e0", bd=2, relief="groove")
input_frame.pack(pady=10, padx=20, fill=tk.X)

tk.Label(input_frame, text="URL de la vidéo :", bg="#e0e0e0", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
url_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
url_entry.grid(row=0, column=1, padx=10, pady=5)
url_entry_tooltip = tk.Label(input_frame, text="Entrez l'URL de la vidéo à télécharger", bg="#e0e0e0", font=("Arial", 10), fg="grey")
url_entry_tooltip.grid(row=0, column=2, padx=10, pady=5)

tk.Label(input_frame, text="Nom du fichier de sortie :", bg="#e0e0e0", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
output_entry.grid(row=1, column=1, padx=10, pady=5)
output_entry_tooltip = tk.Label(input_frame, text="Entrez le nom du fichier de sortie (par exemple, video.mp4)", bg="#e0e0e0", font=("Arial", 10), fg="grey")
output_entry_tooltip.grid(row=1, column=2, padx=10, pady=5)

browse_button = tk.Button(input_frame, text="Parcourir...", command=browse_output, bg="#4CAF50", fg="white", font=("Arial", 12))
browse_button.grid(row=1, column=3, padx=10, pady=5)

download_button = tk.Button(app, text="Télécharger", command=download_video, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
download_button.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

progress_label = tk.Label(app, text="Téléchargement : 0%", bg="#e0e0e0", font=("Arial", 12))
progress_label.pack(pady=5)

# Cadre pour les logs et l'historique
log_history_frame = tk.Frame(app, bg="#e0e0e0", bd=2, relief="groove")
log_history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

log_frame = tk.Frame(log_history_frame, bg="#e0e0e0")
log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

log_label = tk.Label(log_frame, text="Logs", bg="#e0e0e0", font=("Arial", 14, "bold"))
log_label.pack(pady=5)

log_text = tk.Text(log_frame, state='disabled', width=70, height=10, font=("Arial", 12), bg="#f0f0f0", fg="#333")
log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

history_frame = tk.Frame(log_history_frame, bg="#e0e0e0")
history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

history_label = tk.Label(history_frame, text="Historique des Téléchargements", bg="#e0e0e0", font=("Arial", 14, "bold"))
history_label.pack(pady=5)

search_var = tk.StringVar()
search_var.trace("w", search_history)
search_entry = tk.Entry(history_frame, textvariable=search_var, font=("Arial", 12), bg="#f0f0f0")
search_entry.pack(pady=5, padx=10, fill=tk.X)

history_list = tk.Listbox(history_frame, font=("Arial", 12), bg="#f0f0f0", fg="#333")
history_list.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

clear_history_button = tk.Button(history_frame, text="Nettoyer l'historique", command=clear_history, bg="#4CAF50", fg="white", font=("Arial", 12))
clear_history_button.pack(pady=5)

export_history_button = tk.Button(history_frame, text="Exporter l'historique", command=export_history, bg="#4CAF50", fg="white", font=("Arial", 12))
export_history_button.pack(pady=5)

sys.stdout = TextRedirector(log_text)

# Ajuster automatiquement la taille de la fenêtre
app.update_idletasks()
app.geometry(f"{app.winfo_width()}x{app.winfo_height()}")

# Rendre la fenêtre non redimensionnable
app.resizable(False, False)

app.mainloop()
