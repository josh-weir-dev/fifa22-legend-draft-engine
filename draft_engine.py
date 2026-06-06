import pandas as pd
import numpy as np
import random

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

    if 'nameid' in df_name_dictionary.columns:
        df_name_dictionary['nameid'] = pd.to_numeric(df_name_dictionary['nameid'], errors='coerce')
    
    df_dict_clean = df_name_dictionary[['nameid', 'name']].dropna().drop_duplicates(subset=['nameid'], keep='first')
    
    # Force the lookup index to be standard Int64 so float decimals don't break it
    name_lookup = df_dict_clean.set_index(df_dict_clean['nameid'].astype('Int64'))['name']

    # 🔧 FIX 2: Ensure the draft pool IDs are also cast to Int64 before mapping
    pool_first_id = pd.to_numeric(df_draft_pool['firstnameid'], errors='coerce').astype('Int64')
    pool_last_id = pd.to_numeric(df_draft_pool['lastnameid'], errors='coerce').astype('Int64')

    # Execute the mapping with matching data types
    df_draft_pool['first_name'] = pool_first_id.map(name_lookup).fillna('')
    df_draft_pool['last_name'] = pool_last_id.map(name_lookup).fillna('')

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
    
    print("Setting up Draft Engine position requirments")

    teams_list = [
        {"teamid": 269, "name": "Brondby IF"},
        {"teamid": 270, "name": "Silkeborg IF"},
        {"teamid": 271, "name": "Aarhus GF"},
        {"teamid": 272, "name": "Odense Boldklub"},
        {"teamid": 819, "name": "FC Kobenhavn"},
        {"teamid": 820, "name": "Aalborg BK"},
        {"teamid": 822, "name": "Vejle BK"},
        {"teamid": 1443, "name": "Viborg FF"},
        {"teamid": 1447, "name": "Sonderjysk E"},
        {"teamid": 1516, "name": "FC Midtjylland"},
        {"teamid": 1786, "name": "Randers FC"},
        {"teamid": 1788, "name": "FC Nordsjaelland"}
    ]

    rosters = {t["teamid"]: [] for t in teams_list}

    position_counts = {
        t["teamid"]: {"GK": 0, "DEF": 0, "MID": 0, "ATT": 0}
        for t in teams_list
    }

    def calculate_demand_multiplier(current_counts, position):
        count = current_counts[position]

        if position == "GK":
            return 1.0 if count < 2 else 0.0
            
        elif position == "DEF":
            return 1.0 if count < 6 else 0.0
            
        elif position == "MID":
            return 1.0 if count < 7 else 0.0
            
        elif position == "ATT":
            return 1.0 if count < 5 else 0.0
        
        return 1.0

    print("Success: Draft positions setup and cpu logic initialised")

    print("Mapping position integers to the 4 major position areas")

    position_map = {
        0: 'GK',
        3:'DEF', 5:'DEF', 7:'DEF', 8:'DEF',
        10: 'MID', 12: 'MID', 16: 'MID', 18:'MID',14: 'MID', 
        21: 'ATT', 23:'ATT', 25: 'ATT', 27:'ATT'
    }

    df_draft_pool['Position_Group'] = df_draft_pool['preferredposition1'].map(position_map).fillna('MID')

    def assign_base_score(row):
        if row['Position_Group'] == 'GK': return row['GK_Score']
        if row['Position_Group'] == 'DEF': return row['DEF_Score']
        if row['Position_Group'] == 'MID': return row['MID_Score']
        return row['ATT_Score']
    
    df_draft_pool['Base_Archetype_Score'] = df_draft_pool.apply(assign_base_score, axis=1)

    print("Success: Positions and base scores have been assigned!")

    print("Starting the 20-Round Legend Draft")

    random.shuffle(teams_list)

    for index, team in enumerate(teams_list, start=1):
        marker = "YOU" if team["teamid"] == 1788 else ""
        print(f"Pick {index}: {team['name']}{marker}")

    TOTAL_ROUNDS = 20
    USER_TEAM_ID = 1788

    draft_history = []

    for round_num in range(1, TOTAL_ROUNDS + 1):
        print(f"\n=========================================================")
        print(f"ROUND {round_num} / {TOTAL_ROUNDS}")
        print(f"=========================================================")

        if round_num % 2 != 0:
            current_round_order = teams_list.copy()
            print("Draft Order: Forward")
        else:
            current_round_order = teams_list[::-1]
            print("Draft Order: Reverse")
        print("-------------------------------------")

        for team in current_round_order:
            t_id = team["teamid"]
            t_name = team["name"]

            available_players = df_draft_pool[~df_draft_pool['playerid'].isin(draft_history)].copy()

            if available_players.empty:
                print("No more players left in the pool to draft!")
                break

            def calculate_draft_priority(row):
                pos = row['Position_Group']
                base_score = row['Base_Archetype_Score']
                current_counts = position_counts[t_id]
                multiplier = calculate_demand_multiplier(current_counts, pos)
                return base_score * multiplier
            
            available_players['Draft_Priority'] = available_players.apply(calculate_draft_priority, axis=1)

            if t_id == USER_TEAM_ID:
                print(f"Your Turn! [ {t_name.upper()} ]")
                print("Your Current Roster Breakdown: ")
                print(f"GKs: {position_counts[t_id]['GK']}/2 | DEFs: {position_counts[t_id]['DEF']}/6 | MIDs: {position_counts[t_id]['MID']}/7 | ATTs: {position_counts[t_id]['ATT']}/5\n")

                print("Top Available Talents For Your Board:")
                for p_grp in ['GK', 'DEF', 'MID', 'ATT']:
                    sub_pool = available_players[available_players['Position_Group'] == p_grp]
                    if calculate_demand_multiplier(position_counts[t_id], p_grp) == 0:
                        print(f"{p_grp}: [Position Is Full]")
                        continue

                    top_options = sub_pool.sort_values(by='Base_Archetype_Score', ascending=False).head(5)
                    print(f"{p_grp} Options:")
                    for _, row in top_options.iterrows():
                        print(f"• {row['full_name']:<30} (OVR: {row['overallrating']} | Score: {row['Base_Archetype_Score']})")
                
                while True:
                    search_query = input("Enter the name of the player you want to draft: ").strip()

                    if len(search_query) < 2:
                        print("Please type at least 2 characters to search for a player")
                        continue

                    matches = available_players[available_players['full_name'].str.contains(search_query, case=False, na=False)]

                    if matches.empty:
                        print(f"No available players found matching '{search_query}'")
                        continue

                    if len(matches) > 1:
                        print(f"Found {len(matches)} players matching '{search_query}':")
                        matches_list = matches.sort_values(by='Base_Archetype_Score', ascending=False).reset_index(drop=True)

                        for idx, row in matches_list.iterrows():
                            print(f"[{idx + 1}] {row['full_name']:<30} ({row['Position_Group']} | OVR: {row['overallrating']})")
                        print("[0] Cancel search and re-type name")

                        try:
                            chocice_idx=int(input("Type the line number of the player you want: ").strip())
                            if chocice_idx == 0:
                                continue
                            if chocice_idx <1 or chocice_idx > len (matches_list):
                                print("Invalid choice number")
                                continue
                            selected_player = matches_list.iloc[chocice_idx-1]
                        except ValueError:
                            print("Invalid entry. Please enter a valid menu number")
                            continue
                    
                    else:
                        selected_player = matches.iloc[0]
                    
                    chosen_id = selected_player['playerid']
                    p_pos = selected_player['Position_Group']

                    if calculate_demand_multiplier(position_counts[t_id], p_pos) == 0:
                        print(f"Selection rejected: You cannot draft {selected_player['full_name']}. Your {p_pos} area is full")
                        continue

                    break
            else:
                available_players = available_players.sort_values(by='Draft_Priority', ascending=False)
                selected_player = available_players.iloc[0]
                chosen_id = selected_player['playerid']
                p_pos = selected_player['Position_Group']
            
            p_name = selected_player['full_name']
            p_rating = selected_player['overallrating']

            draft_history.append(chosen_id)

            rosters[t_id].append({
                "playerid": chosen_id,
                "name": p_name,
                "position": p_pos,
                "rating": p_rating
            })

            position_counts[t_id][p_pos] += 1

            if t_id == USER_TEAM_ID:
                print(f"SUCCESS! You drafted {p_name} ({p_pos} | OVR: {p_rating})\n")
            else:
                print(f"{t_name:<30} selects  {p_name:<30} ({p_pos:<3} | OVR: {p_rating})")
    print("The draft has officially concluded")
except FileNotFoundError as e:
    print("Error: Could not find one or more database files!")
    print("Please check that your 'Data/' folder contains all 4 text files.")
    print("Details: {e}")
