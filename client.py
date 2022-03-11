from selectors import DefaultSelector
from socket import *
from rich import print
from rich.table import Table
#from Server import DISCONNECT_MESSAGE
from champlistloader import load_some_champs
from core import Champion, Match, Shape
import pickle

sock = socket()
server_address = ("localhost", 8888)
sock.connect(server_address)

def print_match_summary(match: Match) -> None:

    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    # For each round print a table with the results
    for index, round in enumerate(match.rounds):

        # Create a table containing the results of the round
        round_summary = Table(title=f'Round {index+1}')

        # Add columns for each team
        round_summary.add_column("Red",
                                 style="red",
                                 no_wrap=True)
        round_summary.add_column("Blue",
                                 style="blue",
                                 no_wrap=True)

        # Populate the table
        for key in round:
            red, blue = key.split(', ')
            round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                  f'{blue} {EMOJI[round[key].blue]}')
        print(round_summary)
        print('\n')

    # Print the score
    red_score, blue_score = match.score
    print((f'Red: {red_score}\n'
          f'Blue: {blue_score}'))

    # Print the winner
    if red_score > blue_score:
        print(('\n[red]Red victory! :grin:'))
    elif red_score < blue_score:
        print(('\n[blue]Blue victory! :grin:'))
    else:
        print(('\nDraw :expressionless:'))

def print_available_champs(champions: dict[Champion]) -> None:

    # Create a table containing available champions
    available_champs = Table(title='Available champions')

    # Add the columns Name, probability of rock, probability of paper and
    # probability of scissors
    available_champs.add_column("Name", style="cyan", no_wrap=True)
    available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
    available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
    available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

    # Populate the table
    for champion in champions.values():
        available_champs.add_row(*champion.str_tuple)

    print(available_champs)

def makeAndPrintMatchObject(sentence):
    str = pickle.loads(sentence)
    print_match_summary(str)

def makeAndPrintChampions(sentence):
    print('inside makeAndPrintChampions ')
    champions = pickle.loads(sentence)
    print('\n'
    'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
    '\n'
    'Each player choose a champion each time.'
    '\n')

    print('\n')

    print_available_champs(champions)

    print('When prompted: Enter champion name followed by Return')


while True:
    new_sentence = sock.recv(1024).decode('utf-8', 'ignore')

    if new_sentence == 'incomming match summary':
        sentence = sock.recv(1024)
        makeAndPrintMatchObject(sentence)
        sock.close()
        break

    if new_sentence == 'incomming database from server':
        database = sock.recv(1024)
        print('database: ', database)
        makeAndPrintChampions(database)
        new_sentence = sock.recv(1024).decode()

    print(new_sentence)
    sentence = input('')
    sock.send(sentence.encode())
    
