import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Frame, Button, Label, OptionMenu, StringVar
from analyze_json import SpotifyAnalyzer

class SpotifyAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.analyzer = SpotifyAnalyzer()
        self.selected_year = StringVar(root)
        self.selected_year.set("All Time")
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Spotify Streaming History Analyzer")
        self.root.geometry("1800x720")  # Wider to accommodate both frames
        self.root.configure(bg="#121212")

        # Control Frame (Left)
        left_frame = Frame(self.root, bg="#1e1e1e", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Center Frame for Tracks
        tracks_frame = Frame(self.root, bg="#1e1e1e")
        tracks_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Frame for Artists
        artists_frame = Frame(self.root, bg="#1e1e1e")
        artists_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        button_width = 20
        button_height = 2

        # Left frame controls
        select_button = Button(left_frame, text="Select JSON Files", command=self.select_files, font=("Arial", 14),
                               bg="#c0392b", fg="white", width=button_width, height=button_height)
        select_button.pack(pady=10)

        self.year_label = Label(left_frame, text="Select Year:", font=("Arial", 12), bg="#1e1e1e", fg="white")
        self.year_label.pack(pady=5)

        self.year_dropdown = OptionMenu(left_frame, self.selected_year, "All Time")
        self.year_dropdown.config(font=("Arial", 12), bg="#34495e", fg="white", width=15)
        self.year_dropdown.pack(pady=5)

        # Sorting buttons (now affect both tracks and artists)
        sort_label = Label(left_frame, text="Sort By:", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="white")
        sort_label.pack(pady=10)

        sort_plays_button = Button(left_frame, text="Play Count", command=self.sort_by_plays, font=("Arial", 14),
                                  bg="#2980b9", fg="white", width=button_width, height=button_height)
        sort_plays_button.pack(pady=10)

        sort_minutes_button = Button(left_frame, text="Total Minutes", command=self.sort_by_minutes,
                                    font=("Arial", 14), bg="#27ae60", fg="white", width=button_width, height=button_height)
        sort_minutes_button.pack(pady=10)

        instruction_label = Label(left_frame, text="Instructions:", font=("Arial", 12), bg="#1e1e1e", fg="white")
        instruction_label.pack(pady=10)

        instructions = Label(left_frame,
                             text="1. Select your Spotify JSON files.\n2. Choose a year filter.\n3. Sort by plays or minutes.",
                             font=("Arial", 12), bg="#1e1e1e", fg="white", justify=tk.LEFT)
        instructions.pack(pady=10)

        # Tracks Display Frame
        tracks_display_frame = Frame(tracks_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
        tracks_display_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tracks_title = Label(tracks_display_frame, text="Tracks:", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
        tracks_title.pack(pady=10)

        self.tracks_text = Text(tracks_display_frame, wrap=tk.WORD, font=("Arial", 12), bg="#2e2e2e", fg="white",
                               insertbackground='white')
        self.tracks_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tracks_scrollbar = Scrollbar(tracks_display_frame, command=self.tracks_text.yview, bg="black")
        tracks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tracks_text.config(yscrollcommand=tracks_scrollbar.set)

        # Artists Display Frame
        artists_display_frame = Frame(artists_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
        artists_display_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        artists_title = Label(artists_display_frame, text="Artists:", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
        artists_title.pack(pady=10)

        self.artists_text = Text(artists_display_frame, wrap=tk.WORD, font=("Arial", 12), bg="#2e2e2e", fg="white",
                                insertbackground='white')
        self.artists_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        artists_scrollbar = Scrollbar(artists_display_frame, command=self.artists_text.yview, bg="black")
        artists_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.artists_text.config(yscrollcommand=artists_scrollbar.set)

    def select_files(self):
        self.tracks_text.delete(1.0, tk.END)
        self.artists_text.delete(1.0, tk.END)
        self.tracks_text.insert(tk.END, "Analyzing your files, please wait...\n")
        self.root.update_idletasks()

        file_paths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        if not file_paths:
            messagebox.showinfo("Info", "No files selected.")
            return

        combined_data = self.analyzer.load_json_files(file_paths)
        if isinstance(combined_data, str) and combined_data.startswith("Error:"):
            messagebox.showerror("Error", combined_data)
            return
        elif not combined_data:
            messagebox.showerror("Error", "No data to process.")
            return

        # Process the loaded data
        self.analyzer.process_data(combined_data)

        # Update the dropdown based on the years found in the data
        years = ["All Time"] + self.analyzer.track_years
        menu = self.year_dropdown["menu"]
        menu.delete(0, "end")
        for y in years:
            menu.add_command(label=y, command=lambda year_val=y: self.selected_year.set(year_val))

        # Default display using play counts
        self.sort_by_plays()

    def display_tracks(self, sorted_data, sort_type="plays"):
        """
        Display track statistics in the tracks text widget
        """
        self.tracks_text.delete(1.0, tk.END)
        chosen_year = self.selected_year.get()
        self.tracks_text.insert(tk.END, f"Tracks - Sorted by {sort_type.title()} ({chosen_year}):\n\n")

        # Convert "All Time" to None for easier lookups
        the_year = None if chosen_year == "All Time" else int(chosen_year)

        for index, (track_key, play_count) in enumerate(sorted_data, start=1):
            total_ms = 0

            if the_year is not None:
                # Lookup based on the exact year
                if the_year in self.analyzer.track_play_time:
                    total_ms = self.analyzer.track_play_time[the_year].get(track_key, 0)
            else:
                # Sum across all years for "All Time"
                for y_data in self.analyzer.track_play_time.values():
                    total_ms += y_data.get(track_key, 0)

            if total_ms > 0:
                total_minutes = total_ms / 60000
                self.tracks_text.insert(tk.END,
                    f"{index}. {track_key}: {play_count} plays, {total_minutes:.2f} minutes\n"
                )
            else:
                print(f"Debug: Track {track_key} not found in track_play_time")
                self.tracks_text.insert(tk.END,
                    f"{index}. {track_key}: {play_count} plays, Play time not available\n"
                )

    def display_artists(self, sorted_data, sort_type="plays"):
        """
        Display artist statistics in the artists text widget
        """
        self.artists_text.delete(1.0, tk.END)
        chosen_year = self.selected_year.get()
        self.artists_text.insert(tk.END, f"Artists - Sorted by {sort_type.title()} ({chosen_year}):\n\n")

        # Convert "All Time" to None for easier lookups
        the_year = None if chosen_year == "All Time" else int(chosen_year)

        for index, (artist_name, play_count) in enumerate(sorted_data, start=1):
            total_ms = 0

            if the_year is not None:
                # Lookup based on the exact year
                if the_year in self.analyzer.artist_play_time:
                    total_ms = self.analyzer.artist_play_time[the_year].get(artist_name, 0)
            else:
                # Sum across all years for "All Time"
                for y_data in self.analyzer.artist_play_time.values():
                    total_ms += y_data.get(artist_name, 0)

            if total_ms > 0:
                total_minutes = total_ms / 60000
                self.artists_text.insert(tk.END,
                    f"{index}. {artist_name}: {play_count} plays, {total_minutes:.2f} minutes\n"
                )
            else:
                print(f"Debug: Artist {artist_name} not found in artist_play_time")
                self.artists_text.insert(tk.END,
                    f"{index}. {artist_name}: {play_count} plays, Play time not available\n"
                )

    def sort_by_plays(self):
        """
        Sort both tracks and artists by play count
        """
        chosen_year = self.selected_year.get()
        year_val = None if chosen_year == "All Time" else int(chosen_year)
        
        # Get sorted data and display for tracks
        tracks_data = self.analyzer.get_sorted_by_plays(year_val)
        self.display_tracks(tracks_data, "plays")
        
        # Get sorted data and display for artists
        artists_data = self.analyzer.get_artists_sorted_by_plays(year_val)
        self.display_artists(artists_data, "plays")

    def sort_by_minutes(self):
        """
        Sort both tracks and artists by total minutes played
        """
        chosen_year = self.selected_year.get()
        year_val = None if chosen_year == "All Time" else int(chosen_year)
        
        # Get sorted data and display for tracks
        tracks_data = self.analyzer.get_sorted_by_minutes(year_val)
        self.display_tracks(tracks_data, "minutes")
        
        # Get sorted data and display for artists
        artists_data = self.analyzer.get_artists_sorted_by_minutes(year_val)
        self.display_artists(artists_data, "minutes")

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    root = tk.Tk()
    app = SpotifyAnalyzerUI(root)
    root.mainloop()
