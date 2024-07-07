import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from plyer import notification
import yt_dlp
import threading
import queue
import sys
from PIL import Image, ImageTk
import os
import re
import json
from datetime import datetime
import time

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

def load_language(lang_code):
    with open(resource_path(f"languages/{lang_code}.json"), "r", encoding="utf-8") as file:
        return json.load(file)

def set_language(lang_code):
    global lang
    lang = load_language(lang_code)
    app.title(lang["title"])
    title_label.config(text=lang["title"])
    url_label.config(text=lang["url_label"])
    output_label.config(text=lang["output_label"])
    browse_button.config(text=lang["browse_button"])
    download_button.config(text=lang["download_button"])
    pause_button.config(text=lang["pause_button"])
    resume_button.config(text=lang["resume_button"])
    convert_label.config(text=lang["convert_label"])
    log_label.config(text=lang["logs_label"])
    history_label.config(text=lang["history_label"])
    clear_history_button.config(text=lang["clear_history_button"])
    export_history_button.config(text=lang["export_history_button"])
    filemenu.entryconfig(0, label=lang["menu_quit"])
    settingsmenu.entryconfig(0, label=lang["menu_dark_mode"])
    settingsmenu.entryconfig(1, label=lang["menu_save_queue"])
    settingsmenu.entryconfig(2, label=lang["menu_load_queue"])
    helpmenu.entryconfig(0, label=lang["menu_about"])

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

download_queue = queue.Queue()
current_download = None
paused = False

def download_video():
    url = url_entry.get()
    output = output_entry.get()
    schedule_time = schedule_entry.get()

    if not validate_url(url):
        messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
        return

    if not validate_output_filename(output):
        messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier de sortie valide.")
        return

    if schedule_time:
        try:
            schedule_time = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            delay = (schedule_time - current_time).total_seconds()
            if delay > 0:
                status_label.config(text=f"Téléchargement planifié pour {schedule_time}")
                threading.Timer(delay, lambda: download_queue.put((url, output))).start()
                return
        except ValueError:
            messagebox.showerror("Erreur", "Format de date et heure incorrect. Utilisez AAAA-MM-JJ HH:MM:SS")
            return

    download_queue.put((url, output))
    status_label.config(text=lang["status_in_queue"].format(count=download_queue.qsize()))
    if current_download is None:
        start_next_download()

def start_next_download():
    global current_download
    if not download_queue.empty() and not paused:
        url, output = download_queue.get()
        current_download = (url, output)
        status_label.config(text=lang["status_downloading"].format(url=url))
        thread = threading.Thread(target=run_yt_dlp, args=(url, output))
        thread.start()

def run_yt_dlp(url, output):
    ydl_opts = {
        'outtmpl': output,
        'progress_hooks': [progress_hook],
        'writeinfojson': True,
        'writethumbnail': True,
        'writesubtitles': True,
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': convert_var.get()}] if convert_var.get() else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            messagebox.showinfo("Succès", f"Téléchargement terminé. Enregistré sous {output}")
            notification.notify(
                title="Téléchargement terminé",
                message=f"Le téléchargement de {url} est terminé et enregistré sous {output}.",
                timeout=10
            )
            add_to_history(url, output)
    except yt_dlp.utils.DownloadError as e:
        messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")
        notification.notify(
            title="Erreur de téléchargement",
            message=f"Erreur lors du téléchargement de {url}.",
            timeout=10
        )
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur inattendue est survenue : {e}")
        notification.notify(
            title="Erreur inattendue",
            message=f"Une erreur inattendue est survenue lors du téléchargement de {url}.",
            timeout=10
        )

    global current_download
    current_download = None
    start_next_download()

def pause_download():
    global paused
    paused = True
    status_label.config(text=lang["status_paused"])

def resume_download():
    global paused
    paused = False
    status_label.config(text=lang["status_resumed"])
    start_next_download()

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
    messagebox.showinfo("À propos", lang["about_message"])

def quit_app():
    app.quit()

def add_to_history(url, output):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_list.insert(tk.END, f"{now} | {url} -> {output}")
    save_history()

def clear_history():
    history_list.delete(0, tk.END)
    save_history()

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

def save_queue():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        queue_list = list(download_queue.queue)
        with open(file_path, 'w') as f:
            json.dump(queue_list, f)
        messagebox.showinfo("Sauvegarde réussie", f"File d'attente sauvegardée vers {file_path}")

def load_queue():
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as f:
            queue_list = json.load(f)
        for item in queue_list:
            download_queue.put(item)
        status_label.config(text=lang["status_in_queue"].format(count=download_queue.qsize()))
        messagebox.showinfo("Chargement réussi", f"File d'attente chargée depuis {file_path}")

def save_history():
    history = history_list.get(0, tk.END)
    with open(resource_path("history.json"), 'w') as f:
        json.dump(history, f)

def load_history():
    if os.path.exists(resource_path("history.json")):
        with open(resource_path("history.json"), 'r') as f:
            history = json.load(f)
        for item in history:
            history_list.insert(tk.END, item)

def toggle_dark_mode():
    if dark_mode_var.get():
        app.configure(bg="#2e2e2e")
        title_label.configure(bg="#2e2e2e", fg="#ffffff")
        url_label.configure(bg="#2e2e2e", fg="#ffffff")
        output_label.configure(bg="#2e2e2e", fg="#ffffff")
        convert_label.configure(bg="#2e2e2e", fg="#ffffff")
        input_frame.configure(bg="#2e2e2e")
        log_history_frame.configure(bg="#2e2e2e")
        log_frame.configure(bg="#2e2e2e")
        log_label.configure(bg="#2e2e2e", fg="#ffffff")
        log_text.configure(bg="#3e3e3e", fg="#ffffff")
        history_frame.configure(bg="#2e2e2e")
        history_label.configure(bg="#2e2e2e", fg="#ffffff")
        search_entry.configure(bg="#3e3e3e", fg="#ffffff", insertbackground="white")
        history_list.configure(bg="#3e3e3e", fg="#ffffff")
        status_label.configure(bg="#2e2e2e", fg="#ffffff")
    else:
        app.configure(bg="#e0e0e0")
        title_label.configure(bg="#e0e0e0", fg="#000000")
        url_label.configure(bg="#e0e0e0", fg="#000000")
        output_label.configure(bg="#e0e0e0", fg="#000000")
        convert_label.configure(bg="#e0e0e0", fg="#000000")
        input_frame.configure(bg="#e0e0e0")
        log_history_frame.configure(bg="#e0e0e0")
        log_frame.configure(bg="#e0e0e0")
        log_label.configure(bg="#e0e0e0", fg="#000000")
        log_text.configure(bg="#f0f0f0", fg="#000000")
        history_frame.configure(bg="#e0e0e0")
        history_label.configure(bg="#e0e0e0", fg="#000000")
        search_entry.configure(bg="#f0f0f0", fg="#000000", insertbackground="black")
        history_list.configure(bg="#f0f0f0", fg="#000000")
        status_label.configure(bg="#e0e0e0", fg="#000000")

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

logo_path = resource_path("assets/image.png")
icon_path = resource_path("assets/icon.ico")

app = ThemedTk(theme="clam")
app.title("Téléchargeur de vidéos")
app.configure(bg="#e0e0e0")
app.iconbitmap(icon_path)

style = ttk.Style(app)
style.theme_use("clam")

menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Quitter", command=quit_app)
menubar.add_cascade(label="Fichier", menu=filemenu)
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="À propos", command=show_about)
menubar.add_cascade(label="Aide", menu=helpmenu)

