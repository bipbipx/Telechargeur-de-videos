# Téléchargeur de Vidéos

![Logo](assets/image.png)

## Description
Cette application permet de télécharger des vidéos depuis une URL spécifiée et de les enregistrer sous un nom de fichier spécifié.

## Fonctionnalités
- **Téléchargement de vidéos** : Téléchargez des vidéos à partir de n'importe quelle URL supportée.
- **Interface utilisateur conviviale** : Une interface simple et intuitive.
- **Barre de progression** : Suivez l'état de votre téléchargement en temps réel.
- **Logs en direct** : Affichage des logs de téléchargement pour un suivi détaillé.

## Prérequis
- Python 3.x
- `yt-dlp`
- `Pillow`

## Installation
1. **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-repo/video-downloader.git
    cd video-downloader
    ```
2. **Installer les dépendances** :
    ```bash
    pip install yt-dlp pillow
    ```

## Utilisation
1. **Ouvrir l'application** :
    ```bash
    python main.py
    ```
2. **Entrer l'URL de la vidéo** que vous souhaitez télécharger.
3. **Entrer le nom du fichier de sortie** (par exemple, `video.mp4`).
4. **Choisir l'emplacement** où enregistrer le fichier en cliquant sur le bouton `Parcourir...`.
5. **Cliquer sur le bouton `Télécharger`** pour commencer le téléchargement.

![Screenshot](screenshot.png)

## Compilation en .exe
Pour compiler cette application en un fichier exécutable (.exe) sur Windows, utilisez PyInstaller :
1. **Installer PyInstaller** :
    ```bash
    pip install pyinstaller
    ```
2. **Compiler l'application** :
    ```bash
    pyinstaller --onefile --windowed --add-data "image.png;." main.py
    ```
3. **Exécutable généré** :
   L'exécutable sera généré dans le répertoire `dist`.

## Auteur
Bipbipx

## Date
07/07/2024


