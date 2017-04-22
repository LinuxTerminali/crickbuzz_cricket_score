# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, Comment
import schedule
import time
from terminaltables import AsciiTable
from termcolor import colored, cprint
import sys
import os

# Method to visit home page of cricbuzz and get urls of matches


def get_list_of_Matches():
    r = requests.get("http://www.cricbuzz.com/")
    soup = BeautifulSoup(r.text, 'html.parser')
    global list_matches
    list_matches = soup.find_all(
        'div', {'class': 'cb-col cb-col-25 cb-mtch-blk'})
    return get_scorecard_fromlist()
  # print(f['href'])


# method to loop through all the matches returned by get_list_of_Matches() method
def get_scorecard_fromlist():
    # print(s)
    global url
    global s
    i = 0
    previous_text = ''
    while(i != len(list_matches)):
        s = list_matches[i].find_all('a', href=True)
        # print(s)
        url = "http://www.cricbuzz.com/" + s[0]['href']
        r = requests.get(url)
        # print(url)
        global soup
        soup = BeautifulSoup(r.text, 'html.parser')
        # print(soup.find_all('div', {'class': 'cb-min-bat-rw'}))
        # print(get_live_Status())
        if(get_live_Status()):
            live_game()
            # finished()
        else:
            finsihed_game()
        i += 1
    print(colored("\n \n====================================================================================================", "green"))
    print(colored("       That's it we have, Probably no more live games available right now try again letter", "red"))
    print(colored("=====================================================================================================", "green"))

    quit()


# method used after scheduling to get  latest score updates
def refresh_Scorecard():
    r = requests.get(url)
    global soup
    soup = BeautifulSoup(r.text, 'html.parser')
    get_match_status()
    for item in soup.find_all('div', {'class': 'cb-min-bat-rw'}):
        text = item.text
        if "CRR:" in text:
            check_for_wicket(text)
            print_match_summary(text)
        else:
            print(text)
            get_list_of_Matches()


def finished():
    finished = soup.find_all('div', {'class': 'cb-col cb-col-100 cb-min-stts cb-text-mom'})
    if(len(finished) == 0):
        finished = soup.find_all('div', {'class': 'cb-text-complete'})
    return finished[0].text

# method to get recent balls and runs on that balls


def recent_diliveris():
    # print(soup)
    recent_balls = soup.find_all('div', attrs={'class': 'cb-col cb-col-100 cb-font-12 cb-text-gray cb-min-rcnt'})
    # print(recent_balls)
    # print(soup)
    # recent_balls[0].span.clear()
    # print(recent_balls[0].get_text())
    try:
        recent_ball = recent_balls[0].text
        recent_ball = recent_ball.strip('Recent: ')
    except IndexError:
        recent_ball = ' '
    return recent_ball



#method to get crrent batsman and bowler

