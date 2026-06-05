import pandas as pd
import numpy as np

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

    print("Calculating ratings for available players")
    cols_to_convert = [
        'acceleration', 'sprintspeed', 'positioning', 'finishing', 'shotpower', 'dribbling', 'volleys',
        'shortpassing', 'longpassing', 'vision', 'ballcontrol', 'crossing', 'curve', 'agility',
        'interceptions', 'marking', 'standingtackle', 'slidingtackle', 'strength', 'aggression', 'headingaccuracy',
        'gkdiving', 'gkhandling', 'gkkicking', 'gkpositioning', 'gkreflexes'
    ]
    for col in cols_to_convert:
        df_draft_pool[col] = pd.to_numeric(df_draft_pool[col], errors='coerce').fillna(50)
    
    df_draft_pool['ATT_Score'] = (
        (df_draft_pool['finishing'] * 0.25) +
        (df_draft_pool['positioning'] * 0.20) +
        (df_draft_pool['dribbling'] * 0.15) +
        (df_draft_pool['shotpower'] * 0.15) +
        ((df_draft_pool['acceleration'] + df_draft_pool['sprintspeed']) / 2 * 0.15) +
        (df_draft_pool['volleys'] * 0.10)
    ).round(1)

    df_draft_pool['MID_Score'] = (
        (df_draft_pool['shortpassing'] * 0.25) +
        (df_draft_pool['vision'] * 0.25) +
        (df_draft_pool['ballcontrol'] * 0.20) +
        (df_draft_pool['longpassing'] * 0.15) +
        (df_draft_pool['crossing'] * 0.05) +
        (df_draft_pool['curve'] * 0.05) +
        (df_draft_pool['agility'] * 0.05)
    ).round(1)

    df_draft_pool['DEF_Score'] = (
        (df_draft_pool['standingtackle'] * 0.25) +
        (df_draft_pool['marking'] * 0.20) +
        (df_draft_pool['interceptions'] * 0.20) +
        (df_draft_pool['slidingtackle'] * 0.15) +
        (df_draft_pool['strength'] * 0.10) +
        (df_draft_pool['aggression'] * 0.05) +
        (df_draft_pool['headingaccuracy'] * 0.05)
    ).round(1)

    df_draft_pool['GK_Score'] = (
        (df_draft_pool['gkreflexes'] * 0.30) +
        (df_draft_pool['gkdiving'] * 0.25) +
        (df_draft_pool['gkhandling'] * 0.20) +
        (df_draft_pool['gkpositioning'] * 0.15) +
        (df_draft_pool['gkkicking'] * 0.10)
    ).round(1)

    print("Ratings successfully calculated")

    print("Mapping player name IDs to strings ...")

    df_dict_clean = df_name_dictionary[['nameid', 'name']].drop_duplicates(subset=['nameid'], keep='first')
    name_lookup = df_dict_clean.set_index('nameid')['name']

    df_draft_pool['first_name'] = df_draft_pool['firstnameid'].map(name_lookup).fillna('')
    df_draft_pool['last_name'] = df_draft_pool['lastnameid'].map(name_lookup).fillna('')

    if 'playerid' in df_edited_names.columns:
        edited_cols = df_edited_names.columns
        fname_col = 'firstname'
        lname_col = 'surname'

        if fname_col and lname_col:
            edited_lookup = df_edited_names[['playerid', fname_col, lname_col]].drop_duplicates(subset=['playerid'])
            df_draft_pool = df_draft_pool.merge(edited_lookup, on='playerid', how='left')

            df_draft_pool['first_name'] = df_draft_pool['first_name'].replace('', np.nan).fillna(df_draft_pool[fname_col]).fillna('')
            df_draft_pool['last_name'] = df_draft_pool['last_name'].replace('', np.nan).fillna(df_draft_pool[lname_col]).fillna('')

            df_draft_pool = df_draft_pool.drop(columns=[fname_col, lname_col], errors='ignore')

    df_draft_pool['full_name'] = (df_draft_pool['first_name'] + ' ' + df_draft_pool['last_name']).str.strip()

    df_draft_pool['full_name'] = df_draft_pool['full_name'].replace('', np.nan).fillna('Legend ID-' + df_draft_pool['playerid'].astype(str))
    print("Success: Names mapped flawlessly!")
    print("-----------------------------------------")

    print("TOP 5 ATTACKING TARGETS FOR THE CPU:")
    top_attackers = df_draft_pool.sort_values(by='ATT_Score', ascending=False).head(5)
    print(top_attackers[['playerid', 'full_name', 'overallrating', 'ATT_Score', 'MID_Score', 'DEF_Score']].to_string(index=False))

    print("TOP 5 DEFENSIVE TARGETS FOR THE CPU:")
    top_defenders = df_draft_pool.sort_values(by='DEF_Score', ascending=False).head(5)
    print(top_defenders[['playerid', 'full_name', 'overallrating', 'ATT_Score', 'MID_Score', 'DEF_Score']].to_string(index=False))
    print("-----------------------------------------")
except FileNotFoundError as e:
    print("Error: Could not find one or more database files!")
    print("Please check that your 'Data/' folder contains all 4 text files.")
    print("Details: {e}")
