import json
from helpers import resource_path

LANGUAGES = ["en", "fr"]

def load_language(lang_code):
    with open(resource_path(f"languages/{lang_code}.json"), "r", encoding="utf-8") as file:
        return json.load(file)

def set_language(app, title_label, url_label, output_label, browse_button, download_button, pause_button, resume_button, convert_label, log_label, history_label, clear_history_button, export_history_button, filemenu, settingsmenu, helpmenu, lang_code):
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

def initialize_settings(app):
    set_language(app.app, app.title_label, app.url_label, app.output_label, app.browse_button, app.download_button, app.pause_button, app.resume_button, app.convert_label, app.log_label, app.history_label, app.clear_history_button, app.export_history_button, app.filemenu, app.settingsmenu, app.helpmenu, "fr")
