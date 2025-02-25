import json
import os
from datetime import datetime


class SpotifyAnalyzer:
    def __init__(self):
        self.track_plays = {}  # {year: {track: plays}}
        self.track_play_time = {}  # {year: {track: play_time}}
        self.track_years = set()  # To store the years present in the data

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
        self.track_years.clear()

        for entry in combined_data:
            if entry.get("ms_played", 0) >= 20000:
                track_name = entry.get("master_metadata_track_name")
                artist_name = entry.get("master_metadata_album_artist_name")
                timestamp = entry.get("ts")  # Timestamp of when the track was played

                if track_name and artist_name and timestamp:
                    key = f"{artist_name} - {track_name}"
                    try:
                        year = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).year
                        self.track_years.add(year)

                        # Update track_plays
                        if year not in self.track_plays:
                            self.track_plays[year] = {}
                        self.track_plays[year][key] = self.track_plays[year].get(key, 0) + 1

                        # Update track_play_time
                        if year not in self.track_play_time:
                            self.track_play_time[year] = {}
                        self.track_play_time[year][key] = self.track_play_time[year].get(key, 0) + entry.get("ms_played", 0)

                    except ValueError:
                        print(f"Invalid timestamp format: {timestamp}")

        self.track_years = sorted(list(self.track_years))  # Sort years for UI

    def get_sorted_by_plays(self, year=None):
        if year:
            if year in self.track_plays:
                return sorted(self.track_plays[year].items(), key=lambda item: item[1], reverse=True)
            else:
                return []  # No data for this year
        else:
            # Combine all years
            all_plays = {}
            for year_data in self.track_plays.values():
                for track, plays in year_data.items():
                    all_plays[track] = all_plays.get(track, 0) + plays
            return sorted(all_plays.items(), key=lambda item: item[1], reverse=True)

    def get_sorted_by_minutes(self, year=None):
        if year:
            if year in self.track_play_time:
                sorted_data = sorted(self.track_play_time[year].items(), key=lambda item: item[1], reverse=True)
                # Ensure track_plays has the track for the year
                if year in self.track_plays:
                    return [(track, self.track_plays[year][track]) for track, _ in sorted_data if track in self.track_plays[year]]
                else:
                    return []
            else:
                return []  # No data for this year
        else:
            # Combine all years
            all_play_time = {}
            for year_data in self.track_play_time.values():
                for track, play_time in year_data.items():
                    all_play_time[track] = all_play_time.get(track, 0) + play_time
            sorted_data = sorted(all_play_time.items(), key=lambda item: item[1], reverse=True)

            all_plays = {}
            for year_data in self.track_plays.values():
                for track, plays in year_data.items():
                    all_plays[track] = all_plays.get(track, 0) + plays

            return [(track, all_plays[track]) for track, _ in sorted_data if track in all_plays]
