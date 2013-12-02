import socket, hashlib, select
uID = 0
messages = {}
check = {}

def receiveCommand(socketList, loop=True):
    global messages, check, uID
    received = []
    while loop:
        for socket in socketList:
            readable, writable, err = select.select([socket.fileno()], [], [], 0.1)
            if readable:
                received = clientsocket.recv(4096).split('|')
                while received.count('') > 0:
                  received.remove('')
                for i in range(0, len(received)):
                  if i % 2 == 0:
                    messages[uID] = json.loads(received[i].decode('UTF-8'))
                  if i % 2 == 1:
                    check[uID] = json.loads(received[i].decode('UTF-8'))
                  uID += 1
    for key in list(messages.keys()):
      if hashlib.sha1(messages[key]).hexdigest() == check[key]:
        send({'name': 'check', 'check': check[key]}, socket, False)
        return msg, key
      else:
        messages.pop(key)
        check.pop(key)

def send(msg, socket, doCheck=True):
    msg = json.dumps(msg).encode('UTF-8')
    check = json.dumps(hashlib.sha1(msg).hexdigest()).encode('UTF-8')
    socket.send(b'|' + msg + b'|' + check + b'|')
    while doCheck:
        temp, index = receiveCommand([socket], False)
        if temp['name'] == 'check':
            if temp['check'] == check:
                messages.pop(index)
                check.pop(index)
                break
        socket.send(b'|' + msg + b'|' + check + b'|')
			