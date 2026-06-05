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
    
    print("Filtering database down to draft pool ....")
    draft_teams = [269, 270, 271, 272, 819, 820, 822, 1443, 1447, 1516, 1786, 1788]

    #Find all player IDs for those teams
    target_player_links = df_links[df_links['teamid'].isin(draft_teams)]
    target_player_ids = target_player_links['playerid']

    df_draft_pool = df_players[df_players['playerid'].isin(target_player_ids)].copy()

    print("Success: Draft pool selected successfully!")
    print(f"Total players available for the draft: {len(df_draft_pool):,}")
except FileNotFoundError as e:
    print("Error: Could not find one or more database files!")
    print("Please check that your 'Data/' folder contains all 4 text files.")
    print("Details: {e}")
