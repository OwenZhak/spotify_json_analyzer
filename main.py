import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Frame, Button, Label, OptionMenu, StringVar
from analyze_json import SpotifyAnalyzer


class SpotifyAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.analyzer = SpotifyAnalyzer()
        self.selected_year = StringVar(root)
        self.selected_year.set("All Time")  # Default value
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Spotify Streaming History Analyzer")
        self.root.geometry("1400x720")
        self.root.configure(bg="#121212")

        left_frame = Frame(self.root, bg="#1e1e1e", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = Frame(self.root, bg="#1e1e1e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        button_width = 20
        button_height = 2

        select_button = Button(left_frame, text="Select JSON Files", command=self.select_files, font=("Arial", 14),
                               bg="#c0392b", fg="white", width=button_width, height=button_height)
        select_button.pack(pady=10)

        # Year selection dropdown
        self.year_label = Label(left_frame, text="Select Year:", font=("Arial", 12), bg="#1e1e1e", fg="white")
        self.year_label.pack(pady=5)

        self.year_dropdown = OptionMenu(left_frame, self.selected_year, "All Time")  # Initial value, updated later
        self.year_dropdown.config(font=("Arial", 12), bg="#34495e", fg="white", width=15)
        self.year_dropdown.pack(pady=5)

        sort_plays_button = Button(left_frame, text="Sort by Plays", command=self.sort_by_plays, font=("Arial", 14),
                                   bg="#2980b9", fg="white", width=button_width, height=button_height)
        sort_plays_button.pack(pady=10)

        sort_minutes_button = Button(left_frame, text="Sort by Minutes", command=self.sort_by_minutes, font=("Arial", 14),
                                     bg="#27ae60", fg="white", width=button_width, height=button_height)
        sort_minutes_button.pack(pady=10)

        instruction_label = Label(left_frame, text="Instructions:", font=("Arial", 12), bg="#1e1e1e", fg="white")
        instruction_label.pack(pady=10)

        instructions = Label(left_frame, text="1. Select your Spotify JSON files.\n2. Choose how to sort the results.",
                             font=("Arial", 12), bg="#1e1e1e", fg="white")
        instructions.pack(pady=10)

        result_frame = Frame(right_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
        result_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        result_label = Label(result_frame, text="Results:", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
        result_label.pack(pady=10)

        self.result_text = Text(result_frame, wrap=tk.WORD, font=("Arial", 12), bg="#2e2e2e", fg="white",
                                insertbackground='white')
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        scrollbar = Scrollbar(result_frame, command=self.result_text.yview, bg="black")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def select_files(self):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Analyzing your files, please wait...\n")
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

        self.analyzer.process_data(combined_data)

        # Update year dropdown options
        years = ["All Time"] + self.analyzer.track_years
        menu = self.year_dropdown["menu"]
        menu.delete(0, "end")
        for year in years:
            menu.add_command(label=year, command=lambda value=year: self.selected_year.set(value))

        self.sort_by_plays()  # Display initial result

    def display_result(self, sorted_data):
        self.result_text.delete(1.0, tk.END)
        selected_year = self.selected_year.get()
        self.result_text.insert(tk.END, f"Sorted Track Plays ({selected_year}):\n")
        for index, (key, value) in enumerate(sorted_data, start=1):
            play_count = value
            year = int(selected_year) if selected_year != "All Time" else None

            if year is not None and year in self.analyzer.track_play_time and key in self.analyzer.track_play_time[year]:
                total_play_time_ms = self.analyzer.track_play_time[year][key]
                total_play_time_minutes = total_play_time_ms / 60000
                self.result_text.insert(tk.END,
                                         f"{index}. {key}: {play_count} plays, {total_play_time_minutes:.2f} minutes\n")
            elif year is None:  # "All Time" case
                # Aggregate play time across all years
                total_play_time_ms = 0
                for year_data in self.analyzer.track_play_time.values():
                    if key in year_data:
                        total_play_time_ms += year_data[key]

                if total_play_time_ms > 0:
                    total_play_time_minutes = total_play_time_ms / 60000
                    self.result_text.insert(tk.END,
                                             f"{index}. {key}: {play_count} plays, {total_play_time_minutes:.2f} minutes\n")
                else:
                    self.result_text.insert(tk.END, f"{index}. {key}: {play_count} plays, Play time not available\n")
            else:
                self.result_text.insert(tk.END, f"{index}. {key}: {play_count} plays, Play time not available\n")

    def sort_by_plays(self):
        selected_year = self.selected_year.get()
        year = int(selected_year) if selected_year != "All Time" else None
        sorted_data = self.analyzer.get_sorted_by_plays(year)
        self.display_result(sorted_data)

    def sort_by_minutes(self):
        selected_year = self.selected_year.get()
        year = int(selected_year) if selected_year != "All Time" else None
        sorted_data = self.analyzer.get_sorted_by_minutes(year)
        self.display_result(sorted_data)


if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    root = tk.Tk()
    app = SpotifyAnalyzerUI(root)
    root.mainloop()
