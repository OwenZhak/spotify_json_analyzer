import json
import os
import ctypes  # DPI awareness
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Frame, Button, Label

# Set DPI awareness
ctypes.windll.shcore.SetProcessDpiAwareness(True)


def select_files():
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Analyzing your files, please wait...\n")
    root.update_idletasks()

    # Open file dialog to select JSON files
    file_paths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if not file_paths:
        messagebox.showinfo("Info", "No files selected.")
        return

    combined_data = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                combined_data.extend(data)
                print(f"Loaded {len(data)} entries from {file_path}")
        else:
            print(f"File not found: {file_path}")
            messagebox.showerror("Error", "File not found!")
            return

    global track_plays, track_play_time  # Declare as global
    track_plays = {}
    track_play_time = {}

    for entry in combined_data:
        if entry["ms_played"] >= 20000:
            track_name = entry["master_metadata_track_name"]
            artist_name = entry["master_metadata_album_artist_name"]

            # Create a valid key and ensure it's not None
            if track_name and artist_name:
                key = f"{artist_name} - {track_name}"

                if key in track_plays:
                    track_plays[key] += 1
                    track_play_time[key] += entry["ms_played"]
                else:
                    track_plays[key] = 1
                    track_play_time[key] = entry["ms_played"]

    # Display default sorting (by plays)
    display_result(sorted(track_plays.items(), key=lambda item: item[1], reverse=True))


def display_result(sorted_data):
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Sorted Track Plays:\n")
    for index, (key, value) in enumerate(sorted_data, start=1):
        play_count = value
        total_play_time_ms = track_play_time[key]
        total_play_time_minutes = total_play_time_ms / 60000
        result_text.insert(tk.END, f"{index}. {key}: {play_count} plays, {total_play_time_minutes:.2f} minutes\n")


def sort_by_plays():
    sorted_data = sorted(track_plays.items(), key=lambda item: item[1], reverse=True)
    display_result(sorted_data)


def sort_by_minutes():
    sorted_data = sorted(track_play_time.items(), key=lambda item: item[1], reverse=True)

    # Create a list of tracks and their plays based on the sorted minutes
    sorted_tracks = [(track, track_plays[track]) for track, _ in sorted_data if track in track_plays]
    display_result(sorted_tracks)


def clear_results():
    result_text.delete(1.0, tk.END)


# Create the main application window
root = tk.Tk()
root.title("Spotify Streaming History Analyzer")
root.geometry("1400x720")  # Increased width
root.configure(bg="#121212")  # Dark background

# Create frames for layout
left_frame = Frame(root, bg="#1e1e1e", width=300)  # Darker left frame
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = Frame(root, bg="#1e1e1e")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create buttons in the left frame
button_width = 20  # Set a fixed width for all buttons
button_height = 2  # Set a fixed height for all buttons

# Set darker shades for buttons
select_button = Button(left_frame, text="Select JSON Files", command=select_files, font=("Arial", 14), bg="#c0392b",
                       fg="white", width=button_width, height=button_height)
select_button.pack(pady=10)

sort_plays_button = Button(left_frame, text="Sort by Plays", command=sort_by_plays, font=("Arial", 14), bg="#2980b9",
                           fg="white", width=button_width, height=button_height)
sort_plays_button.pack(pady=10)

sort_minutes_button = Button(left_frame, text="Sort by Minutes", command=sort_by_minutes, font=("Arial", 14),
                             bg="#27ae60", fg="white", width=button_width, height=button_height)
sort_minutes_button.pack(pady=10)

# Create a label for instructions
instruction_label = Label(left_frame, text="Instructions:", font=("Arial", 12), bg="#1e1e1e", fg="white")
instruction_label.pack(pady=10)

# Displayed Instructions
instructions = Label(left_frame, text="1. Select your Spotify JSON files.\n2. Choose how to sort the results.",
                     font=("Arial", 12), bg="#1e1e1e", fg="white")
instructions.pack(pady=10)

# Create a frame for the result text widget
result_frame = Frame(right_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
result_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

result_label = Label(result_frame, text="Results:", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
result_label.pack(pady=10)

# Create a Text widget
result_text = Text(result_frame, wrap=tk.WORD, font=("Arial", 12), bg="#2e2e2e", fg="white", insertbackground='white')
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

# Create a scrollbar for the Text widget
scrollbar = Scrollbar(result_frame, command=result_text.yview, bg="black")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

# Run the application
root.mainloop()
