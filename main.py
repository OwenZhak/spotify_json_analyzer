import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Frame, Button, Label, OptionMenu, StringVar, ttk
from analyze_json import SpotifyAnalyzer

class SpotifyAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.analyzer = SpotifyAnalyzer()
        self.selected_year = StringVar(root)
        self.selected_year.set("All Time")
        # Add variable to track current sort method
        self.current_sort = "plays"  # Default sort is by plays
        # Add a trace to the selected_year variable
        self.selected_year.trace("w", self.year_changed)
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Spotify Streaming History Analyzer")
        self.root.geometry("1200x720")
        self.root.configure(bg="#121212")

        # Define colors
        DARK_GREEN = "#1DB954"  # Spotify green
        DARK_PINK = "#FF69B4"   # Hot pink
        BG_COLOR = "#121212"    # Dark background
        TEXT_COLOR = "white"
        TEXT_BG = "#2e2e2e"

        # Create a top frame for buttons
        top_frame = Frame(self.root, bg=BG_COLOR)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Add buttons to top frame with specified colors
        select_button = Button(top_frame, text="Select JSON Files", command=self.select_files, font=("Arial", 12),
                              bg=DARK_GREEN, fg=TEXT_COLOR, padx=10, pady=5)
        select_button.pack(side=tk.LEFT, padx=5)

        # Year selection
        year_label = Label(top_frame, text="Year:", font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        year_label.pack(side=tk.LEFT, padx=5)

        self.year_dropdown = OptionMenu(top_frame, self.selected_year, "All Time")
        self.year_dropdown.config(font=("Arial", 12), bg=DARK_GREEN, fg=TEXT_COLOR)
        self.year_dropdown.pack(side=tk.LEFT, padx=5)

        # Sort buttons
        sort_label = Label(top_frame, text="Sort By:", font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        sort_label.pack(side=tk.LEFT, padx=10)

        sort_plays_button = Button(top_frame, text="Play Count", command=self.sort_by_plays, font=("Arial", 12),
                                  bg=DARK_PINK, fg=TEXT_COLOR, padx=10, pady=5)
        sort_plays_button.pack(side=tk.LEFT, padx=5)

        sort_minutes_button = Button(top_frame, text="Total Minutes", command=self.sort_by_minutes,
                                    font=("Arial", 12), bg=DARK_PINK, fg=TEXT_COLOR, padx=10, pady=5)
        sort_minutes_button.pack(side=tk.LEFT, padx=5)

        # Create tab control with custom styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_COLOR, foreground=TEXT_COLOR, padding=[10, 5], font=('Arial', 12))
        style.map("TNotebook.Tab", 
                background=[("selected", DARK_GREEN), ("active", DARK_PINK)],
                foreground=[("selected", TEXT_COLOR), ("active", TEXT_COLOR)])
        
        self.tab_control = ttk.Notebook(self.root)
        
        # Create Tracks tab
        tracks_tab = Frame(self.tab_control, bg=BG_COLOR)
        self.tab_control.add(tracks_tab, text='Tracks')
        
        # Create Artists tab
        artists_tab = Frame(self.tab_control, bg=BG_COLOR)
        self.tab_control.add(artists_tab, text='Artists')
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Tracks content
        tracks_frame = Frame(tracks_tab, bg=BG_COLOR)
        tracks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tracks_text = Text(tracks_frame, wrap=tk.WORD, font=("Arial", 12), bg=TEXT_BG, fg=TEXT_COLOR,
                               insertbackground='white')
        self.tracks_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tracks_scrollbar = Scrollbar(tracks_frame, command=self.tracks_text.yview)
        tracks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tracks_text.config(yscrollcommand=tracks_scrollbar.set)
        
        # Artists content
        artists_frame = Frame(artists_tab, bg=BG_COLOR)
        artists_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.artists_text = Text(artists_frame, wrap=tk.WORD, font=("Arial", 12), bg=TEXT_BG, fg=TEXT_COLOR,
                                insertbackground='white')
        self.artists_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        artists_scrollbar = Scrollbar(artists_frame, command=self.artists_text.yview)
        artists_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.artists_text.config(yscrollcommand=artists_scrollbar.set)
        
        # Default welcome message
        welcome_message = "Welcome to Spotify Streaming History Analyzer!\n\n"
        welcome_message += "1. Click 'Select JSON Files' to load your Spotify data\n"
        welcome_message += "2. Choose a year filter from the dropdown\n"
        welcome_message += "3. Sort by Play Count or Total Minutes\n"
        welcome_message += "4. Switch between Tracks and Artists tabs to view results"
        
        self.tracks_text.insert(tk.END, welcome_message)
        self.artists_text.insert(tk.END, welcome_message)

    def select_files(self):
        self.tracks_text.delete(1.0, tk.END)
        self.artists_text.delete(1.0, tk.END)
        self.tracks_text.insert(tk.END, "Analyzing your files, please wait...\n")
        self.artists_text.insert(tk.END, "Analyzing your files, please wait...\n")
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
        self.current_sort = "plays"  # Update current sort method
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
        self.current_sort = "minutes"  # Update current sort method
        chosen_year = self.selected_year.get()
        year_val = None if chosen_year == "All Time" else int(chosen_year)
        
        # Get sorted data and display for tracks
        tracks_data = self.analyzer.get_sorted_by_minutes(year_val)
        self.display_tracks(tracks_data, "minutes")
        
        # Get sorted data and display for artists
        artists_data = self.analyzer.get_artists_sorted_by_minutes(year_val)
        self.display_artists(artists_data, "minutes")
    
    def year_changed(self, *args):
        """
        Called when the year selection changes, re-applies the current sort
        """
        # Skip if no data is loaded yet
        if not hasattr(self.analyzer, 'track_years') or not self.analyzer.track_years:
            return
            
        # Apply the current sort method
        if self.current_sort == "plays":
            self.sort_by_plays()
        else:
            self.sort_by_minutes()

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    root = tk.Tk()
    app = SpotifyAnalyzerUI(root)
    root.mainloop()