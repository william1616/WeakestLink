import socket, hashlib, select, json, os.path
from collections import OrderedDict

path = os.path.dirname(__file__)
try:
    import misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

debug = True
uID = 1
messages = {}
check = {}

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
                    misc.log('Received the following Message: '+ str(received[i]))
                  elif i % 2 == 1:
                    check[uID] = json.loads(received[i].decode('UTF-8'))
                    uID += 1
        for key in list(messages.keys()):
            if hashlib.sha1(messages[key]).hexdigest() == check[key]:
                msg = json.loads(messages[key].decode('UTF-8'))
                return msg['type'], key
            else:
                messages.pop(key)
                check.pop(key)
        first = False
    return None, None
        
def getMessagefromStack(key): #this function should not be called use getMessageofType() instead
    temp = json.loads(json.loads(messages[key].decode('UTF-8'))['content'], object_pairs_hook = OrderedDict)
    messages.pop(key)
    check.pop(key)
    return temp #temp deleted when function returns as local
    
def getMessageofType(type, socketList, waitForMessage=True):
    receivedType, receivedKey = getMessage(socketList, waitForMessage)
    while waitForMessage and receivedType != type:
        receivedType, receivedKey = getMessage(socketList)
    if receivedKey and receivedType == type:
        return getMessagefromStack(receivedKey)
    else:
        return None

def sendMessage(type, content, socketObj):
    global messages, check
    msg = json.dumps({'type': type, 'content': json.dumps(content)}).encode('UTF-8')
    msgCheck = hashlib.sha1(msg).hexdigest()
    bytesMsgCheck = json.dumps(msgCheck).encode('UTF-8')
    bytesMsg = b'|' + msg + b'|' + bytesMsgCheck + b'|'
    socketObj.send(bytesMsg)
    misc.log('Sent the following Message: '+ str(bytesMsg))

def initServerSocket(bindAddress, bindPort):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((bindAddress, bindPort))
    serversocket.listen(5)
    return serversocket
    
def serverListner(serversocket):
    readable, writable, err = select.select([serversocket.fileno()], [], [], 0.1)
    if readable:
        clientsocket, address = serversocket.accept()
        return clientsocket, address
    return None, None

def attemptConnect(socketObj, address, port):
    try:
        misc.log('Attempting to connect to ' + str(address) + ' on port ' + str(port))
        socketObj.connect((address, port))
        misc.log('Successfully connected to ' + str(address) + ' on port ' + str(port))
        return True
    except:
        misc.log('Failed to connect to ' + str(address) + ' on port ' + str(port))
        return False

def initClientSocket():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return clientsocket
        
def localClient():
    clientsocket = initClientSocket()
    clientsocket.connect(('localhost',1024))
    return clientsocket

def localServer():
    serversocket = initServerSocket('localhost',1024)
    return serversocket
    
def closeSocket(socketObj):
    #this shouldn't be needed but there no harm calling it
    try:
        socketObj.shutdown(socket.SHUT_RDWR)
    except OSError: #incase the socket is not connected
        pass
    socketObj.close()
