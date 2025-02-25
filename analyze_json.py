import json
import os
from datetime import datetime


class SpotifyAnalyzer:
    def __init__(self):
        # Stores how many times each track was played by year
        self.track_plays = {}       # {year: {track_key: play_count}}
        # Stores total play time (milliseconds) for each track by year
        self.track_play_time = {}   # {year: {track_key: total_ms}}
        self.track_years = set()    # Distinct years found in the data

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
        """
        For each track in combined_data, count a play only if ms_played >= 20000.
        Also accumulate total milliseconds played for each track+year.
        """
        self.track_plays.clear()
        self.track_play_time.clear()
        self.track_years.clear()

        for entry in combined_data:
            ms_played = entry.get("ms_played", 0)
            # Only count if 20+ seconds were played
            if ms_played >= 20000:
                track_name = entry.get("master_metadata_track_name")
                artist_name = entry.get("master_metadata_album_artist_name")
                timestamp = entry.get("ts")

                if track_name and artist_name and timestamp:
                    key = f"{artist_name} - {track_name}"
                    try:
                        year = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).year
                        self.track_years.add(year)

                        # Update track plays
                        if year not in self.track_plays:
                            self.track_plays[year] = {}
                        self.track_plays[year][key] = self.track_plays[year].get(key, 0) + 1

                        # Update track play time
                        if year not in self.track_play_time:
                            self.track_play_time[year] = {}
                        self.track_play_time[year][key] = self.track_play_time[year].get(key, 0) + ms_played

                    except ValueError:
                        print(f"Invalid timestamp format: {timestamp}")

        # Sort year values (for UI dropdowns or reports)
        self.track_years = sorted(list(self.track_years))

    def _get_year_dict(self, data_dict, year=None):
        """
        Returns dict for a single year or combines all years if year is None.
        """
        if year is not None:
            return data_dict.get(year, {})
        combined = {}
        for single_year_dict in data_dict.values():
            for track, val in single_year_dict.items():
                combined[track] = combined.get(track, 0) + val
        return combined

    def get_sorted_by_plays(self, year=None):
        """
        Sorts tracks by total plays in descending order.
        """
        tracks_data = self._get_year_dict(self.track_plays, year)
        return sorted(tracks_data.items(), key=lambda item: item[1], reverse=True)

    def get_sorted_by_minutes(self, year=None):
        """
        Sorts tracks by total milliseconds played in descending order.
        Returns a list of (track_key, total_plays) tuples, matching the format used in display.
        """
        selected_dict = self._get_year_dict(self.track_play_time, year)
        sorted_data = sorted(selected_dict.items(), key=lambda item: item[1], reverse=True)

        # Filter out records if they don't exist in track_plays for the same year(s)
        if year is not None:
            if year in self.track_plays:
                return [(track, self.track_plays[year][track]) for track, _ in sorted_data
                        if track in self.track_plays[year]]
            else:
                return []
        else:
            # Combine plays too
            all_plays = self._get_year_dict(self.track_plays, None)
            return [(track, all_plays[track]) for track, _ in sorted_data if track in all_plays]
