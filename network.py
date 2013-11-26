import socket, hashlib, select

def receiveCommand(socketList, loop=True):
	messages = check = []
    while loop:
        for socket in socketList:
            readable, writable, err = select.select([socket.fileno()], [], [], 0.1)
            if readable:
				messages = clientsocket.recv(4096).split('|')
				while messages.count('') > 0:
					messages.remove('')
				for i in range(0, len(messages)):
					if i % 2 == 1:
						check.append(messages.pop(i).decode('UTF-8'))
				for i in range(0, len(messages)):
					if hashlib.sha1(messages[i]) == check[i]:
						messages.pop(i)
						check.pop(i)
						send(check, socket, False)
						return json.loads(message[i].decode('UTF-8'))

def send(msg, socket, doCheck=True):
    msg = json.dumps(msg).encode('UTF-8')
    check = json.dumps(hashlib.sha1(msg)).encode('UTF-8')
	socket.send(b'|' + msg + b'|' + check + b'|')
	while doCheck:
		if receiveCommand([socket], False) == check:
			break
		socket.send(b'|' + msg + b'|' + check + b'|')
			