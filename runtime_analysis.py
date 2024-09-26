import time
import timeit
import matplotlib.pyplot as plt
from main import MusicApp, Song  # Import necessary classes from main.py

# Initialize the MusicApp instance with the specified data file
music_app = MusicApp(data_file='music_data.json')

# Function to generate a list of songs for testing, each song has a unique name and artist
def generate_songs(num_songs):
    return [Song(name=f"Song {i}", artists="Artist {i}", album="Album", genre="Genre", duration="3:00") for i in range(num_songs)]

# Test case for adding songs to the music library
def test_add_songs(num_songs):
    songs = generate_songs(num_songs)  # Generate the specified number of songs
    for song in songs:
        music_app.songs.append(song)  # Add each song directly to the songs list in MusicApp
    music_app.save_data()  # Save the changes after all songs are added

# Test case for searching a song by its name in the music library
def test_search_song():
    song_name = "Song 500"  # Search for a specific song by its name
    results = [song for song in music_app.songs if song_name.lower() in song.name.lower()]  # Find matching songs
    return results  # Return the search results

# Test case for removing a song from the music library
def test_remove_song():
    song_name = "Song 500"  # Specify the song to be removed
    song_to_remove = next((s for s in music_app.songs if s.name.lower() == song_name.lower()), None)  # Find the song
    if song_to_remove:
        music_app.songs.remove(song_to_remove)  # Remove the song from the list
        music_app.save_data()  # Save the updated library after removal
    return song_to_remove  # Return the removed song

# Test case for saving and loading the music library data
def test_save_and_load():
    music_app.save_data()  # Save the current state of the library to the JSON file
    music_app.load_data()  # Reload the data from the JSON file to simulate persistence

# Measure the performance of each operation and record execution times
def run_runtime_analysis():
    input_sizes = [100, 500, 1000, 5000]  # Different input sizes for testing
    add_times = []  # To store the execution time for adding songs
    search_times = []  # To store the execution time for searching a song
    remove_times = []  # To store the execution time for removing a song
    save_load_times = []  # To store the execution time for saving and loading data

    for size in input_sizes:
        # Measure time for adding songs to the library
        add_time = timeit.timeit(lambda: test_add_songs(size), number=1)
        add_times.append(add_time)  # Store the time for adding songs

        # Measure time for searching a specific song
        search_time = timeit.timeit(test_search_song, number=1)
        search_times.append(search_time)  # Store the time for searching songs

        # Measure time for removing a specific song
        remove_time = timeit.timeit(test_remove_song, number=1)
        remove_times.append(remove_time)  # Store the time for removing songs

        # Measure time for saving and loading data
        save_load_time = timeit.timeit(test_save_and_load, number=1)
        save_load_times.append(save_load_time)  # Store the time for saving and loading data

    # Plot the results for each operation's execution time
    plt.figure(figsize=(10, 6))

    # Plot for adding songs
    plt.plot(input_sizes, add_times, marker='o', label="Add Songs")
    # Plot for searching songs
    plt.plot(input_sizes, search_times, marker='o', label="Search Song")
    # Plot for removing songs
    plt.plot(input_sizes, remove_times, marker='o', label="Remove Song")
    # Plot for saving and loading data
    plt.plot(input_sizes, save_load_times, marker='o', label="Save & Load Data")

    plt.title("Performance of MusicApp Operations")  # Set the title of the plot
    plt.xlabel("Number of Songs")  # Label for x-axis
    plt.ylabel("Execution Time (seconds)")  # Label for y-axis
    plt.legend()  # Show the legend
    plt.grid(True)  # Show the grid for better readability
    plt.show()  # Display the plot

# Entry point for running the runtime analysis
if __name__ == "__main__":
    run_runtime_analysis()  # Execute the runtime analysis function