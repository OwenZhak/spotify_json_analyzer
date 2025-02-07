import unittest
from unittest.mock import patch, mock_open
from analyze_json import SpotifyAnalyzer

class TestSpotifyAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SpotifyAnalyzer()

    def test_load_json_files(self):
        valid_json_content = '[{"ms_played": 30000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"}]'
        invalid_json_content = 'Not a JSON'
        empty_json_content = '[]'

        with patch('builtins.open', mock_open(read_data=valid_json_content)), patch('os.path.exists', return_value=True):
            result = self.analyzer.load_json_files(["test_file.json"])
            self.assertEqual(len(result), 1, "Should load one entry")

        with patch('builtins.open', mock_open(read_data=invalid_json_content)), patch('os.path.exists', return_value=True):
            result = self.analyzer.load_json_files(["test_file.json"])
            self.assertIsInstance(result, str, "Should return an error message for invalid JSON")

        with patch('builtins.open', mock_open(read_data=empty_json_content)), patch('os.path.exists', return_value=True):
            result = self.analyzer.load_json_files(["test_file.json"])
            self.assertIsInstance(result, str, "Should return an error message for empty JSON")

    def test_process_data(self):
        combined_data = [
            {"ms_played": 30000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"},
            {"ms_played": 25000, "master_metadata_track_name": "Track2", "master_metadata_album_artist_name": "Artist2"},
            {"ms_played": 10000, "master_metadata_track_name": "Track3", "master_metadata_album_artist_name": "Artist3"}
        ]
        self.analyzer.process_data(combined_data)
        self.assertEqual(len(self.analyzer.track_plays), 2, "Should process and count tracks with ms_played >= 20000")
        self.assertEqual(self.analyzer.track_plays["Artist1 - Track1"], 1, "Should correctly count track plays")
        self.assertEqual(self.analyzer.track_play_time["Artist1 - Track1"], 30000, "Should correctly sum ms_played")

    def test_process_data_with_duplicates(self):
        combined_data = [
            {"ms_played": 30000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"},
            {"ms_played": 25000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"},
            {"ms_played": 15000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"}  # This should be ignored
        ]
        self.analyzer.process_data(combined_data)
        self.assertEqual(len(self.analyzer.track_plays), 1, "Should process and count unique tracks with ms_played >= 20000")
        self.assertEqual(self.analyzer.track_plays["Artist1 - Track1"], 2, "Should correctly count track plays")
        self.assertEqual(self.analyzer.track_play_time["Artist1 - Track1"], 55000, "Should correctly sum ms_played")

    def test_get_sorted_by_plays(self):
        self.analyzer.track_plays = {"Artist1 - Track1": 2, "Artist2 - Track2": 1}
        sorted_plays = self.analyzer.get_sorted_by_plays()
        self.assertEqual(sorted_plays, [("Artist1 - Track1", 2), ("Artist2 - Track2", 1)], "Should sort tracks by plays")

    def test_get_sorted_by_minutes(self):
        self.analyzer.track_play_time = {"Artist1 - Track1": 60000, "Artist2 - Track2": 30000}
        self.analyzer.track_plays = {"Artist1 - Track1": 2, "Artist2 - Track2": 1}
        sorted_minutes = self.analyzer.get_sorted_by_minutes()
        self.assertEqual(sorted_minutes, [("Artist1 - Track1", 2), ("Artist2 - Track2", 1)], "Should sort tracks by minutes")

if __name__ == "__main__":
    unittest.main()
