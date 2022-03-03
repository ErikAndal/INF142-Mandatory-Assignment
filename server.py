from socket import *
from rich import print
from rich.prompt import Prompt
from rich.table import Table
from champlistloader import load_some_champs
from core import Champion, Match, Shape, Team

serverPort = 8888
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
connectionSocket, addr = serverSocket.accept()

def flip(number):
    number += (1 % 2)
    return number

def input_champion(prompt: str,
                   color: str,
                   champions: dict[Champion],
                   player1: list[str],
                   player2: list[str]) -> None:

    # Prompt the player to choose a champion and provide the reason why
    # certain champion cannot be selected

    while True:
        connectionSocket.send(f'[{color}]{prompt}:'.encode())
        
        match connectionSocket.recv(2048).decode():
            case name if name not in champions:
                connectionSocket.send((f'The champion "{name}" is not available. Try again.').encode())
            case name if name in player1:
                connectionSocket.send((f'{name} is already in your team. Try again.').encode())
            case name if name in player2:
                connectionSocket.send((f'{name} is in the enemy team. Try again.').encode())
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
    connectionSocket.send((f'Red: {red_score}\n'
          f'Blue: {blue_score}').encode())

    # Print the winner
    if red_score > blue_score:
        connectionSocket.send(('\n[red]Red victory! :grin:').encode())
    elif red_score < blue_score:
        connectionSocket.send(('\n[blue]Blue victory! :grin:').encode())
    else:
        connectionSocket.send(('\nDraw :expressionless:').encode())


def main() -> None:

    
    #sentence = connectionSocket.recv(2048).decode()
    #newSentence = sentence
    #connectionSocket.send(newSentence.encode())
    #connectionSocket.close()
    
    player1 = []
    player2 = []

    champions = load_some_champs()

    # Champion selection
    for _ in range(2):
        input_champion('Player 1', 'red', champions, player1, player2)
        input_champion('Player 2', 'blue', champions, player2, player1)

    print('\n')

    # Match
    match = Match(
        Team([champions[name] for name in player1]),
        Team([champions[name] for name in player2])
    )
    match.play()

    # Print a summary
    print_match_summary(match)


if __name__ == '__main__':
    main()

