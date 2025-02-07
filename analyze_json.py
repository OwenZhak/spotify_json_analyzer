import json
import os


class SpotifyAnalyzer:
    def __init__(self):
        self.track_plays = {}
        self.track_play_time = {}

    def load_json_files(self, file_paths):
        combined_data = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if not data:
                            raise ValueError("Empty JSON file")
                        combined_data.extend(data)
                        print(f"Loaded {len(data)} entries from {file_path}")
                except json.JSONDecodeError:
                    print(f"File is not a valid JSON: {file_path}")
                    return f"Error: File {file_path} is not a valid JSON."
                except ValueError as ve:
                    print(f"File error: {file_path}: {ve}")
                    return f"Error: File {file_path} is empty."
                except Exception as e:
                    print(f"Error loading file {file_path}: {e}")
                    return f"Error: Failed to load file {file_path}: {e}"
            else:
                print(f"File not found: {file_path}")
                return f"Error: File not found {file_path}."
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

    def get_sorted_by_plays(self):
        return sorted(self.track_plays.items(), key=lambda item: item[1], reverse=True)

    def get_sorted_by_minutes(self):
        sorted_data = sorted(self.track_play_time.items(), key=lambda item: item[1], reverse=True)
        return [(track, self.track_plays[track]) for track, _ in sorted_data if track in self.track_plays]
