import socket, hashlib, select, json
uID = 0
messages = {}
check = {}

def initServerSocket(bindAddress, bindPort):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((bindAddress, bindPort))
    serversocket.listen(5)
    serversocket.setblocking(False)    
    return serversocket
	
def initClientSocket(connectAddress, connectPort):
	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientsocket.connect((connectAddress, connectPort))
	return clientsocket

def receiveCommand(socketList, waitForCommand=True):
    global messages, check, uID
    received = []
    first = True
    while first or waitForCommand:
        for socket in socketList:
            readable, writable, err = select.select([socket.fileno()], [], [], 0.1)
            if readable:
                received = socket.recv(4096).split(b'|')
                while received.count(b'') > 0:
                  received.remove(b'')
                for i in range(0, len(received)):
                  if i % 2 == 0:
                    messages[uID] = received[i]
                  elif i % 2 == 1:
                    check[uID] = json.loads(received[i].decode('UTF-8'))
                    uID += 1
        for key in list(messages.keys()):
            if hashlib.sha1(messages[key]).hexdigest() == check[key]:
                msg = json.loads(messages[key].decode('UTF-8'))
                if msg['name'] != 'check':
                    for socket in socketList:
                        send({'name': 'check', 'check': check[key]}, socket, False)
                return json.loads(messages[key].decode('UTF-8')), key
            else:
                messages.pop(key)
                check.pop(key)
        first = False

def send(msg, socket, doCheck=True):
    global messages, check
    msg = json.dumps(msg).encode('UTF-8')
    msgCheck = hashlib.sha1(msg).hexdigest()
    bytesMsgCheck = json.dumps(msgCheck).encode('UTF-8')
    socket.send(b'|' + msg + b'|' + bytesMsgCheck + b'|')
    while doCheck:
        receivedCommand, index = receiveCommand([socket], False)
        if receivedCommand and receivedCommand['name'] == 'check' and receivedCommand['check'] == msgCheck:
            messages.pop(index)
            check.pop(index)
            break
        socket.send(b'|' + msg + b'|' + bytesMsgCheck + b'|')