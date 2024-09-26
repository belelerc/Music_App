import unittest
import os
from main import MusicApp, Song, Playlist  # Import the main modules for testing

class TestMusicApp(unittest.TestCase):

    # Set up the test environment with sample data before each test
    def setUp(self):
        """Set up an instance of MusicApp and sample data for testing."""
        self.app = MusicApp(data_file='test_music_data.json')  # Use a separate test JSON file
        self.app.songs = [
            Song(name="Test Song 1", artists="Artist A", album="Album A", genre="Rock", duration="3:30"),
            Song(name="Test Song 2", artists="Artist B", album="Album B", genre="Pop", duration="4:10"),
        ]
        self.app.playlists = [
            Playlist(name="Test Playlist")  # Create a sample playlist
        ]
        self.app.playlists[0].add_song(self.app.songs[0])  # Add the first song to the playlist
        self.app.save_data()  # Save the data after setup

    # Clean up the test data file after each test
    def tearDown(self):
        """Clean up test data file."""
        if os.path.exists(self.app.data_file):  # Remove the test data file if it exists
            os.remove(self.app.data_file)

    # Test exporting an empty playlist
    def test_empty_playlist_export(self):
        """Test if exporting an empty playlist works correctly."""
        empty_playlist = Playlist(name="Empty Playlist")
        self.app.playlists.append(empty_playlist)  # Add an empty playlist
        self.app.save_data()

        # Export the empty playlist
        self.app.export_playlist("Empty Playlist")
        file_name = "Empty_Playlist.txt"

        # Check if the file was created
        self.assertTrue(os.path.exists(file_name))

        # Verify the contents of the file
        with open(file_name, 'r') as f:
            content = f.read()
            self.assertIn("Playlist: Empty Playlist", content)
            self.assertNotIn("Songs:", content)  # Ensure no songs are listed

        # Clean up the exported file
        os.remove(file_name)

    # Test if creating a song with an empty name raises an error
    def test_empty_song_name(self):
        """Test if adding a song with an empty name raises an error."""
        with self.assertRaises(ValueError):
            song = Song(name="", artists="Artist X", album="Album X", genre="Pop", duration="3:30")

    # Test if invalid duration format raises an error
    def test_invalid_duration_format(self):
        """Test if adding a song with an invalid duration format raises an error."""
        invalid_duration = "5:99"  # Invalid duration format
        with self.assertRaises(ValueError):
            song = Song(name="Invalid Duration Song", artists="Artist X", album="Album X", genre="Pop", duration=invalid_duration)

    # Test adding multiple songs to the app
    def test_add_multiple_songs(self):
        """Test if adding multiple songs works correctly."""
        songs_to_add = [
            {"name": "New Test Song 1", "artists": "Artist C", "album": "Album C", "genre": "Jazz", "duration": "5:20"},
            {"name": "New Test Song 2", "artists": "Artist D", "album": "Album D", "genre": "Blues", "duration": "3:45"}
        ]
        initial_song_count = len(self.app.songs)  # Get the initial song count

        # Add the new songs to the app
        for song_data in songs_to_add:
            song = Song(**song_data)
            self.app.songs.append(song)

        self.app.save_data()
        self.assertEqual(len(self.app.songs), initial_song_count + len(songs_to_add))  # Verify new song count

    # Test removing a song and then undoing the action
    def test_remove_song_and_undo(self):
        """Test if removing a song and then undoing the action works."""
        song_to_remove = self.app.songs[0]  # Select a song to remove
        initial_song_count = len(self.app.songs)

        # Remove the song from the app
        self.app.songs.remove(song_to_remove)
        self.app.undo_stack.append(('remove', song_to_remove))  # Prepare for undo operation
        self.app.save_data()
        self.assertEqual(len(self.app.songs), initial_song_count - 1)

        # Undo the remove action
        self.app.undo()
        self.assertEqual(len(self.app.songs), initial_song_count)  # Verify the song was restored

    # Test exporting a playlist
    def test_export_playlist(self):
        """Test if exporting a playlist works correctly."""
        playlist_name = "Test Playlist"

        # Export the playlist without prompting
        self.app.export_playlist(playlist_name)
        file_name = playlist_name.replace(" ", "_") + ".txt"  # Format the file name

        # Check if the file was created
        self.assertTrue(os.path.exists(file_name))

        # Verify the file contents
        with open(file_name, 'r') as f:
            content = f.read()
            self.assertIn("Playlist: Test Playlist", content)
            self.assertIn("Test Song 1", content)  # Verify the song is listed

        # Clean up the exported file
        os.remove(file_name)

    # Test adding a song to a playlist
    def test_add_song_to_playlist(self):
        """Test if adding a song to a playlist works."""
        initial_song_count_in_playlist = len(self.app.playlists[0].songs)
        self.app.playlists[0].add_song(self.app.songs[1])  # Add a song to the playlist
        self.app.save_data()
        self.assertEqual(len(self.app.playlists[0].songs), initial_song_count_in_playlist + 1)  # Verify the song count

    # Test removing a song from a playlist
    def test_remove_song_from_playlist(self):
        """Test if removing a song from a playlist works."""
        initial_song_count_in_playlist = len(self.app.playlists[0].songs)
        self.app.playlists[0].remove_song(self.app.songs[0].name)  # Remove a song by name
        self.app.save_data()
        self.assertEqual(len(self.app.playlists[0].songs), initial_song_count_in_playlist - 1)  # Verify the song count

    # Test creating a new playlist
    def test_create_playlist(self):
        """Test if creating a new playlist works."""
        initial_playlist_count = len(self.app.playlists)
        new_playlist = Playlist(name="New Test Playlist")  # Create a new playlist
        self.app.playlists.append(new_playlist)
        self.app.save_data()
        self.assertEqual(len(self.app.playlists), initial_playlist_count + 1)  # Verify the playlist count

    # Test deleting a playlist
    def test_delete_playlist(self):
        """Test if deleting a playlist works."""
        initial_playlist_count = len(self.app.playlists)
        playlist_to_delete = self.app.playlists[0]
        self.app.playlists.remove(playlist_to_delete)  # Remove the first playlist
        self.app.save_data()
        self.assertEqual(len(self.app.playlists), initial_playlist_count - 1)  # Verify the playlist count

    # Test searching for songs by artist
    def test_search_by_artist(self):
        """Test searching songs by artist."""
        search_term = "Artist A"
        results = [song for song in self.app.songs if search_term.lower() in (artist.lower() for artist in song.artists)]
        self.assertTrue(len(results) > 0)  # Ensure that results were found
        self.assertEqual(results[0].artists[0], "Artist A")  # Verify the correct artist was found

    # Test searching for songs by genre
    def test_search_by_genre(self):
        """Test searching songs by genre."""
        search_term = "Rock"
        results = [song for song in self.app.songs if search_term.lower() == song.genre.lower()]
        self.assertTrue(len(results) > 0)  # Ensure that results were found
        self.assertEqual(results[0].genre, "Rock")  # Verify the correct genre was found

    # Test searching for songs by album
    def test_search_by_album(self):
        """Test searching songs by album."""
        search_term = "Album A"
        results = [song for song in self.app.songs if search_term.lower() == song.album.lower()]
        self.assertTrue(len(results) > 0)  # Ensure that results were found
        self.assertEqual(results[0].album, "Album A")  # Verify the correct album was found

    # Test sorting songs by name
    def test_sort_songs_by_name(self):
        """Test if sorting songs by name works correctly."""
        self.app.songs.sort(key=lambda song: song.name)  # Sort songs by name
        self.assertEqual(self.app.songs[0].name, "Test Song 1")  # Verify the first song in the sorted list

    # Test sorting songs by duration
    def test_sort_songs_by_duration(self):
        """Test if sorting songs by duration works."""
        self.app.songs.sort(key=lambda song: song.duration)  # Sort songs by duration
        self.assertEqual(self.app.songs[0].duration, "3:30")  # Verify the first song in the sorted list

# Main function to run the unit tests
if __name__ == '__main__':
    unittest.main()