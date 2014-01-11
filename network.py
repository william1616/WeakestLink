import socket, hashlib, select, json, os, datetime, __main__, time
debug = True
uID = 1
messages = {}
check = {}
sender = {}

if __main__.__file__:
    fileName = os.path.basename(__main__.__file__) + ' via ' + os.path.basename(__file__)
else:
    fileName = os.path.basename(__file__)

def getMessage(socketList, waitForMessage=True): #this function should not be called use getMessageofType() instead
    global messages, check, uID
    received = []
    first = True
    while first or waitForMessage:
        for socketObj in socketList:
            readable, writable, err = select.select([socketObj.fileno()], [], [], 0.1)
            if readable:
                received = socketObj.recv(4096).split(b'|')
                while received.count(b'') > 0:
                  received.remove(b'')
                for i in range(0, len(received)):
                  if i % 2 == 0:
                    messages[uID] = received[i]
                    if debug:
                        with open('log.txt', 'a') as file:
                            file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Received the following Message: '+ str(received[i]) + '\n')
                  elif i % 2 == 1:
                    check[uID] = json.loads(received[i].decode('UTF-8'))
                    sender[uID] = socketObj
                    uID += 1
        for key in list(messages.keys()):
            if hashlib.sha1(messages[key]).hexdigest() == check[key]:
                msg = json.loads(messages[key].decode('UTF-8'))
                if msg['type'] != 'check':
                    sendMessage('check', check[key], sender[key], False)
                return msg['type'], key
            else:
                messages.pop(key)
                check.pop(key)
                sender.pop(key)
        first = False
    return None, None
        
def getMessagefromStack(key): #this function should not be called use getMessageofType() instead
    temp = json.loads(json.loads(messages[key].decode('UTF-8'))['content'])
    messages.pop(key)
    check.pop(key)
    sender.pop(key)
    return temp #temp deleted when function returns as local
    
def getMessageofType(type, socketList, waitForMessage=True):
    receivedType, receivedKey = getMessage(socketList, waitForMessage)
    while waitForMessage and receivedType != type:
        receivedType, receivedKey = getMessage(socketList)
    if receivedKey:
        return getMessagefromStack(receivedKey)
    else:
        return None

def sendMessage(type, content, socketObj, doCheck=True):
    global messages, check
    msg = json.dumps({'type': type, 'content': json.dumps(content)}).encode('UTF-8')
    msgCheck = hashlib.sha1(msg).hexdigest()
    bytesMsgCheck = json.dumps(msgCheck).encode('UTF-8')
    bytesMsg = b'|' + msg + b'|' + bytesMsgCheck + b'|'
    socketObj.send(bytesMsg)
    if debug:
        with open('log.txt', 'a') as file:
            file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Sent the following Message: '+ str(bytesMsg) + '\n')
    while doCheck:
        time.sleep(0.1)
        receivedCheck = getMessageofType('check', [socketObj], False)
        if receivedCheck == msgCheck:
            break
        socketObj.send(bytesMsg) #fails after a large number of attempts at sending the data
        if debug:
            with open('log.txt', 'a') as file:
                file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Sent the following Message: '+ str(bytesMsg) + '\n')

def initServerSocket(bindAddress, bindPort):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((bindAddress, bindPort))
    serversocket.listen(5)
    serversocket.setblocking(False)
    return serversocket
    
def serverListner(serversocket):
    readable, writable, err = select.select([serversocket.fileno()], [], [], 1)
    if readable:
        clientsocket, address = serversocket.accept()
        clientsocket.setblocking(True)
        return clientsocket, address
    return None, None

def attemptConnect(socketObj, address, port):
    try:
        if debug:
            with open('log.txt', 'a') as file:
                file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Attempting to connect to ' + str(address) + ' on port ' + str(port) + '\n')
        socketObj.connect((address, port))
        if debug:
            with open('log.txt', 'a') as file:
                file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Successfully connected to ' + str(address) + ' on port ' + str(port) + '\n')
        return True
    except:
        if debug:
            with open('log.txt', 'a') as file:
                file.write(str(datetime.datetime.now()) + ' [' + fileName + '] Failed to connect to ' + str(address) + ' on port ' + str(port) + '\n')
        return False

def initClientSocket():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return clientsocket
        
def localClient():
    clientsocket = initClientSocket('localhost',1024)
    return clientsocket

def localServer():
    serversocket = initServerSocket('localhost',1024)
    return serversocket
