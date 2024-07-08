import yt_dlp
import threading
import time
from tkinter import messagebox
import tkinter as tk
import json

# Global variable to control the download thread
is_paused = False
download_thread = None

def start_download(url, output, schedule_time, convert_format, status_label, history_list, progress_var, progress_label, app):
    def run_yt_dlp():
        ydl_opts = {
            'outtmpl': output,
            'progress_hooks': [progress_hook],
        }
        if convert_format:
            ydl_opts['format'] = convert_format

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                status_label.config(text=f"Téléchargement terminé: {output}")
                history_list.insert(0, output)
                save_history(history_list)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")

    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = p.replace('%', '')
            progress_var.set(float(p))
            progress_label.config(text=f"Téléchargement : {p}%")
            app.update_idletasks()
        elif d['status'] == 'finished':
            progress_var.set(100)
            progress_label.config(text="Téléchargement terminé")
            app.update_idletasks()

    global download_thread
    if download_thread and download_thread.is_alive():
        messagebox.showerror("Erreur", "Un téléchargement est déjà en cours.")
        return

    if schedule_time:
        download_thread = threading.Thread(target=schedule_download, args=(schedule_time, run_yt_dlp, status_label))
    else:
        download_thread = threading.Thread(target=run_yt_dlp)
    download_thread.start()

def pause_download(status_label):
    global is_paused
    is_paused = True
    status_label.config(text="Téléchargement en pause")

def resume_download(status_label, convert_format, history_list, app):
    global is_paused
    is_paused = False
    status_label.config(text="Téléchargement repris")
    if download_thread:
        start_download(download_thread, convert_format, history_list, app)

def schedule_download(schedule_time, download_function, status_label):
    delay = (time.mktime(time.strptime(schedule_time, "%Y-%m-%d %H:%M:%S")) - time.time())
    if delay > 0:
        status_label.config(text=f"Téléchargement planifié dans {delay} secondes")
        time.sleep(delay)
    download_function()

def load_history(history_list):
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
            for item in history:
                history_list.insert(0, item)
    except FileNotFoundError:
        pass

def save_history(history_list):
    history = history_list.get(0, tk.END)
    with open('history.json', 'w') as f:
        json.dump(history, f)
