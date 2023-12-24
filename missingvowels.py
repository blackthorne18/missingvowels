#!/usr/local/bin/python3.10

# ---------------------------------------------------------------------------------------
# Notes
# time.sleep(2.5) 2.5 seconds
# Numbers for keys
# Escape - 27
# Enter - 10

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# Importing modules and preparing global variables such as file paths
import random
import pickle
import curses
from curses import wrapper
import time
import os
import sys

MAINPATH = './data/'
HIGHSCORE_PATH = MAINPATH + '.highscore'
DBPREFIX = 'db_'
KEYN = {
    'backspace': 127,
    'escape': 27,
    'enter': 10
}
TIMEPERANS = 20
POINTS, LASTPOINT = 0, 0
# ---------------------------------------------------------------------------------------
# 
#
# ---------------------------------------------------------------------------------------
# Prepares (or loads) question set for the No Vowels round from Only Connect
def readyset():
    global questionset, HIGHSCORE
    
    # Caching Proces
    if not os.path.isfile('./data/questionset.p'):
        # If the file .isready does not exist, then program will prepare the questionset
        # from scratc
        dataset = {}
        
        # Gets all files from the MAINPATH with specified DBPREFIX
        # These are the input files to be read
        INPUTDATASETS = []
        for file in list(os.walk(MAINPATH))[0][2]:
            if file.startswith(DBPREFIX):
                INPUTDATASETS.append(file)
        
        # Read all input datasets provided
        for file in INPUTDATASETS:
            with open(f'{MAINPATH}/{file}', 'r') as f:
                dataset[file] = f.read().split('\n')
        
        
        questionset = []
        vowels = ['A', 'E', 'I', 'O', 'U']
        # For each category in the dataset
        for key, val in dataset.items():
            # For each entry in the dataset of a particular category
            for item in val:
                # Remove vowels and rearrange the spaces in the sentence/phrase
                ques = item.replace(" ", "")
                for ch in vowels:
                    ques = ques.replace(ch, '')
                randomspace = random.choices(range(1, len(ques)-1), k=int(len(ques)/4))
                randomspace.sort()
                ques = list(ques)
                for pos, rs in enumerate(randomspace):
                    ques.insert(rs + pos, ' ')
                ques = ''.join(ques)
                ques = ' '.join(ques.split())
                
                # Add to questionset
                category = key.replace(DBPREFIX, '').capitalize()
                questionset.append({'question': ques, 'answer': item, 'category': category})
        
        # Store questionset to pickle file
        pickle.dump(questionset, open(f'{MAINPATH}/questionset.p', 'wb'))
        os.system(f'echo 0 > {HIGHSCORE_PATH}')
    else:
        # If file exists, directly load questionset
        questionset = pickle.load(open(f'{MAINPATH}/questionset.p', 'rb'))
        with open(HIGHSCORE_PATH, 'r') as f:
            HIGHSCORE = int(f.read())
# ---------------------------------------------------------------------------------------
# 
#
# ---------------------------------------------------------------------------------------
# Return x position from string
def getxpos(entry):
    return max(0, int((MAXCOL - len(entry)) * 0.5))
# ---------------------------------------------------------------------------------------
# 
#
# ---------------------------------------------------------------------------------------
# Adding Progress Bar
def showResult(stdscr, quesWin, ansPad, resultnumber, typedAnswer, correctAnswer):
    global POINTS, HIGHSCORE, LASTPOINT
    # Announce Result
    if resultnumber == 1:
        POINTS += 1
        LASTPOINT = POINTS
    else:
        LASTPOINT = POINTS
        if POINTS > HIGHSCORE:
            HIGHSCORE = POINTS
            with open(HIGHSCORE_PATH, 'w+') as f:
                f.write(f'{HIGHSCORE}')
        POINTS = 0
    resultstr = [':(', ':)', ':('][resultnumber]
    whichTense = ['have ended the round on', 'are currently on', 'have ended the round on'][resultnumber]
    highlightAns = ['wrong', 'correct', 'wrong'][resultnumber]
    # Add typedAnswer
    ansPad.clear()
    typedAnswer = f'Your response: {typedAnswer.capitalize()}'
    split_a = typedAnswer.split(':')[0] + ": "
    split_b = typedAnswer.split(':')[1][1:]
    ansPad.addstr(1, getxpos(typedAnswer), split_a, ATTR['intro'] )
    ansPad.addstr(1, getxpos(typedAnswer) + len(split_a), split_b, ATTR[highlightAns] )
    ansPad.refresh()
    # Add correct Answer
    correctAnswer = f'Answer: {correctAnswer.capitalize()}'
    quesWin.addstr(4, getxpos(correctAnswer), correctAnswer, ATTR['title'] )
    # Showing the score
    currentPoints = f'You {whichTense} {LASTPOINT} points ' + resultstr
    quesWin.addstr(10, getxpos(currentPoints), currentPoints, ATTR['intro'] )
    quesWin.refresh()
    # Make next decision
    nextMenu = 'n: Next  q: Exit'
    stdscr.addstr(int(MAXROW * 0.8), getxpos(nextMenu), nextMenu, ATTR['intro'] )
    stdscr.refresh()
    while True:
        try:
            nextmove = chr(stdscr.getch()).lower()
            if nextmove == 'n':
                beginround(stdscr, quesWin)
            elif nextmove == 'q':
                titlescreen(stdscr, quesWin)
        except Exception:
            pass
