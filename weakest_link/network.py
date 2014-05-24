import socket, hashlib, select, os.path, pickle
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
usedTypes = []

class msgClass():
    def __init__(self, type, content):
        self.type = type
        self.content = content

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
                    check[uID] = pickle.loads(received[i])
                    uID += 1
        for key in list(messages.keys()):
            if hashlib.sha1(messages[key]).hexdigest() == check[key]:
                msg = pickle.loads(messages[key])
                if msg.type in usedTypes:
                    return msg.type, key
                else:
                    messages.pop(key)
                    check.pop(key)
            else:
                misc.log('Message Check Failed: ' + messages[key])
                messages.pop(key)
                check.pop(key)
        first = False
    return None, None
        
def getMessagefromStack(key): #this function should not be called use getMessageofType() instead
    temp = pickle.loads(messages[key]).content
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
    msg = pickle.dumps(msgClass(type, content))
    bytesMsg = b'|' + msg + b'|' + pickle.dumps(hashlib.sha1(msg).hexdigest()) + b'|'
    socketObj.send(bytesMsg)
    misc.log('Sent the following Message: '+ str(bytesMsg))
    
def addUsedType(type):
    global usedTypes
    usedTypes.append(type)
    misc.log('Adding type: ' + type + ' to usedType list')
    
def removeUsedType(type):
    global usedTypes
    try:
        usedTypes.remove(type)
        misc.log('Removing type: ' + type + ' from usedType list')
    except ValueError:
        misc.log('Type: \'' + type + '\' not in list - ignoring')

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
    
def getIPAddress():
    return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
