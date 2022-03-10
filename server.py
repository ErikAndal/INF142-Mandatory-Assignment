from socket import *
from rich import print
from rich.table import Table
from database import load_some_champs
from core import Champion, Match, Shape, Team
from selectors import EVENT_READ, DefaultSelector
import time
import pickle

sel = DefaultSelector()
sock = socket()
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind(('localhost', 8888))
sock.listen()
sock.setblocking(False)
sel.register(sock, EVENT_READ, True)

# List for connections
socketList = []

def accept(sock):
    conn, address = sock.accept()
    print('accepted', conn, 'from', address)
    conn.setblocking(False)
    socketList.append(conn)
    sel.register(conn, EVENT_READ)
    # This ensures that at least two connections are in socketList
    if len(socketList) >= 2:
        main()
    

def read(conn):
    data = conn.recv(1024)
    if data:
        sentence = data.decode()
        print(sentence)
        conn.send(sentence.encode())

    else:
        print('Closing', conn)
        sel.unregister(conn)
        conn.close()


def input_champion(prompt: str,
                   color: str,
                   champions: dict[Champion],
                   player1: list[str],
                   player2: list[str], sock) -> None:

    # Prompt the player to choose a champion and provide the reason why
    # certain champion cannot be selected
    
    while True:
        # Open for blocking, else I get: "BlockingIOError: [Errno 35] Resource temporarily unavailable"
        sock.setblocking(True)

        sock.send(f'[{color}]{prompt}:\r'.encode())

        match sock.recv(1024).decode():
            case name if name not in champions:
                sock.send((f'The champion "{name}" is not available. Try again.\n').encode())
            case name if name in player1:
                sock.send((f'{name} is already in your team. Try again.\n').encode())
            case name if name in player2:
                sock.send((f'{name} is in the enemy team. Try again.\n').encode())
            case _:
                player1.append(name)
                break


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


def main() -> None:

    print('game running..')

    player1 = []
    player2 = []

    champions = load_some_champs()

    # Champion selection
    for _ in range(2):
        input_champion('Player 1', 'red', champions, player1, player2, socketList[0])
        input_champion('Player 2', 'blue', champions, player2, player1, socketList[1])
        
    # Match
    match = Match(
        Team([champions[name] for name in player1]),
        Team([champions[name] for name in player2])
    )
    match.play()

    # Print a summary to clients
    socketList[0].send('incomming match summary'.encode())
    socketList[1].send('incomming match summary'.encode())

    # To avoid match summary from being displayed the wrong way
    time.sleep(1)
    
    # pickle match
    msg = pickle.dumps(match)
    
    # Send pickled objects to the two clients
    socketList[0].send(msg)
    socketList[1].send(msg)

    # Clear socketList such that game is rerunnable
    socketList.clear()


while True:
    events = sel.select()
    for key, _ in events:
        if key.data:
            accept(key.fileobj)
        else:
            read(key.fileobj)