# ---------------------------------------------------------------------------------------
#
#
# ---------------------------------------------------------------------------------------
# Adding questions each round
def beginround(stdscr, quesWin):
    # Start modifying the screen contents
    stdscr.clear()
    #
    # Add title header
    title_string = ' Missing Vowels Round from Only Connect '
    stdscr.addstr(int(MAXROW * 0.1), getxpos(title_string), title_string, ATTR['title'] )
    stdscr.addstr(int(MAXROW * 0.15), 0, '.'*MAXCOL, ATTR['category'] )
    stdscr.addstr(int(MAXROW * 0.7), 0, '.'*MAXCOL, ATTR['category'] )
    stdscr.refresh()
    #
    roundx = random.choice(questionset)
    # Add category
    quesWin.clear()
    categoryx = 'Category: ' + roundx['category']
    quesWin.addstr(1, getxpos(categoryx), categoryx, ATTR['category'] )
    #
    # Add question
    questionx = roundx['question']
    quesWin.addstr(4, getxpos(questionx), questionx, ATTR['intro'] )
    #
    # Move cursor to newline
    correctAnswer = roundx['answer']
    quesWin.addstr(6, getxpos(''), "")
    quesWin.refresh()
    ansPad = curses.newwin(6, MAXCOL, int(MAXROW * 0.2) + 5, 0)
    # 
    # Get input from user but don't stall the code while waiting
    stdscr.nodelay(True)
    typedAnswer = ""
    start_time = time.time()
    while True:
        userinput = ""
        try:
            userinput = stdscr.getch()
        except Exception:
            pass
        
        # If block begins
        if userinput == KEYN['escape']:
            titlescreen(stdscr, quesWin)
        elif userinput == KEYN['enter']:
            resultnumber = int(typedAnswer.upper() == correctAnswer.upper())
            showResult(stdscr, quesWin, ansPad, resultnumber, typedAnswer, correctAnswer)
        elif userinput >= 0:
            if userinput != KEYN['backspace']:
                typedAnswer += chr(userinput)
            else:
                typedAnswer = typedAnswer[:-1]
        # Initialise answer window
        ansPad.clear()
        #
        # Adding progress bar
        timenow = int(time.time() - start_time)
        if timenow == TIMEPERANS:
            showResult(stdscr, quesWin, ansPad, 2, typedAnswer, correctAnswer)
        progresbar = '[{}{}]'.format('#' * timenow, ' ' * (TIMEPERANS - timenow))
        ansPad.addstr(5, getxpos(progresbar), progresbar)
        #
        # Show current score
        currentPoints = f'Points scored:{POINTS}'
        ansPad.addstr(3, getxpos(currentPoints), currentPoints, ATTR['intro'] )
        #
        # Enter typed answer
        ansPad.addstr(1, getxpos(typedAnswer), typedAnswer, ATTR['intro'] )
        #
        ansPad.refresh()
# ---------------------------------------------------------------------------------------
#
#
# ---------------------------------------------------------------------------------------
# Draw Title Screen
def titlescreen(stdscr, quesWin):
    # Start modifying the screen contents
    stdscr.nodelay(False)
    stdscr.clear()
    #
    # Add title header
    title_string = ' Missing Vowels Round from Only Connect '
    stdscr.addstr(int(MAXROW * 0.1), getxpos(title_string), title_string, ATTR['title'] )
    stdscr.addstr(int(MAXROW * 0.15), 0, '.'*MAXCOL, ATTR['category'] )
    stdscr.addstr(int(MAXROW * 0.7), 0, '.'*MAXCOL, ATTR['category'] )
    points_scored = f'Your highest win streak is {HIGHSCORE} wins.'
    stdscr.addstr(int(MAXROW * 0.8), getxpos(points_scored), points_scored, ATTR['category'] )
    stdscr.refresh()
    #
    # Add intro
    quesWin.clear()
    if LASTPOINT > 0:
        points_scored = f'You were on a {LASTPOINT} point streak last time!'
        quesWin.addstr(10, getxpos(points_scored), points_scored, ATTR['intro'] )
    intro_string = "Hit 's' to start the round or 'q' to exit"
    quesWin.addstr(2, getxpos(intro_string), intro_string, ATTR['intro'] )
    quesWin.addstr(5, getxpos(''), '')
    quesWin.refresh()
    #
    while True:
        userinput = chr(stdscr.getch()).lower()
        if userinput == 's':
            beginround(stdscr, quesWin)
        if userinput == 'q':
            exit()
# ---------------------------------------------------------------------------------------
# 
#
# ---------------------------------------------------------------------------------------
# Entry point for setting up the environment
def main(stdscr):
    global MAXROW, MAXCOL, ATTR, QWROW, QWCOL
    # Prepare and load questionset
    readyset()
    # 
    # Creating global variables to use across functions
    # Defining position and color variables
    # Position variables
    MAXROW, MAXCOL = stdscr.getmaxyx()
    # Color variables
    curses.init_pair(1, 255, 0)
    curses.init_pair(2, 0, 2)
    curses.init_pair(3, 0, 9)
    ATTR = {
        'title': curses.color_pair(1) | curses.A_STANDOUT,
        'intro': curses.color_pair(1),
        'category': curses.color_pair(1) | curses.A_UNDERLINE,
        'correct': curses.color_pair(2),
        'wrong': curses.color_pair(3),
    }
    #
    # Creating the main window where the questions will be displayed
    quesWin = curses.newwin(12, MAXCOL, int(MAXROW * 0.2), 0)
    QWROW, QWCOL = quesWin.getmaxyx()
    #
    # Print title screen
    titlescreen(stdscr, quesWin)
    #
# ---------------------------------------------------------------------------------------
# 
#
# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        wrapper(main)
    except KeyboardInterrupt:
        print('Program killed')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

# ---------------------------------------------------------------------------------------
