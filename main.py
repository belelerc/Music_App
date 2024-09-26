import json
import os
import re

# Function to get user input and validate it based on whether empty input is allowed
def get_valid_input(prompt, allow_empty=False):
    while True:
        user_input = input(prompt).strip()
        if user_input or allow_empty:  # Return input if it's valid or empty is allowed
            return user_input
        print("Input cannot be empty. Please try again.")  # Error message for empty input

# Function to confirm a user action by asking for 'y' or 'n'
def confirm_action(prompt):
    while True:
        confirmation = input(f"{prompt} (y/n): ").lower()
        if confirmation in ['y', 'n']:  # Check if user input is 'y' or 'n'
            return confirmation == 'y'  # Return True for 'y', False for 'n'
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")  # Invalid input message

# Class representing a song with details like name, artists, album, genre, and duration
class Song:
    def __init__(self, name, artists, album, genre, duration):
        if not name:  # Check if song name is empty
            raise ValueError("Song name cannot be empty.")  # Raise error if name is empty
        
        # Validate the song duration using a regular expression (e.g., mm:ss or hh:mm:ss)
        if not re.match(r'^\d+:[0-5]\d$', duration):
            raise ValueError(f"Invalid duration format: {duration}. Expected format 'mm:ss' or 'hh:mm:ss'.")
        
        self.name = name
        self.artists = [artist.strip() for artist in artists.split(',')]  # Handle multiple artists
        self.album = album
        self.genre = genre
        self.duration = duration

    # String representation of the song (for easy display)
    def __str__(self):
        return f"{self.name} by {', '.join(self.artists)}"

    # Convert song data into a dictionary (useful for saving to JSON)
    def to_dict(self):
        return {
            "name": self.name,
            "artists": self.artists,
            "album": self.album,
            "genre": self.genre,
            "duration": self.duration
        }

    # Static method to create a Song object from a dictionary
    @staticmethod
    def from_dict(data):
        return Song(
            name=data['name'],
            artists=', '.join(data['artists']),
            album=data['album'],
            genre=data['genre'],
            duration=data['duration']
        )

# Class representing a playlist containing multiple songs
class Playlist:
    def __init__(self, name):
        self.name = name  # Initialize playlist name
        self.songs = []  # Initialize an empty list of songs in the playlist

    # Add a song to the playlist
    def add_song(self, song):
        self.songs.append(song)

    # Remove a song from the playlist by matching song name
    def remove_song(self, song_name):
        self.songs = [song for song in self.songs if song.name.lower() != song_name.lower()]

    # String representation of the playlist (just the name)
    def __str__(self):
        return self.name

    # Convert playlist data into a dictionary (useful for saving to JSON)
    def to_dict(self):
        return {
            "name": self.name,
            "songs": [song.to_dict() for song in self.songs]
        }

    # Static method to create a Playlist object from a dictionary
    @staticmethod
    def from_dict(data):
        playlist = Playlist(data["name"])
        for song_data in data["songs"]:  # Add each song in the data to the playlist
            song = Song.from_dict(song_data)
            playlist.add_song(song)
        return playlist

