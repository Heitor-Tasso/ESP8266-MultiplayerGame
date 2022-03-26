import socket

ip = "192.168.4.2"
gateway = "192.168.4.1"
port = 80

def setState(state):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((gateway, port))
    s.sendall(f'{state}\n'.encode('utf-8'))
    s.close()

for i in range(6):
    setState(f'Numero {i}')