def get_current_bastman_bowler():
    batsman_1 = ' '
    batsman_2 = ' '
    bowler_1 = ' '
    bowler_2 = ' '
    items = soup.find_all('div', {'class': 'cb-col cb-col-100 cb-min-itm-rw'})
    class01 = {'class': 'cb-col cb-col-10 ab text-right'}
    class02 = {'class': 'cb-col cb-col-10 text-right'}
    class03 = {'class': 'cb-col cb-col-8 text-right'}
    class04 = {'class': 'cb-col cb-col-50'}
    if(len(items) == 4):
        batsman_1 = items[0].find_all('div', class04)[0].text
        batsman_1 += " " + items[0].find_all('div', class01)[0].text
        batsman_1 += "(" + items[0].find_all('div', class01)[1].text + ")"

        batsman_2 = items[1].find_all('div', class04)[0].text
        batsman_2 += " " + items[1].find_all('div', class01)[0].text
        batsman_2 += "(" + items[1].find_all('div', class01)[1].text + ")"

        bowler_1 = items[2].find_all('div', class04)[0].text
        bowler_1 += " " + items[2].find_all('div', class02)[0].text
        bowler_1 += " " + items[2].find_all('div', class02)[1].text
        bowler_1 += " " + items[2].find_all('div', class03)[1].text

        bowler_2 = items[3].find_all('div', class04)[0].text
        bowler_2 += " " + items[3].find_all('div', class02)[0].text
        bowler_2 += " " + items[3].find_all('div', class02)[1].text
        bowler_2 += " " + items[3].find_all('div', class03)[1].text
        # print(batsman_1,batsman_2,bowler_1,bowler_2)
    elif(len(items)) == 3:
        batsman_1 = items[0].find_all('div', class04)[0].text
        batsman_1 += " " + items[0].find_all('div', class01)[0].text
        batsman_1 += "(" + items[0].find_all('div', class01)[1].text + ")"

        bowler_1 = items[1].find_all('div', class04)[0].text
        bowler_1 += " " + items[1].find_all('div', class02)[0].text
        bowler_1 += " " + items[1].find_all('div', class02)[1].text
        bowler_1 += " " + items[1].find_all('div', class03)[1].text

        bowler_2 = items[2].find_all('div', class04)[0].text
        bowler_2 += " " + items[2].find_all('div', class02)[0].text
        bowler_2 += " " + items[2].find_all('div', class02)[1].text
        bowler_2 += " " + items[2].find_all('div', class03)[1].text

    return batsman_1, batsman_2, bowler_1, bowler_2

# method to get status of the match ex innings break, stumps or rain or how much runs needed


def get_match_status():
    # print(soup)
    try:
        match_Status = []
        tags = ['cb-text-inprogress', 'cb-text-lunch', 'cb-text-stump',
                'cb-text-innings break', 'cb-text-rain', 'cb-text-tea',
                'cb-text-badlight']
        i = 0
        while(len(match_Status) == 0):
            # print(tags[i])
            if(len(tags) != i):
                match_Status = soup.find_all('div', {'class': tags[i]})
                i += 1
            else:
                break
        status = match_Status[0].text
    except IndexError:
        status = " "

    # print(match_Status)

    return status

# method called by get_scorecard_fromlist() to print the data in a tabular form


def print_match_summary(t):
    # print(soup)
    # print(soup.find_all('div', {'class': 'cb-text-stump'}))
    first_inings = soup.find('div', {'class': 'cb-text-gray cb-font-16'})
    # print()
    if(first_inings == None):
        first_ining_score = " "
    else:
        first_ining_score = first_inings.text
    current_batsman_bowler = get_current_bastman_bowler()
    batsmans = current_batsman_bowler[0] + "\n" + current_batsman_bowler[1]
    bowler = current_batsman_bowler[2] + "\n" + current_batsman_bowler[3]
    # print(batsmans)
    ongoing_data = [[colored('Match', 'green'),
                     colored('Status', 'green'),
                     colored('Recent balls', 'green'),
                     colored('Batsmans R  B', 'green'),
                     colored('Bowlers O R W', 'green')],
                    [colored(first_ining_score + t, 'yellow'),
                     colored(get_match_status(), 'white'),
                     colored(recent_diliveris(), 'magenta'),
                     colored(batsmans, 'yellow'),
                     colored(bowler, 'yellow')]
                    ]
    table = AsciiTable(ongoing_data)
    print(table.table)
    if("Innings Break" in get_match_status()):
        global wicket_count
        wicket_count = 0
        print(colored("Take a Coffee meanwhile or check others it's a Innings break here", "red"))
        cancel_scedule()
        get_list_of_Matches()
    elif("Stump" in get_match_status()):
        wicket_count = 0
        cancel_scedule()
        get_list_of_Matches()
    elif("stopped" in get_match_status()):
        wicket_count = 0
        cancel_scedule()
        get_list_of_Matches()

# get the status of the match weather it is live or finished


