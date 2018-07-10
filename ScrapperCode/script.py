import re
import requests
import time
import os
import sys
import unidecode
from bs4 import BeautifulSoup


# Default year
folder_year = "2016"

# Type in year with script to scrape a different year
if (len(sys.argv) > 1):
    folder_year = sys.argv[1]

# Creates standings link based on year
standings = requests.get("http://www.espn.com/mens-college-basketball/standings/_/season/" + folder_year)

half_time = 20 #in minutes

# Scrapes gameflow in url given by parameter link and writes to file of team specified by the abbrev parameter
def scrapeGameFlow(link, abbrev):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')
    # print soup.prettify()

    # Get HTML of gameflow for the first half of the game
    firstHalf_gflow = soup.find("div", {"id": "gp-quarter-1"})

    if not firstHalf_gflow:
        return -999

    # Get team abreviations
    teams = soup.find_all("div", {"class": "competitors"})
    awayAbr = unidecode.unidecode(teams[0].find("div", {"class": "team away"}).find("span", {"class": "abbrev"}).text)
    homeAbr = unidecode.unidecode(teams[0].find("div", {"class": "team home"}).find("span", {"class": "abbrev"}).text)

    # Variable for file to eventually write to
    fileToWrite = None

    # Get team city and create file name from them
    away = unidecode.unidecode(teams[0].find("div", {"class": "team away"}).find("span", {"class": "long-name"}).text)
    home = unidecode.unidecode(teams[0].find("div", {"class": "team home"}).find("span", {"class": "long-name"}).text)

    filename = away + "_At_" + home

    # Place file depending on whether home or away team
    if (awayAbr == abbrev):
        if not os.path.exists("./" + folder_year + "/" + away):
            os.makedirs("./" + folder_year + "/" + away + "/home")
            os.makedirs("./" + folder_year + "/" + away + "/away")
        filename = open("./" + folder_year + "/" + away + "/away/" + filename + ".csv", "w+")

    else:
        if not os.path.exists("./" + folder_year + "/" + home):
            os.makedirs("./" + folder_year + "/" + home + "/home")
            os.makedirs("./" + folder_year + "/" + home + "/away")
        filename = open("./" + folder_year + "/" + home + "/home/" + filename + ".csv", "w+")

    # Create .csv headers
    filename.write("Away Team,Home Team,Away Score,Home Score,Minute,Second,isScoringPosession,Desc.\n")

    # Getting the actual rows of the table displaying possessions
    firstHalf_possRows = firstHalf_gflow.find("table").find_all("tr")
    firstHalf_possRows .pop(0)  #popped the first row because it was simply displaying the labels for the columns

    # Scrapped Possessions as list of tuples (Away Team Score, Home Team score, Time left in half, Scoring Play)
    firstHalf_scraped = []

    for pos in firstHalf_possRows:

        # See if it is scoring possession (signified by having a class attribute, otherwise it would not have one)
        scoring = 0
        if pos.has_attr('class'):
            scoring = 1


        # Get time stamp of row
        sTime = unidecode.unidecode(pos.find("td",{"class": "time-stamp"}).text)

        # Adjust to count up from 00:00 to 48:00
        parsedTime = time.strptime(sTime, "%M:%S")
        parseMin = parsedTime.tm_min
        parseSec = parsedTime.tm_sec + (60 * parseMin)
        parseSec = (half_time * 60) - parseSec
        newMin = parseSec / 60
        newSec = parseSec % 60

        # Get Combined score in form of 'away - home' and regex to parse individual score
        combinedScore = unidecode.unidecode(pos.find("td",{"class": "combined-score"}).text)
        awayScore = re.search(r'(\d*)\s*-\s*', combinedScore).groups()[0]
        homeScore = re.search(r'\d*\s*-\s*(\d*)', combinedScore).groups()[0]

        # Get possesion details of row
        details = (pos.find("td", {"class": "game-details"}).text).encode('ascii','ignore')


        # Add to list as tuple
        firstHalf_scraped.append((away, home, awayScore, homeScore, newMin, newSec, scoring, details))
        filename.write(
            away + "," + home + "," + awayScore + "," + homeScore + "," + str(newMin) + "," + str(newSec) + "," + str(scoring) + "," + details + "\n")



    # Get HTML of gameflow for the second half of the game
    secondHalf_gflow = soup.find("div", {"id": "gp-quarter-2"})

    if(secondHalf_gflow is not None):
        # Getting the actual rows of the table displaying possessions
        secondHalf_possRows = secondHalf_gflow.find("table").find_all("tr")
        secondHalf_possRows.pop(0)  # popped the first row because it was simply displaying the labels for the columns

        # Scrapped Possessions as list of tuples (Away Team Score, Home Team score, Time left in half, Scoring Play)
        secondHalf_scraped = []

        for pos in secondHalf_possRows:

            # See if it is scoring possession (signified by having a class attribute, otherwise it would not have one)
            scoring = 0
            if pos.has_attr('class'):
                scoring = 1

            # Get time stamp of row
            sTime = unidecode.unidecode(pos.find("td", {"class": "time-stamp"}).text)
            parsedTime = time.strptime(sTime, "%M:%S")

            # Adjust to count up from 00:00 to 48:00
            parsedTime = time.strptime(sTime, "%M:%S")
            parseMin = parsedTime.tm_min
            parseSec = parsedTime.tm_sec + (60 * parseMin)
            parseSec = (half_time * 60) - parseSec
            newMin = half_time + (parseSec / 60)
            newSec = parseSec % 60

            # Get Combined score in form of 'away - home' and regex to parse individual score
            combinedScore = unidecode.unidecode(pos.find("td", {"class": "combined-score"}).text)
            awayScore = re.search(r'(\d*)\s*-\s*', combinedScore).groups()[0]
            homeScore = re.search(r'\d*\s*-\s*(\d*)', combinedScore).groups()[0]

            # Get possesion details of row
            details = (pos.find("td", {"class": "game-details"}).text).encode('ascii', 'ignore')


            # Add to list as tuple
            secondHalf_scraped.append((away, home, awayScore, homeScore, newMin, newSec, scoring, details))
            filename.write(
                away + "," + home + "," + awayScore + "," + homeScore + "," + str(newMin) + "," + str(newSec) + "," + str(scoring) + "," + details + "\n")
    else:
        print "no second half" + link


    # Just for debugging purposes to add a breakpoint
    filename.close()