# Main class representing the music application
class MusicApp:
    def __init__(self, data_file='music_data.json'):
        self.data_file = data_file  # JSON file where data is stored
        self.songs = []  # List of songs
        self.playlists = []  # List of playlists
        self.undo_stack = []  # Stack to store undo operations
        self.load_data()  # Load data from file on initialization

    # Load song and playlist data from the JSON file
    def load_data(self):
        if os.path.exists(self.data_file):  # Check if file exists
            try:
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    self.songs = [Song.from_dict(song_data) for song_data in data["songs"]]
                    self.playlists = [Playlist.from_dict(playlist_data) for playlist_data in data["playlists"]]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}")  # Handle errors in file reading/parsing

    # Save song and playlist data to the JSON file
    def save_data(self):
        data = {
            "songs": [song.to_dict() for song in self.songs],
            "playlists": [playlist.to_dict() for playlist in self.playlists]
        }
        with open(self.data_file, 'w') as file:  # Write data back to the file
            json.dump(data, file, indent=4)

    # Function to add multiple songs at once
    def add_multiple_songs(self):
        """Allows user to input multiple songs one by one."""
        while True:
            name = get_valid_input("Enter the song name (or 'q' to stop): ")
            if name.lower() == 'q':  # Exit the loop if user types 'q'
                break
            artists = get_valid_input("Enter the artist name or enter multiple artists separated by a comma: ")
            album = get_valid_input("Enter the album name: ")
            genre = get_valid_input("Enter the genre: ")
            duration = get_valid_input("Enter the duration (e.g., mm:ss): ")
            
            if not re.match(r'^\d+:\d{2}$', duration):  # Validate the duration format
                print("Invalid duration format. Please enter in 'mm:ss' or 'hh:mm:ss' format.")
                continue
            
            song = Song(name, artists, album, genre, duration)  # Create a new Song object
            self.songs.append(song)  # Add the song to the list
            self.save_data()  # Save changes to the file
            print(f"Song '{name}' added successfully.")  # Confirmation message

    # Function to remove a song from the library and playlists
    def remove_song(self):
        song_name = get_valid_input("Enter the name of the song to remove: ")
        song = next((s for s in self.songs if s.name.lower() == song_name.lower()), None)
        if song:  # Check if the song exists
            if confirm_action(f"Are you sure you want to remove the song '{song_name}'?"):
                self.undo_stack.append(('remove', song))  # Add removal action to the undo stack
                self.songs.remove(song)  # Remove song from library
                for playlist in self.playlists:  # Remove song from all playlists
                    playlist.songs = [s for s in playlist.songs if s.name.lower() != song_name.lower()]
                self.save_data()  # Save changes to the file
                print(f"Song '{song_name}' removed from library and all playlists.")
            else:
                print("Action canceled.")  # User canceled the action
        else:
            print(f"Song '{song_name}' not found in the library.")  # Song not found

    # Undo the last remove action
    def undo(self):
        """Undo the last remove song operation."""
        if not self.undo_stack:  # Check if there's anything to undo
            print("Nothing to undo.")
            return
        
        last_action = self.undo_stack.pop()  # Retrieve the last action
        action_type, song = last_action
        if action_type == 'remove':
            self.songs.append(song)  # Restore the song
            self.save_data()  # Save changes
            print(f"Undo: Song '{song.name}' has been restored.")  # Confirmation message

    # Function to create a new playlist
    def create_playlist(self):
        name = get_valid_input("Enter the playlist name: ")
        playlist = Playlist(name)  # Create a new playlist
        self.playlists.append(playlist)  # Add it to the list
        self.save_data()  # Save changes
        print("Playlist created successfully.")  # Confirmation message

    # Function to export a playlist to a text file
    def export_playlist(self, playlist_name=None):
        """Export a playlist to a text file."""
        if playlist_name is None:
            playlist_name = get_valid_input("Enter the playlist name to export: ")  # Get playlist name from user

        playlist = next((p for p in self.playlists if p.name.lower() == playlist_name.lower()), None)
        if playlist:  # Check if the playlist exists
            file_name = playlist_name.replace(" ", "_") + ".txt"  # Create a filename
            with open(file_name, 'w') as f:
                f.write(f"Playlist: {playlist.name}\n")
                if playlist.songs:  # Write songs if there are any
                    f.write("Songs:\n")
                    for song in playlist.songs:
                        f.write(f"{song.name} by {', '.join(song.artists)} ({song.duration})\n")
            print(f"Playlist '{playlist_name}' exported to '{file_name}'")  # Confirmation message
        else:
            print("Playlist not found.")  # Playlist not found message

    # Function to add a song to a playlist
    def add_song_to_playlist(self):
        song_name = get_valid_input("Enter the song name: ")
        playlist_name = get_valid_input("Enter the playlist name: ")
        song = next((s for s in self.songs if s.name.lower() == song_name.lower()), None)
        playlist = next((p for p in self.playlists if p.name.lower() == playlist_name.lower()), None)
        if song and playlist:  # Check if both song and playlist exist
            playlist.add_song(song)  # Add song to playlist
            self.save_data()  # Save changes
            print("Song added to playlist successfully.")  # Confirmation message
        else:
            print("Song or playlist not found.")  # Error message

    # Function to search for songs in the library by name
    def search_songs(self):
        search_term = get_valid_input("Enter the search term: ")
        results = [song for song in self.songs if search_term.lower() in song.name.lower()]
        if results:  # Display results if any songs match
            print("Search results:")
            for song in results:
                print(song)
        else:
            print(f"No matching songs found for '{search_term}'.")  # No results message

    # Sub-menu for song-related actions
    def songs_menu(self):
        while True:
            print("\n--- Songs Menu ---")
            print("1. Add New Song(s)")
            print("2. Remove Song from Library")
            print("3. Undo Last Remove")
            print("4. Back to Main Menu")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.add_multiple_songs()  # Call function to add songs
            elif choice == '2':
                self.remove_song()  # Call function to remove song
            elif choice == '3':
                self.undo()  # Call function to undo last action
            elif choice == '4':
                break  # Exit to main menu
            else:
                print("Invalid choice. Please try again.")  # Handle invalid input

    # Sub-menu for playlist-related actions
    def playlists_menu(self):
        while True:
            print("\n--- Playlists Menu ---")
            print("1. Create Playlist")
            print("2. Add Song to Playlist")
            print("3. Export Playlist")
            print("4. Back to Main Menu")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.create_playlist()  # Call function to create playlist
            elif choice == '2':
                self.add_song_to_playlist()  # Call function to add song to playlist
            elif choice == '3':
                self.export_playlist()  # Call function to export playlist
            elif choice == '4':
                break  # Exit to main menu
            else:
                print("Invalid choice. Please try again.")  # Handle invalid input

    # Main menu function to navigate the app
    def main_menu(self):
        while True:
            print("\n--- Music App Main Menu ---")
            print("1. Songs Menu")
            print("2. Playlists Menu")
            print("3. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.songs_menu()  # Go to songs menu
            elif choice == '2':
                self.playlists_menu()  # Go to playlists menu
            elif choice == '3':
                self.save_data()  # Save data before exiting
                print("Exiting the app.")
                break  # Exit the application
            else:
                print("Invalid choice. Please try again.")  # Handle invalid input

# Entry point of the program
if __name__ == "__main__":
    app = MusicApp()
    app.main_menu()  # Start the application by showing the main menu