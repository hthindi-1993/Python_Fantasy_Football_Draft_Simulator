import tkinter as tk
from tkinter import messagebox
import random as rd
import requests
import pygame
import os
from dotenv import load_dotenv

# Initialize pygame mixer
pygame.mixer.init()

# Load environment variables from .env
load_dotenv()

# ---------------------
# CONFIG - LOAD FROM ENV
# ---------------------
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# ---------------------
# VOICE CLIP GENERATOR (MP3)
# ---------------------
def generate_voice_clip(text, voice_id, api_key, filename):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?output_format=mp3_44100_128"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.75
        },
        "text_type": "ssml"
    }

    response = requests.post(url, json=data, headers=headers, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    else:
        print("Error generating audio:", response.text)
        return False

import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


def play_audio(file_path):
    if os.path.exists(file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except pygame.error as e:
            print(f"Audio playback failed: {e}")

# ---------------------
# INTRO ANNOUNCEMENTS
# ---------------------
def play_intro_announcement():
    path = "audio/announcement.mp3"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        intro_message = (
            f"<speak>Welcome to your Fantasy Football League Draft Order. "
            "Let's get started.</speak>"
        )
        generate_voice_clip(intro_message, VOICE_ID, ELEVEN_API_KEY, path)
    play_audio(path)

# ---------------------
# DRAFT LOGIC
# ---------------------
def draft_order(teams_list):
    order = {}
    inner_func_teams_list = teams_list.copy()
    for index in range(len(teams_list)):
        selected_team = rd.choice(inner_func_teams_list)
        order[str(len(teams_list) - index)] = selected_team
        inner_func_teams_list.remove(selected_team)
    return order

spoken_ordinals = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th",
    5: "5th", 6: "6th", 7: "7th", 8: "8th",
    9: "9th", 10: "10th", 11: "11th", 12: "12th"
}

# ---------------------
# ANIMATED REVEAL
# ---------------------
def animated_reveal(order_dict, delay_seconds):
    sorted_picks = sorted(order_dict.items(), key=lambda x: int(x[0]), reverse=True)
    output_window = tk.Toplevel()
    output_window.title("Draft Order Reveal 🎉")
    output_window.state("zoomed")

    reveal_text = tk.Text(output_window, font=("Consolas", 14), bg="black", fg="lime", wrap="word")
    reveal_text.pack(expand=True, fill="both", padx=20, pady=20)
    reveal_text.insert("end", "🎲 Welcome to the Fantasy Draft Reveal!\n\n")
    reveal_text.config(state="disabled")

    countdown_label = tk.Label(output_window, font=("Impact", 72), fg="red", bg="black")
    countdown_label.pack(pady=20)

    def reveal_next(index):
        if index >= len(sorted_picks):
            reveal_text.config(state="normal")
            reveal_text.insert("end", "\n✅ Draft Order Complete!\n")
            reveal_text.config(state="disabled")
            countdown_label.config(text="")
            return

        pick_num, team = sorted_picks[index]
        pick_int = int(pick_num)
        spoken_pick = spoken_ordinals.get(pick_int, f"{pick_int}th")
        message = f"""<speak>With the {spoken_pick} pick of the draft, the pick goes to <break time=\"1s\"/>{team}.</speak>"""
        text = f"{spoken_pick}:\t{team}\n\n"

        reveal_text.config(state="normal")
        reveal_text.insert("end", text)
        reveal_text.see("end")
        reveal_text.config(state="disabled")

        filename = f"audio/audio_pick_{pick_num}.mp3"
        if not os.path.exists(filename):
            generate_voice_clip(message, VOICE_ID, ELEVEN_API_KEY, filename)

        play_audio("audio/intro/intro.mp3")  # 🔔 Play intro before each pick
        play_audio(filename)

        def animate_countdown(n):
            if n > 0:
                countdown_label.config(text=str(n), fg="red")
                countdown_label.after(500, lambda: countdown_label.config(fg="orange"))
                countdown_label.after(1000, lambda: animate_countdown(n - 1))
            else:
                countdown_label.config(text="")
                output_window.after(500, lambda: reveal_next(index + 1))

        animate_countdown(int(delay_seconds))

    reveal_next(0)

# ---------------------
# GUI APP
# ---------------------
def ask_for_league_member_names_gui():
    prefilled_names = [
        "Team Alpha", "Team Bravo", "Team Charlie", "Team Delta",
        "Team Echo", "Team Foxtrot", "Team Golf", "Team Hotel",
        "Team India", "Team Juliet", "Team Kilo", "Team Lima"
    ]

    def delete_audio_files():
        folder = "audio"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) and filename.endswith(('.mp3', '.wav')) and "intro" not in filename:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    def submit_names():
        team_members_list = [entry.get().strip() for entry in entry_fields if entry.get().strip()]
        if len(team_members_list) != len(entry_fields):
            messagebox.showwarning("Incomplete", "Please fill out all team member names.")
            return

        try:
            delay = float(delay_entry.get())
            if delay <= 0:
                raise ValueError
        except ValueError:
            delay = 1.5
            messagebox.showinfo("Delay Info", "Invalid delay entered. Using default of 1.5 seconds.")

        delete_audio_files()
        play_intro_announcement()
        result = draft_order(team_members_list)
        animated_reveal(result, delay)

    root = tk.Tk()
    root.title("Fantasy Draft Order Generator")
    root.geometry("900x750")
    root.columnconfigure(0, weight=1)

    main_frame = tk.Frame(root)
    main_frame.grid(sticky="nsew", padx=40, pady=40)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    entry_fields = []
    for i in range(12):
        col = 0 if i < 6 else 1
        row = i if i < 6 else i - 6
        label = tk.Label(main_frame, text=f"Team Member {i+1}:", font=("Arial", 12))
        label.grid(row=row, column=col*2, sticky="e", padx=(0, 10), pady=10)
        entry = tk.Entry(main_frame, font=("Arial", 12), width=25)
        entry.grid(row=row, column=col*2 + 1, sticky="w", pady=10)
        if i < len(prefilled_names):
            entry.insert(0, prefilled_names[i])
        entry_fields.append(entry)

    delay_label = tk.Label(root, text="Delay Between Picks (seconds):", font=("Arial", 12))
    delay_label.grid(row=8, column=0, pady=(10, 5))
    delay_entry = tk.Entry(root, font=("Arial", 12), justify="center", width=10)
    delay_entry.insert(0, "1.5")
    delay_entry.grid(row=9, column=0, pady=(0, 20))

    submit_button = tk.Button(
        root, text="Submit & Reveal Draft Order", command=submit_names,
        font=("Arial", 14), bg="#4CAF50", fg="white", padx=20, pady=10
    )
    submit_button.grid(row=10, column=0, pady=10)

    root.mainloop()

# ---------------------
# Run it!
# ---------------------
ask_for_league_member_names_gui()