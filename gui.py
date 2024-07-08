import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
from downloader import start_download, pause_download, resume_download, load_history, save_history
from settings import set_language, LANGUAGES
from helpers import TextRedirector, resource_path, resize_image
import sys
import json  # Ajouter l'importation de json


class VideoDownloaderApp:
    def __init__(self):
        self.app = ThemedTk(theme="clam")
        self.app.title("Téléchargeur de vidéos")
        self.app.configure(bg="#e0e0e0")
        self.app.iconbitmap(resource_path("assets/icon.ico"))
        self.current_language = "fr"
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style(self.app)
        style.theme_use("clam")

        menubar = tk.Menu(self.app)
        self.create_file_menu(menubar)
        self.create_settings_menu(menubar)
        self.create_help_menu(menubar)
        self.app.config(menu=menubar)

        self.title_label = tk.Label(self.app, text="Téléchargeur de vidéos", bg="#e0e0e0", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=10)

        # Chargement du logo
        logo_path = resource_path("assets/image.png")
        logo = resize_image(logo_path, 150)
        if logo:
            logo_label = tk.Label(self.app, image=logo, bg="#e0e0e0")
            logo_label.image = logo  # Empêche l'image d'être supprimée par le garbage collector
            logo_label.pack(pady=10)

        self.input_frame = tk.Frame(self.app, bg="#e0e0e0", bd=2, relief="groove")
        self.input_frame.pack(pady=10, padx=20, fill=tk.X)
        self.create_input_widgets()

        self.create_buttons()
        self.create_progress_bar()
        self.create_log_history_frames()
        self.create_status_label()

        sys.stdout = TextRedirector(self.log_text)
        self.app.update_idletasks()
        self.app.geometry(f"{self.app.winfo_width()}x{self.app.winfo_height()}")
        self.app.resizable(False, False)
        load_history(self.history_list)
        set_language(self.app, self.title_label, self.url_label, self.output_label, self.browse_button,
                     self.download_button, self.pause_button, self.resume_button, self.convert_label, self.log_label,
                     self.history_label, self.clear_history_button, self.export_history_button, self.filemenu,
                     self.settingsmenu, self.helpmenu, self.current_language)

    def create_file_menu(self, menubar):
        self.filemenu = tk.Menu(menubar, tearoff=0)
        self.filemenu.add_command(label="Quitter", command=self.quit_app)
        menubar.add_cascade(label="Fichier", menu=self.filemenu)

    def create_settings_menu(self, menubar):
        self.settingsmenu = tk.Menu(menubar, tearoff=0)
        self.dark_mode_var = tk.BooleanVar()
        self.settingsmenu.add_checkbutton(label="Mode Sombre", variable=self.dark_mode_var,
                                          command=self.toggle_dark_mode)
        self.settingsmenu.add_command(label="Sauvegarder la file d'attente", command=self.save_queue)
        self.settingsmenu.add_command(label="Charger la file d'attente", command=self.load_queue)
        language_menu = tk.Menu(self.settingsmenu, tearoff=0)
        for lang in LANGUAGES:
            language_menu.add_command(label=lang, command=lambda l=lang: self.change_language(l))
        self.settingsmenu.add_cascade(label="Langue", menu=language_menu)
        menubar.add_cascade(label="Paramètres", menu=self.settingsmenu)

    def create_help_menu(self, menubar):
        self.helpmenu = tk.Menu(menubar, tearoff=0)
        self.helpmenu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=self.helpmenu)

    def create_input_widgets(self):
        self.url_label = tk.Label(self.input_frame, text="URL de la vidéo :", bg="#e0e0e0", font=("Arial", 14))
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.url_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 14))
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)
        self.url_entry_tooltip = tk.Label(self.input_frame, text="Entrez l'URL de la vidéo à télécharger", bg="#e0e0e0",
                                          font=("Arial", 10), fg="grey")
        self.url_entry_tooltip.grid(row=0, column=2, padx=10, pady=5)

        self.output_label = tk.Label(self.input_frame, text="Nom du fichier de sortie :", bg="#e0e0e0",
                                     font=("Arial", 14))
        self.output_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.output_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 14))
        self.output_entry.grid(row=1, column=1, padx=10, pady=5)
        self.output_entry_tooltip = tk.Label(self.input_frame,
                                             text="Entrez le nom du fichier de sortie (par exemple, video.mp4)",
                                             bg="#e0e0e0", font=("Arial", 10), fg="grey")
        self.output_entry_tooltip.grid(row=1, column=2, padx=10, pady=5)

        self.browse_button = tk.Button(self.input_frame, text="Parcourir...", command=self.browse_output, bg="#4CAF50",
                                       fg="white", font=("Arial", 12))
        self.browse_button.grid(row=1, column=3, padx=10, pady=5)

        self.schedule_label = tk.Label(self.input_frame, text="Planifier le téléchargement (AAAA-MM-JJ HH:MM:SS) :",
                                       bg="#e0e0e0", font=("Arial", 14))
        self.schedule_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.schedule_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 14))
        self.schedule_entry.grid(row=2, column=1, padx=10, pady=5)

        self.convert_label = tk.Label(self.input_frame, text="Convertir au format :", bg="#e0e0e0", font=("Arial", 14))
        self.convert_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.convert_var = tk.StringVar()
        self.convert_entry = ttk.Combobox(self.input_frame, textvariable=self.convert_var, values=["mp4", "mp3", "avi"],
                                          font=("Arial", 14))
        self.convert_entry.grid(row=3, column=1, padx=10, pady=5)

    def create_buttons(self):
        button_frame = tk.Frame(self.app, bg="#e0e0e0")
        button_frame.pack(pady=10)

        self.download_button = tk.Button(button_frame, text="Télécharger", command=self.download_video, bg="#4CAF50",
                                         fg="white", font=("Arial", 14, "bold"))
        self.download_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(button_frame, text="Pause", command=self.pause_download, bg="#FFA500", fg="white",
                                      font=("Arial", 14, "bold"))
        self.pause_button.grid(row=0, column=1, padx=5)

        self.resume_button = tk.Button(button_frame, text="Reprendre", command=self.resume_download, bg="#4CAF50",
                                       fg="white", font=("Arial", 14, "bold"))
        self.resume_button.grid(row=0, column=2, padx=5)

    def create_progress_bar(self):
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.app, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10, fill=tk.X, padx=20)

        self.progress_label = tk.Label(self.app, text="Téléchargement : 0%", bg="#e0e0e0", font=("Arial", 12))
        self.progress_label.pack(pady=5)

    def create_log_history_frames(self):
        log_history_frame = tk.Frame(self.app, bg="#e0e0e0", bd=2, relief="groove")
        log_history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        log_frame = tk.Frame(log_history_frame, bg="#e0e0e0")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.log_label = tk.Label(log_frame, text="Logs", bg="#e0e0e0", font=("Arial", 14, "bold"))
        self.log_label.pack(pady=5)

        self.log_text = tk.Text(log_frame, state='disabled', width=70, height=10, font=("Arial", 12), bg="#f0f0f0",
                                fg="#333")
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        history_frame = tk.Frame(log_history_frame, bg="#e0e0e0")
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.history_label = tk.Label(history_frame, text="Historique des Téléchargements", bg="#e0e0e0",
                                      font=("Arial", 14, "bold"))
        self.history_label.pack(pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_history)
        self.search_entry = tk.Entry(history_frame, textvariable=self.search_var, font=("Arial", 12), bg="#f0f0f0")
        self.search_entry.pack(pady=5, padx=10, fill=tk.X)

        self.history_list = tk.Listbox(history_frame, font=("Arial", 12), bg="#f0f0f0", fg="#333")
        self.history_list.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.clear_history_button = tk.Button(history_frame, text="Nettoyer l'historique", command=self.clear_history,
                                              bg="#4CAF50", fg="white", font=("Arial", 12))
        self.clear_history_button.pack(pady=5)

        self.export_history_button = tk.Button(history_frame, text="Exporter l'historique", command=self.export_history,
                                               bg="#4CAF50", fg="white", font=("Arial", 12))
        self.export_history_button.pack(pady=5)

    def create_status_label(self):
        self.status_label = tk.Label(self.app, text="Prêt", bg="#e0e0e0", font=("Arial", 10), anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def download_video(self):
        url = self.url_entry.get()
        output = self.output_entry.get()
        schedule_time = self.schedule_entry.get()
        convert_format = self.convert_var.get()
        error_message = start_download(url, output, schedule_time, convert_format, self.status_label, self.history_list,
                                       self.progress_var, self.progress_label, self.app)
        if error_message:
            messagebox.showerror("Erreur", error_message)

    def pause_download(self):
        pause_download(self.status_label)

    def resume_download(self):
        resume_download(self.status_label, self.convert_var.get(), self.history_list, self.app)

    def search_history(self, *args):
        search_term = self.search_var.get().lower()
        self.history_list.delete(0, tk.END)
        for item in self.history_list.get(0, tk.END):
            if search_term in item.lower():
                self.history_list.insert(tk.END, item)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video files", "*.mp4")])
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, file_path)

    def clear_history(self):
        self.history_list.delete(0, tk.END)
        save_history(self.history_list)

    def export_history(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                for item in self.history_list.get(0, tk.END):
                    f.write("%s\n" % item)
            messagebox.showinfo("Exportation réussie", f"Historique exporté vers {file_path}")

    def show_about(self):
        messagebox.showinfo("À propos", "Téléchargeur de Vidéos v1.0\nDéveloppé par Votre Nom")

    def quit_app(self):
        self.app.quit()

    def toggle_dark_mode(self):
        if self.dark_mode_var.get():
            self.app.configure(bg="#2e2e2e")
            self.set_widgets_color(bg="#2e2e2e", fg="#ffffff", bg_entry="#3e3e3e")
        else:
            self.app.configure(bg="#e0e0e0")
            self.set_widgets_color(bg="#e0e0e0", fg="#000000", bg_entry="#f0f0f0")

    def set_widgets_color(self, bg, fg, bg_entry):
        widgets = [self.app, self.url_label, self.output_label, self.convert_label,
                   self.schedule_label, self.url_entry, self.output_entry,
                   self.url_entry_tooltip, self.output_entry_tooltip, self.log_label,
                   self.history_label, self.search_entry, self.history_list,
                   self.status_label, self.log_text, self.input_frame]  # Correction des références
        for widget in widgets:
            widget.configure(bg=bg, fg=fg)
        self.url_entry.configure(insertbackground=fg)
        self.output_entry.configure(insertbackground=fg)
        self.search_entry.configure(bg=bg_entry, fg=fg, insertbackground=fg)
        self.log_text.configure(bg=bg_entry, fg=fg)
        self.history_list.configure(bg=bg_entry, fg=fg)

    def change_language(self, lang_code):
        self.current_language = lang_code
        set_language(self.app, self.title_label, self.url_label, self.output_label, self.browse_button,
                     self.download_button, self.pause_button, self.resume_button, self.convert_label, self.log_label,
                     self.history_label, self.clear_history_button, self.export_history_button, self.filemenu,
                     self.settingsmenu, self.helpmenu, lang_code)

    def update_labels(self, lang):
        self.title_label.config(text=lang["title"])
        self.url_label.config(text=lang["url_label"])
        self.output_label.config(text=lang["output_label"])
        self.browse_button.config(text=lang["browse_button"])
        self.download_button.config(text=lang["download_button"])
        self.pause_button.config(text=lang["pause_button"])
        self.resume_button.config(text=lang["resume_button"])
        self.convert_label.config(text=lang["convert_label"])
        self.log_label.config(text=lang["logs_label"])
        self.history_label.config(text=lang["history_label"])
        self.clear_history_button.config(text=lang["clear_history_button"])
        self.export_history_button.config(text=lang["export_history_button"])
        self.filemenu.entryconfig(0, label=lang["menu_quit"])
        self.settingsmenu.entryconfig(0, label=lang["menu_dark_mode"])
        self.settingsmenu.entryconfig(1, label=lang["menu_save_queue"])
        self.settingsmenu.entryconfig(2, label=lang["menu_load_queue"])
        self.helpmenu.entryconfig(0, label=lang["menu_about"])

    def save_queue(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            queue_list = list(download_queue.queue)
            with open(file_path, 'w') as f:
                json.dump(queue_list, f)
            messagebox.showinfo("Sauvegarde réussie", f"File d'attente sauvegardée vers {file_path}")

    def load_queue(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                queue_list = json.load(f)
            for item in queue_list:
                download_queue.put(item)
            self.status_label.config(text=f"In queue: {download_queue.qsize()} download(s)")
            messagebox.showinfo("Chargement réussi", f"File d'attente chargée depuis {file_path}")

    def run(self):
        self.app.mainloop()
