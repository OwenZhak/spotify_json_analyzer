import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from main import SpotifyAnalyzerUI


class TestSpotifyAnalyzerUI(unittest.TestCase):

    @patch('main.filedialog.askopenfilenames')
    def test_select_files(self, mock_askopenfilenames):
        mock_askopenfilenames.return_value = ["test_file.json"]
        mock_root = tk.Tk()
        ui = SpotifyAnalyzerUI(mock_root)
        ui.analyzer = MagicMock()

        # Mock analyzer methods
        ui.analyzer.load_json_files.return_value = [{"ms_played": 30000, "master_metadata_track_name": "Track1", "master_metadata_album_artist_name": "Artist1"}]
        ui.analyzer.get_sorted_by_plays.return_value = [("Artist1 - Track1", 1)]
        ui.analyzer.process_data = MagicMock()

        ui.select_files()
        ui.analyzer.load_json_files.assert_called_once_with(["test_file.json"])
        ui.analyzer.process_data.assert_called_once()

    def test_display_result(self):
        mock_root = tk.Tk()
        ui = SpotifyAnalyzerUI(mock_root)
        ui.result_text = MagicMock()

        sorted_data = [("Artist1 - Track1", 1)]
        ui.display_result(sorted_data)
        ui.result_text.insert.assert_any_call(tk.END, "1. Artist1 - Track1: 1 plays, 0.50 minutes\n")

    @patch('main.SpotifyAnalyzerUI.display_result')
    def test_sort_by_plays(self, mock_display_result):
        mock_root = tk.Tk()
        ui = SpotifyAnalyzerUI(mock_root)
        ui.analyzer = MagicMock()
        ui.analyzer.get_sorted_by_plays.return_value = [("Artist1 - Track1", 1)]

        ui.sort_by_plays()
        ui.analyzer.get_sorted_by_plays.assert_called_once()
        mock_display_result.assert_called_once()

    @patch('main.SpotifyAnalyzerUI.display_result')
    def test_sort_by_minutes(self, mock_display_result):
        mock_root = tk.Tk()
        ui = SpotifyAnalyzerUI(mock_root)
        ui.analyzer = MagicMock()
        ui.analyzer.get_sorted_by_minutes.return_value = [("Artist1 - Track1", 1)]

        ui.sort_by_minutes()
        ui.analyzer.get_sorted_by_minutes.assert_called_once()
        mock_display_result.assert_called_once()


if __name__ == "__main__":
    unittest.main()