def get_live_Status():
    live_ = soup.find_all('div', {'class': 'cb-min-bat-rw'})
    # print(live_)
    if(len(live_) == 0):
        # print(finsihed_game)
        finished_g = soup.find_all(
            'div', {'class': 'cb-col cb-col-100 cb-min-tm cb-text-gray'})
        return False
    return True

# method used to get data and print if match is live


def live_game():
    for item in soup.find_all('div', {'class': 'cb-min-bat-rw'}):
        text = item.text
        global seen_matches
        if "CRR:" in text:
            if(not(text in seen_matches)):
                seen_matches = seen_matches+ " " +text

                print_match_summary(item.text)
            # print(item.text)
                # print(user_input())
                if(user_input()):
                    # print("refresh_Scorecard")

                    getplayingeleven()
                    schedule_match()
                    return refresh_Scorecard()
                else:
                    break
            else:
                break
        else:
            # print(seen_matches)
            if(not(text in seen_matches)):
                seen_matches = seen_matches + " " + text
                finished_data = [[colored('Match', 'green'),
                                  colored('Status', 'green'),
                                  colored('Result', 'green')],
                                 [colored(text, 'yellow'),
                                  colored("Finished", 'red'),
                                  colored(finished(), 'magenta')]
                                 ]
                table = AsciiTable(finished_data)
                print(table.table)
                break

# method to used to get data and print if match is finished


def finsihed_game():
    for item in soup.find_all('div', {'class': 'cb-col cb-col-100 cb-min-tm cb-text-gray'}):
        text = item.text
        if "CRR:" in text:
            print_match_summary(item.text)
            # print(item.text)
            keep_checking = int(input('Wanna keep check on this Press 1'))
            if(keep_checking == 1):
                schedule_match()
                return refresh_Scorecard()
            else:
                # print(list_matches)
                break
        else:
            global seen_matches
            # print(seen_matches)
            if(not(text in seen_matches)):
                seen_matches = seen_matches + " " + text
                previous_text = text
                finished_data = [[colored('Match', 'green'),
                                  colored('Status', 'green'),
                                  colored('Result', 'green')],
                                 [colored(text, 'yellow'),
                                  colored("Finished", 'red'),
                                  colored(finished(), 'magenta')]
                                 ]
                table = AsciiTable(finished_data)
                print(table.table)
                break

# method used while scheduling to check if a wicket is fall it will notify
# by playing audio


def check_for_wicket(text):
    try:
        text = text.split('/')
        # print(text)
        text = text[1].split()
        new_wicket_count = text[0]
        global wicket_count
        global first_time
        if(first_time):
            wicket_count = new_wicket_count
            first_time = False
        elif(new_wicket_count != wicket_count):
            wicket_count = new_wicket_count
            os.system("aplay out.wav")
    except IndexError:
        print('A Wicket might have fall')
    except IOError:
        print('A Wicket might have fall')
    except KeyboardInterrupt:
        quit()

    # print("do something")

    # print(bea_soup)

# method used to get the todays playing eleven for both the team


