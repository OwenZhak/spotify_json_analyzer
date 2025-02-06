import json
import os
import ctypes  # DPI awareness
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Frame, Button, Label


class SpotifyAnalyzer:
    def __init__(self, root):
        self.root = root
        self.track_plays = {}
        self.track_play_time = {}

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Spotify Streaming History Analyzer")
        self.root.geometry("1400x720")  # Increased width
        self.root.configure(bg="#121212")  # Dark background

        # Create frames for layout
        left_frame = Frame(self.root, bg="#1e1e1e", width=300)  # Darker left frame
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = Frame(self.root, bg="#1e1e1e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create buttons in the left frame
        button_width = 20  # Set a fixed width for all buttons
        button_height = 2  # Set a fixed height for all buttons

        # Set darker shades for buttons
        select_button = Button(left_frame, text="Select JSON Files", command=self.select_files, font=("Arial", 14),
                               bg="#c0392b", fg="white", width=button_width, height=button_height)
        select_button.pack(pady=10)

        sort_plays_button = Button(left_frame, text="Sort by Plays", command=self.sort_by_plays, font=("Arial", 14),
                                   bg="#2980b9", fg="white", width=button_width, height=button_height)
        sort_plays_button.pack(pady=10)

        sort_minutes_button = Button(left_frame, text="Sort by Minutes", command=self.sort_by_minutes, font=("Arial", 14),
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
        self.result_text = Text(result_frame, wrap=tk.WORD, font=("Arial", 12), bg="#2e2e2e", fg="white",
                                insertbackground='white')
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Create a scrollbar for the Text widget
        scrollbar = Scrollbar(result_frame, command=self.result_text.yview, bg="black")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def select_files(self):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Analyzing your files, please wait...\n")
        self.root.update_idletasks()

        # Open file dialog to select JSON files
        file_paths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        if not file_paths:
            messagebox.showinfo("Info", "No files selected.")
            return

        combined_data = self.load_json_files(file_paths)
        if not combined_data:
            return

        self.process_data(combined_data)
        self.display_result(sorted(self.track_plays.items(), key=lambda item: item[1], reverse=True))

    def load_json_files(self, file_paths):
        combined_data = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        combined_data.extend(data)
                        print(f"Loaded {len(data)} entries from {file_path}")
                except Exception as e:
                    print(f"Error loading file {file_path}: {e}")
                    messagebox.showerror("Error", f"Error loading file {file_path}: {e}")
                    return None
            else:
                print(f"File not found: {file_path}")
                messagebox.showerror("Error", "File not found!")
                return None
        return combined_data

    def process_data(self, combined_data):
        self.track_plays.clear()
        self.track_play_time.clear()

        for entry in combined_data:
            if entry.get("ms_played", 0) >= 20000:
                track_name = entry.get("master_metadata_track_name")
                artist_name = entry.get("master_metadata_album_artist_name")

                if track_name and artist_name:
                    key = f"{artist_name} - {track_name}"
                    self.track_plays[key] = self.track_plays.get(key, 0) + 1
                    self.track_play_time[key] = self.track_play_time.get(key, 0) + entry.get("ms_played", 0)

    def display_result(self, sorted_data):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Sorted Track Plays:\n")
        for index, (key, value) in enumerate(sorted_data, start=1):
            play_count = value
            total_play_time_ms = self.track_play_time[key]
            total_play_time_minutes = total_play_time_ms / 60000
            self.result_text.insert(tk.END, f"{index}. {key}: {play_count} plays, {total_play_time_minutes:.2f} minutes\n")

    def sort_by_plays(self):
        sorted_data = sorted(self.track_plays.items(), key=lambda item: item[1], reverse=True)
        self.display_result(sorted_data)

    def sort_by_minutes(self):
        sorted_data = sorted(self.track_play_time.items(), key=lambda item: item[1], reverse=True)
        sorted_tracks = [(track, self.track_plays[track]) for track, _ in sorted_data if track in self.track_plays]
        self.display_result(sorted_tracks)


if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    root = tk.Tk()
    app = SpotifyAnalyzer(root)
    root.mainloop()
