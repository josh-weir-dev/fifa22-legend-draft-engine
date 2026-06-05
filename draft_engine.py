import pandas as pd

print("Initialising FIFA 22 Legend Draft Engine...")
print("-----------------------------------------")

#Define paths to the database files
PLAYERS_PATH = "Data/players.txt"
LINKS_PATH = "Data/teamplayerlinks.txt"
TEAMS_PATH = "Data/teams.txt"
EDITED_NAMES_PATH = "Data/editedplayernames.txt"
DC_NAMES_PATH = "Data/dcplayernames.txt"

try:
    #Read values of files into Pandas DataFrames
    df_players = pd.read_csv(PLAYERS_PATH, sep='\t', low_memory=False, encoding='utf-16')
    df_links = pd.read_csv(LINKS_PATH, sep='\t', low_memory=False, encoding='utf-16')
    df_teams = pd.read_csv(TEAMS_PATH, sep='\t', low_memory=False, encoding='utf-16')
    df_edited_names = pd.read_csv(EDITED_NAMES_PATH, sep='\t', low_memory=False, encoding='utf-16')
    df_name_dictionary = pd.read_csv(DC_NAMES_PATH, sep='\t',low_memory=False, encoding='utf-16')

    print("Success: All core database files loaded perfectly!")
    print(f"Total players in database: {len(df_players):,}")
    print(f"Total edited names in database: {len(df_edited_names):,}")
    print(f"Total teams in database: {len(df_teams):,}")
    print(f"Total names in master dictionary: {len(df_name_dictionary):,}")

    print("\n--- Name Dictionary Columns ---")
    print(df_name_dictionary.columns.tolist())
    print("\n--- First 5 rows of Name Dictionary ---")
    print(df_name_dictionary.head(5))
except FileNotFoundError as e:
    print("Error: Could not find one or more database files!")
    print("Please check that your 'Data/' folder contains all 4 text files.")
    print("Details: {e}")