def getplayingeleven():
    scorecard_url = url.replace('scores', 'scorecard')
    re = requests.get(scorecard_url)
    scorecard_soup = BeautifulSoup(re.text, 'html.parser')
    print(colored(scorecard_soup.find('div', {
          'class': 'cb-col cb-scrcrd-status cb-col-100 cb-text-live'}).text, "green"))
    rr = scorecard_soup.find_all(
        'div', {'class': 'cb-col cb-col-100 cb-minfo-tm-nm'})
    ss = scorecard_soup.find_all(
        'div', {'class', 'cb-col cb-col-100 cb-minfo-tm-nm cb-minfo-tm2-nm'})
    # print(len(rr))
    try:
        if(len(rr) == 5):
            print(colored(rr[0].text.replace("Squad", ": "), 'green'), colored(
                "Today's " + rr[1].text, 'white'))
            print(colored("On " + rr[2].text, 'red'))
            print(" ")
            print(colored(ss[0].text.replace("Squad", " : "),
                          "green"), colored("Today's " + rr[3].text, 'white'))
            print(colored("On " + rr[4].text, 'red'))
        elif(len(rr) == 4):
            print(colored(rr[0].text.replace("Squad", ": "), 'green'), colored(
                "Today's " + rr[1].text, 'white'))
            print(" ")
            print(colored(ss[0].text.replace("Squad", " : "),
                          "green"), colored("Today's " + rr[3].text, 'white'))
    except IndexError:
        print('Unable to get the Playing XI')
    except KeyboardInterrupt:
        quit()
    '''for squad in range(len(rr)):
    print(rr[squad].text)
  for ss in scorecard_soup.find_all('div', {'class','cb-col cb-col-100 cb-minfo-tm-nm cb-minfo-tm2-nm'}):
     print(ss.text)'''
    # print(scorecard_soup.find('div', {'class': 'cb-col cb-col-73'}))
    # print(scorecard_soup.find('div', {'class': 'cb-col cb-col-100 cb-minfo-tm-nm'}))
    # print(scorecard_soup)

# method used to take user input


def user_input():
    try:
        while(True):
            keep_checking = int(input('Wanna keep check on this Press 1'))
            if(keep_checking == 1):
                # print('true')
                return True
            else:
                # print("false")
                return False
    except ValueError:
                # print("Please press 1 to continue or any other number to move ahead")
        return False
    except KeyboardInterrupt:
        quit()

# method used to schedule the match


def schedule_match():
    try:
        schedule.every(30).seconds.do(refresh_Scorecard).tag('score_updates', 'task')
        while 1:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        quit()

# method used to cancel the schedule match


def cancel_scedule():
    schedule.clear('score_updates')

# a method containing ascii art


def asciiart():
    art1 = """
                                   _      _        _
                                  (_)    | |      | |
                          ___ _ __ _  ___| | _____| |_
                         / __| '__| |/ __| |/ / _ \ __|
                        | (__| |  | | (__|   <  __/ |_
                         \___|_|  |_|\___|_|\_\___|\__|
                        """
    art2 = """
          --------------------------------------------------------------------------

          @                               _                                  ,,
           \\   _   @'                    ( )_                       .      _  \\
            \\_( )_//                    / Y |                   .      /--( )_//
              | Y/--                    /\   /               .        '//  \~ \
              |_/       _ / o"         ( _\ /            .                   - \
            _ //\      | | |    .       \_\\\        .                     //  \\--,
           /_// /      | | |      .    / \ \\\ .                           \\
          / // /_______|_|_|__________/_/_\ \_______________________________\\______
          -------------------------------------------- Play Cricket ----------------
                   """
    print(art1)
    print(art2)


if __name__ == "__main__":
    try:
        print(colored("==================================================================================================", 'green'))
        print(
            colored("                              #Live Cricket Score Tracker#", 'yellow'))
        print(colored("==================================================================================================", 'green'))
        asciiart()
        print(colored(
            "\n                 #1) If a Live Match is avialable you will get a option to follow it  ", "red"))
        print(colored(
            "\n                 #2) Choosen Match score will get update after every 30 seconds", 'red'))
        print(colored(
            "\n                 #3) if a wicket falls it will notify you so put your headphones on", 'red'))
        print(colored(
            "                            Powerd by http://www.cricbuzz.com/", "green"))
        print(colored(
            "                            Ascii Art by http://ascii.co.uk/art/cricket", "green"))
        print(colored('\n                              Created by LinuxTerminali', 'green'))
        first_time = True
        wicket_count = 0
        seen_matches = " "
        url = ' '
        s = ''
        soup = ''
        list_url = []
        list_matches = []
        get_list_of_Matches()
    except KeyboardInterrupt:
        quit()