def scrapeBoxScore(link, abbrev):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get team abreviations
    teams = soup.find_all("div", {"class": "competitors"})

    if not teams:
        return

    awayAbr = str(teams[0].find("div", {"class": "team away"}).find("span", {"class": "abbrev"}).text)
    homeAbr = str(teams[0].find("div", {"class": "team home"}).find("span", {"class": "abbrev"}).text)

    # Variable for file to eventually write to
    fileToWrite = None

    # Get team city and create file name from them
    away = str(teams[0].find("div", {"class": "team away"}).find("span", {"class": "long-name"}).text)
    home = str(teams[0].find("div", {"class": "team home"}).find("span", {"class": "long-name"}).text)

    filename = away + "_At_" + home

    # Place file depending on whether home or away team
    if (awayAbr == abbrev):
        if not os.path.exists("./" + folder_year + "/" + away):
            os.makedirs("./" + folder_year + "/" + away + "/home")
            os.makedirs("./" + folder_year + "/" + away + "/away")
        filename = open("./" + folder_year + "/" + away + "/away/" + filename + "_BOX.csv", "w+")

    else:
        if not os.path.exists("./" + folder_year + "/" + home):
            os.makedirs("./" + folder_year + "/" + home + "/home")
            os.makedirs("./" + folder_year + "/" + home + "/away")
        filename = open("./" + folder_year + "/" + home + "/home/" + filename + "_BOX.csv", "w+")

    filename.write(home + "," + away + ",totalRebounds,totalOffensive,totalDefensive,totalturnovers\n")

    # Home and Away score
    awayScore = unidecode.unidecode(soup.find("div", {"class": "score icon-font-after"}).text)
    homeScore = unidecode.unidecode(soup.find("div", {"class": "score icon-font-before"}).text)

    reboundTest = soup.find("tr", {"data-stat-attr": "totalRebounds"})
    if not reboundTest:
        return

    totalReboundsRow = reboundTest.find_all("td")
    awayTotalRebounds = int(unidecode.unidecode(totalReboundsRow[1].text).strip())
    homeTotalRebounds = int(unidecode.unidecode(totalReboundsRow[2].text).strip())
    totalRebounds = awayTotalRebounds + homeTotalRebounds

    totalReboundsRow = soup.find("tr", {"data-stat-attr": "offensiveRebounds"}).find_all("td")
    awayTotalRebounds = int(unidecode.unidecode(totalReboundsRow[1].text).strip())
    homeTotalRebounds = int(unidecode.unidecode(totalReboundsRow[2].text).strip())
    totalOffRebounds = awayTotalRebounds + homeTotalRebounds

    totalReboundsRow = soup.find("tr", {"data-stat-attr": "defensiveRebounds"}).find_all("td")
    awayTotalRebounds = int(unidecode.unidecode(totalReboundsRow[1].text).strip())
    homeTotalRebounds = int(unidecode.unidecode(totalReboundsRow[2].text).strip())
    totalDefRebounds = awayTotalRebounds + homeTotalRebounds

    totalTurnoversRow = soup.find("tr", {"data-stat-attr": "totalTurnovers"}).find_all("td")
    awayTotalTurnovers = int(unidecode.unidecode(totalTurnoversRow[1].text).strip())
    homeTotalTurnovers = int(unidecode.unidecode(totalTurnoversRow[2].text).strip())
    totalTurnovers = awayTotalTurnovers + homeTotalTurnovers

    filename.write(awayScore + "," + homeScore + "," + str(totalRebounds) + "," + str(totalOffRebounds) + "," + str(totalDefRebounds) + "," + str(totalTurnovers) + "\n")

    # Just for debugging purposes to add a breakpoint
    filename.close()


