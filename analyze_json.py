import json
import os
from datetime import datetime

class SpotifyAnalyzer:
    def __init__(self):
        # Track statistics
        self.track_plays = {}       # {year: {track_key: play_count}}
        self.track_play_time = {}   # {year: {track_key: total_ms}}
        # New artist statistics
        self.artist_plays = {}      # {year: {artist_name: play_count}}
        self.artist_play_time = {}  # {year: {artist_name: total_ms}}
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
        Also accumulate total milliseconds played for each track+year and artist+year.
        """
        self.track_plays.clear()
        self.track_play_time.clear()
        self.artist_plays.clear()
        self.artist_play_time.clear()
        self.track_years.clear()

        for entry in combined_data:
            ms_played = entry.get("ms_played", 0)
            # Only count if 20+ seconds were played
            if ms_played >= 20000:
                track_name = entry.get("master_metadata_track_name")
                artist_name = entry.get("master_metadata_album_artist_name")
                timestamp = entry.get("ts")

                if track_name and artist_name and timestamp:
                    track_key = f"{artist_name} - {track_name}"
                    try:
                        year = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).year
                        self.track_years.add(year)

                        # Update track plays and play time
                        if year not in self.track_plays:
                            self.track_plays[year] = {}
                        self.track_plays[year][track_key] = self.track_plays[year].get(track_key, 0) + 1

                        if year not in self.track_play_time:
                            self.track_play_time[year] = {}
                        self.track_play_time[year][track_key] = self.track_play_time[year].get(track_key, 0) + ms_played

                        # Update artist plays and play time
                        if year not in self.artist_plays:
                            self.artist_plays[year] = {}
                        self.artist_plays[year][artist_name] = self.artist_plays[year].get(artist_name, 0) + 1

                        if year not in self.artist_play_time:
                            self.artist_play_time[year] = {}
                        self.artist_play_time[year][artist_name] = self.artist_play_time[year].get(artist_name, 0) + ms_played

                    except ValueError:
                        print(f"Invalid timestamp format: {timestamp}")

        self.track_years = sorted(list(self.track_years))

    def _get_year_dict(self, data_dict, year=None):
        """
        Returns dict for a single year or combines all years if year is None.
        """
        if year is not None:
            return data_dict.get(year, {})
        combined = {}
        for single_year_dict in data_dict.values():
            for key, val in single_year_dict.items():
                combined[key] = combined.get(key, 0) + val
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
        Returns a list of (track_key, total_plays) tuples.
        """
        selected_dict = self._get_year_dict(self.track_play_time, year)
        sorted_data = sorted(selected_dict.items(), key=lambda item: item[1], reverse=True)

        if year is not None:
            if year in self.track_plays:
                return [(track, self.track_plays[year][track]) for track, _ in sorted_data
                        if track in self.track_plays[year]]
            else:
                return []
        else:
            all_plays = self._get_year_dict(self.track_plays, None)
            return [(track, all_plays[track]) for track, _ in sorted_data if track in all_plays]
            
    def get_artists_sorted_by_plays(self, year=None):
        """
        Sorts artists by total plays in descending order.
        """
        artists_data = self._get_year_dict(self.artist_plays, year)
        return sorted(artists_data.items(), key=lambda item: item[1], reverse=True)

    def get_artists_sorted_by_minutes(self, year=None):
        """
        Sorts artists by total milliseconds played in descending order.
        Returns a list of (artist_name, total_plays) tuples.
        """
        selected_dict = self._get_year_dict(self.artist_play_time, year)
        sorted_data = sorted(selected_dict.items(), key=lambda item: item[1], reverse=True)

        if year is not None:
            if year in self.artist_plays:
                return [(artist, self.artist_plays[year][artist]) for artist, _ in sorted_data
                        if artist in self.artist_plays[year]]
            else:
                return []
        else:
            all_plays = self._get_year_dict(self.artist_plays, None)
            return [(artist, all_plays[artist]) for artist, _ in sorted_data if artist in all_plays]
