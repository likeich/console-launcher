import os
import json

"""
Problem: Arcade file names are not the same as the full game title. Ex: "mslug.zip" is "Metal Slug - Super Vehicle-001"

Solution: Create a JSON file for each letter of the alphabet, containing the game titles and descriptions.
This is hosted on GitHub and can be accessed by the MAME frontend to retrieve the full game title.
Having a JSON file for each letter is a good balance between having a single file or a file for each game.

Database source: http://adb.arcadeitalia.net/download.php
"""

database_file_path = 'gamelist.txt'
save_folder_path = 'titles'

# Create a directory for the titles
os.makedirs(save_folder_path, exist_ok=True)

# Initialize a dictionary to hold game data
games_by_letter = {}

# Process the database file
with open(database_file_path, 'r') as file:
    # Skip the first line (headers)
    next(file)

    for line in file:
        # Split the line into name and description
        parts = line.split(maxsplit=1)
        if len(parts) >= 2:
            name, description = parts[0], parts[1].strip().removeprefix("\"").removesuffix("\"")
            first_letter = name[0].lower()  # Assuming game names are case-insensitive

            # Add the game to the dictionary
            if first_letter not in games_by_letter:
                games_by_letter[first_letter] = {}
            games_by_letter[first_letter][name] = description

# Create a JSON file for each letter
for letter, games in games_by_letter.items():
    with open(os.path.join(save_folder_path, f'{letter}.json'), 'w') as json_file:
        json.dump(games, json_file, indent=4)

print(f"JSON files have been created in the '{save_folder_path}' folder.")
