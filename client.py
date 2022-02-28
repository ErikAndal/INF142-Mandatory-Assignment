from socket import *
serverName = 'localhost'
serverPort = 8888
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sentence = input('send message:')
clientSocket.send(sentence.encode)
modifiedSentence = clientSocket.recv(2048)
print('From server: ', modifiedSentence.decode())
clientSocket.close()