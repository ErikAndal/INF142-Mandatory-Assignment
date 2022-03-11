import time
from core import Champion
from selectors import DefaultSelector
from socket import *
from rich import print
from rich.table import Table
from core import Champion, Match, Shape
import pickle

def _parse_champ(champ_text: str) -> Champion:
    name, rock, paper, scissors = champ_text.split(sep=',')
    return Champion(name, float(rock), float(paper), float(scissors))


def from_csv(filename: str) -> dict[str, Champion]:
    champions = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            champ = _parse_champ(line)
            champions[champ.name] = champ
    return champions


def load_some_champs():
    return from_csv('some_champs.txt')


sock = socket()
server_address = ("localhost", 8888)
sock.connect(server_address)

def sendDatabase():
    championsToSend = load_some_champs()
    msg = pickle.dumps(championsToSend)
    sock.send('incomming database from database'.encode())
    time.sleep(1)

    sock.send(msg)
    print('picled object sent form database')



while True:
    new_sentence = sock.recv(1024).decode('utf-8', 'ignore')
    if new_sentence == 'send database':
        print('DATABASEDATABASEDATABASEDATABASEDATABASEDATABASE')
        sendDatabase()
        break

    print(new_sentence)
    sentence = input('')
    sock.send(sentence.encode())
    
