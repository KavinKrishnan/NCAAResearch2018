import os
import csv
import pathlib


def getDuplicates(folder_year):
    # Lists to be appended
    duplicates = []
    teamList = []

    # Get name of all csv files in each subdirectory
    for path, subdirs, files in os.walk('.'):

        for name in files:
            name = str(pathlib.PurePath(name))
            awayTeam = name.split('_')[0]
            homeTeam = (name.split('_')[-1]).split('.')[0]
            teamList.append((awayTeam, homeTeam))

    for teams in teamList:
        try:
            # Checks if times played home and away
            if (teams[1], teams[0]) in teamList:

                # Extract data from both games
                with open(os.path.join('./' + folder_year + '/' + teams[0] + '/away/',teams[0] + '_At_' + teams[1] + '.csv'), 'rt') as csvin:
                    game1 = [row for row in csv.reader(csvin)]
                    margin1 = int(game1[-1][3]) - int(game1[-1][2])
                    possessions1 = len([row[7] for row in game1 if ("made" or "Defensive Rebound" or "Turnover") in row[7]])

                with open(os.path.join('./' + folder_year + '/' + teams[1] + '/away/',teams[1] + '_At_' + teams[0] + '.csv'), 'rt') as csvin:
                    game2 = [row for row in csv.reader(csvin)]
                    margin2 = int(game2[-1][3]) - int(game2[-1][2])
                    possessions2 = len([row[7] for row in game2 if ("made" or "Defensive Rebound" or "Turnover") in row[7]])

                gameData = [teams[0], teams[1], margin1, -margin2, possessions1, possessions2, margin1/possessions1, margin2/possessions2]
                if gameData not in duplicates:
                    print(gameData)                    
                    duplicates.append(gameData)
        except:
            pass

    return duplicates

# Write list to csv file
def write_to_csv(fname, margin_list):

    with open(fname, 'w', newline='') as fout:
        csvout = csv.writer(fout, delimiter=',', quotechar='"')
        csvout.writerow(["Team 1", "Team 2", "Margin 1", "Margin 2", "Possessions 1", "Possessions 2", "M/P 1", "M/P 2"])
        csvout.writerows(margin_list)
    
write_to_csv("Margins_Per_Possession.csv", getDuplicates('2017'))