# Create folder for year of results
if not os.path.exists("./" + folder_year):
    os.makedirs("./" + folder_year)


#Section of code that goes through teams in standings of given year and parses each game log
standingSoup = BeautifulSoup(standings.content, 'html.parser')
standingTeams = standingSoup.find_all("tr", {"class": "Table2__tr Table2__tr--sm Table2__even"})
for sTeam in standingTeams:
    abbrev = sTeam.find("abbr")
    linkBlock = sTeam.find("a")
    if hasattr(linkBlock, 'href'):
        link = str(linkBlock.get("href"))

        # Get id of team
        id = re.search(r'id\/(\d*)', link).groups()[0]

        # Open team schedule based on team id and folder year
        schedLink = "http://www.espn.com/mens-college-basketball/team/schedule/_/id/" + id +"/year/" + folder_year
        schedReq = requests.get(schedLink)
        scheduleSoup = BeautifulSoup(schedReq.content, 'html.parser')
        gameFlows = scheduleSoup.find_all("li", {"class": "score"})

        # Call scrapeGameFlow function on each gameflow link
        for gF in gameFlows:
            flowLink = gF.find("a")
            if hasattr(flowLink, 'href'):
                flow = str(flowLink.get("href"))

                # Gets game id from href link
                gameId = re.search(r'gameId\/(\d*)', flow).groups()[0]

                # Link of playbyplay/gameflow page
                linkToScrape = "http://www.espn.com/mens-college-basketball/playbyplay?gameId=" + gameId
                flowExists = scrapeGameFlow(linkToScrape, str(abbrev.text))
                if (flowExists == -999):
                    linkToBoxScrape = "http://www.espn.com/mens-college-basketball/matchup?gameId=" + gameId
                    scrapeBoxScore(linkToBoxScrape, str(abbrev.text))


# scrapeGameFlow("http://www.espn.com/mens-college-basketball/playbyplay?gameId=400916310", "IDHO")


# Just for debugging purposes to add a breakpoint
print











