import tkinter as tk
from tkinter import messagebox
import requests

# ------------------ GAME STATE ------------------ #
current_word = ""
hint_index = 0
current_info = {}

# ------------------ WINDOW SETUP ------------------ #
window = tk.Tk()
window.title("GUESS THAT WORD!!!")
window.geometry("1000x800")
window.resizable(False, False)
window.configure(bg="white")

# ------------------ UI ------------------ #
title_lbl = tk.Label(
    window,
    text="Guess the hidden word:",
    font=("Times New Roman", 25),
    bg="white"
)
title_lbl.pack(pady=10)

entry = tk.Entry(
    window,
    font=("Comic Sans MS", 20),
    width=30,
    bg="lightblue"
)
entry.pack(pady=5)

output_label = tk.Label(
    window,
    text="",
    font=("Comic Sans MS", 16),
    bg="white",
    fg="black",
    wraplength=900,
    justify="left"
)
output_label.pack(pady=10)

hint_label = tk.Label(
    window,
    text="",
    font=("Comic Sans MS", 18),
    bg="white",
    fg="blue"
)
hint_label.pack(pady=5)

clue_label = tk.Label(
    window,
    text="",
    font=("Comic Sans MS", 16),
    bg="white",
    fg="black",
    wraplength=900,
    justify="left"
)
clue_label.pack(pady=10)

# ------------------ FUNCTIONS ------------------ #
def fetch_word_info(word):
    """Get dictionary info safely."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:    
        data = requests.get(url, timeout=5).json()

        if isinstance(data, dict) and data.get("title") == "No Definitions Found":
            return None

        meanings = data[0]["meanings"]
        definition = meanings[0]["definitions"][0].get(
            "definition", "No definition available."
        )   

        synonyms = []
        antonyms = []

        for m in meanings:
            synonyms.extend(m.get("synonyms", []))
            antonyms.extend(m.get("antonyms", []))
            for d in m["definitions"]:
                synonyms.extend(d.get("synonyms", []))
                antonyms.extend(d.get("antonyms", []))

        return {
            "definition": definition,
            "synonyms": list(set(synonyms))[:8],
            "antonyms": list(set(antonyms))[:8]
        }

    except Exception:  
        return None


def load_random_word():
    """Pick a new word and generate clues."""
    global current_word, hint_index, current_info

    hint_index = 0
    hint_label.config(text="")
    output_label.config(text="")
    entry.delete(0, tk.END)

    try:
        current_word = requests.get(   
            "https://random-word-api.herokuapp.com/word",
            timeout=5
        ).json()[0].lower()

        info = fetch_word_info(current_word)
        current_info = info if info else {
            "definition": "No definition available.",
            "synonyms": [],
            "antonyms": []
        }

        syn = current_info["synonyms"][0] if current_info["synonyms"] else "None"
        ant = current_info["antonyms"][0] if current_info["antonyms"] else "None"

        clue_text = (
            f"📝 Definition:\n{current_info['definition']}\n\n"
            f"🟩 Synonym Clue: {syn}\n"
            f"🟥 Antonym Clue: {ant}\n\n"
            f"Hint: Click 'Reveal Hint' to show letters."
        )
        clue_label.config(text=clue_text)

    except Exception as e:
        messagebox.showerror("Error", f"Could not load word: {e}")


def check_guess():
    """Check user's guess."""
    guess = entry.get().strip().lower()

    if not guess:
        messagebox.showwarning("Input Error", "Enter a guess first!")
        return

    if guess == current_word:
        output_label.config(
            text=(
                f"🎉 Correct! The word was: {current_word}\n\n"
                f"📖 Definition: {current_info['definition']}\n\n"
                f"🟩 Synonyms: {', '.join(current_info['synonyms']) or 'None'}\n"
                f"🟥 Antonyms: {', '.join(current_info['antonyms']) or 'None'}"
            )
        )
    else:
        output_label.config(text="❌ Incorrect! Try again!")


def reveal_hint():
    """Reveal letters one at a time."""
    global hint_index

    if not current_word:
        hint_label.config(text="Load a word first!")
        return

    if hint_index >= len(current_word):
        hint_label.config(text="All letters have been revealed!")
        return

    hint_index += 1
    revealed = current_word[:hint_index] + "*" * (len(current_word) - hint_index)
    hint_label.config(text=f"🔍 Hint: {revealed}")

# ------------------ BUTTONS ------------------ #
btn_new = tk.Button(
    window,
    text="New Random Word",
    font=("Times New Roman", 20),
    bg="orange",
    command=load_random_word
)
btn_new.pack(pady=5)

btn_reveal = tk.Button(
    window,
    text="Reveal Hint",
    font=("Times New Roman", 20),
    bg="yellow",
    command=reveal_hint
)
btn_reveal.pack(pady=5)

btn_guess = tk.Button(
    window,
    text="Submit Guess",
    font=("Times New Roman", 20),
    bg="lightgreen",
    command=check_guess
)
btn_guess.pack(pady=5)  

# ------------------ RUN ------------------ #
window.mainloop()