settingsmenu = tk.Menu(menubar, tearoff=0)
dark_mode_var = tk.BooleanVar()
settingsmenu.add_checkbutton(label="Mode Sombre", variable=dark_mode_var, command=toggle_dark_mode)
settingsmenu.add_command(label="Sauvegarder la file d'attente", command=save_queue)
settingsmenu.add_command(label="Charger la file d'attente", command=load_queue)
menubar.add_cascade(label="Paramètres", menu=settingsmenu)

app.config(menu=menubar)

title_label = tk.Label(app, text="Téléchargeur de vidéos", bg="#e0e0e0", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

logo = resize_image(logo_path, 150)
if logo:
    logo_label = tk.Label(app, image=logo, bg="#e0e0e0")
    logo_label.pack(pady=10)

input_frame = tk.Frame(app, bg="#e0e0e0", bd=2, relief="groove")
input_frame.pack(pady=10, padx=20, fill=tk.X)

url_label = tk.Label(input_frame, text="URL de la vidéo :", bg="#e0e0e0", font=("Arial", 14))
url_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
url_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
url_entry.grid(row=0, column=1, padx=10, pady=5)
url_entry_tooltip = tk.Label(input_frame, text="Entrez l'URL de la vidéo à télécharger", bg="#e0e0e0", font=("Arial", 10), fg="grey")
url_entry_tooltip.grid(row=0, column=2, padx=10, pady=5)

output_label = tk.Label(input_frame, text="Nom du fichier de sortie :", bg="#e0e0e0", font=("Arial", 14))
output_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
output_entry.grid(row=1, column=1, padx=10, pady=5)
output_entry_tooltip = tk.Label(input_frame, text="Entrez le nom du fichier de sortie (par exemple, video.mp4)", bg="#e0e0e0", font=("Arial", 10), fg="grey")
output_entry_tooltip.grid(row=1, column=2, padx=10, pady=5)

browse_button = tk.Button(input_frame, text="Parcourir...", command=browse_output, bg="#4CAF50", fg="white", font=("Arial", 12))
browse_button.grid(row=1, column=3, padx=10, pady=5)

schedule_label = tk.Label(input_frame, text="Planifier le téléchargement (AAAA-MM-JJ HH:MM:SS) :", bg="#e0e0e0", font=("Arial", 14))
schedule_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
schedule_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
schedule_entry.grid(row=2, column=1, padx=10, pady=5)

convert_label = tk.Label(input_frame, text="Convertir au format :", bg="#e0e0e0", font=("Arial", 14))
convert_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
convert_var = tk.StringVar()
convert_entry = ttk.Combobox(input_frame, textvariable=convert_var, values=["mp4", "mp3", "avi"], font=("Arial", 14))
convert_entry.grid(row=3, column=1, padx=10, pady=5)

button_frame = tk.Frame(app, bg="#e0e0e0")
button_frame.pack(pady=10)

download_button = tk.Button(button_frame, text="Télécharger", command=download_video, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
download_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(button_frame, text="Pause", command=pause_download, bg="#FFA500", fg="white", font=("Arial", 14, "bold"))
pause_button.grid(row=0, column=1, padx=5)

resume_button = tk.Button(button_frame, text="Reprendre", command=resume_download, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
resume_button.grid(row=0, column=2, padx=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

progress_label = tk.Label(app, text="Téléchargement : 0%", bg="#e0e0e0", font=("Arial", 12))
progress_label.pack(pady=5)

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

status_label = tk.Label(app, text="Prêt", bg="#e0e0e0", font=("Arial", 10), anchor="w")
status_label.pack(side="bottom", fill="x")

sys.stdout = TextRedirector(log_text)

app.update_idletasks()
app.geometry(f"{app.winfo_width()}x{app.winfo_height()}")

app.resizable(False, False)

load_history()

set_language("fr")

app.mainloop()
