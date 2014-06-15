import socket, hashlib, select, os.path, pickle
from  threading import Thread
from queue import Queue, Empty
from time import sleep

path = os.path.dirname(__file__)
try:
    import misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")
    
usedTypes = []
    
class messageQueue(Queue): #prevent unused types from being returned/queued
    def __init__(self, maxsize=0):
        super().__init__(maxsize)
        self.types = {}
        
    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        if item.type not in self.types: #if the type is unrecognised add it to the dict
            self.types[item.type] = 1
        else: #otherwise just increment it
            self.types[item.type] += 1

    def get(self, type, block=True, timeout=None):
        global usedTypes
        try:
            while block or self.types[type] > 0:
                item = super().get(block, timeout)
                misc.log('Got item \'' + str(item.type) + '\' from Stack')
                self.task_done()
                if item.type in usedTypes:
                    self.types[item.type] -= 1 #decrease the number of that type in the queue
                    if item.type == type: #put the item back if its a usedType but not of the type specified
                        misc.log('Stack Size: ' + str(self.qsize()))
                        return item
                    else:
                        self.put(item)
                        misc.log('Putting Item \'' + str(item.type) + '\' back into Stack')
                else: #if the item is not put back in the queue decrease the number of that type in the queue
                    misc.log('Removing Item \'' + str(item.type) + '\' from Stack as type not in usedTypes List')
                    self.types[item.type] -= 1
            raise Empty()
        except KeyError:
            raise Empty()

receivedMessages = messageQueue()

class msgClass():
    def __init__(self, type, content):
        self.type = type
        self.content = pickle.dumps(content)
        self.hash = self.generateHash()
    
    def generateHash(self):
        #use pickle as .encode() only works for text
        return hashlib.sha1(pickle.dumps(self.content)).hexdigest()
        
    def checkHash(self):
        return self.generateHash() == self.hash
        
    def getContent(self):
        return pickle.loads(self.content)

def getMessage(socketObj):
    global receivedMessages
    while True:
        try:
            received = socketObj.recv(4096)
        except ConnectionResetError as exception:
            misc.log(str(exception))
            misc.log('Stopping Listning Daemon')
            break
        try:
            received = pickle.loads(received)
            if received.checkHash() == False:
                raise ValueError('The Checksum Failed')
        except (EOFError, ValueError, AttributeError) as exception:
            misc.log('Message Check Failed: \'' + str(exception) + '\'')
        else:
            receivedMessages.put(received, block=False)
            misc.log('Received the following Message: \''+ str(received.getContent()) + '\' of type \'' + str(received.type) + '\'')
                
def addListningDaemon(*args):
    global receivedMessages
    for socket in args:
        listner = Thread(target=getMessage, args=(socket,))
        listner.setDaemon(True)
        listner.start()
    
def getMessageofType(type, waitForMessage=True):
    global receivedMessages
    try:
        msg = receivedMessages.get(type, waitForMessage)
    except Empty:
        return None
    else:
        misc.log('Retreived Message: \'' + str(msg.getContent()) + '\' of type \'' + str(msg.type) + '\'')
        return msg.getContent()
        
def messageInBuffer(type=None):
    global receivedMessages, usedTypes
    return (not type and not receivedMessages.empty() or type in receivedMessages.types and receivedMessages.types[type] > 0 and type in usedTypes)
    
def sendMessage(type, content, socketObj):
    msg = msgClass(type, content)
    socketObj.send(pickle.dumps(msg))
    misc.log('Sent the following Message: \''+ str(content) + '\' of type \'' + str(msg.type) + '\'')
    sleep(0.005) #allow time for the message to be processed before sending another message
    
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
    serversocket.listen(socket.SOMAXCONN)
    return serversocket
    
def serverListner(serversocket):
    readable, writable, err = select.select([serversocket.fileno()], [], [], 0.01)
    if readable:
        clientsocket, address = serversocket.accept()
        clientsocket.setblocking(True)
        addListningDaemon(clientsocket)
        return clientsocket, address
    return None, None

def attemptConnect(socketObj, address, port):
    try:
        misc.log('Attempting to connect to ' + str(address) + ' on port ' + str(port))
        socketObj.connect((address, port))
        misc.log('Successfully connected to ' + str(address) + ' on port ' + str(port))
        addListningDaemon(socketObj)
        misc.log('Starting Listning Daemon')
        return True
    except OSError as exception:
        misc.log('Failed to connect to ' + str(address) + ' on port ' + str(port) + ' - \'' + str(exception) + '\'')
        return False

def initClientSocket():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.setblocking(True)
    return clientsocket
        
def localClient():
    clientsocket = initClientSocket()
    if attemptConnect(clientsocket, 'localhost', 1024):
        return clientsocket
    else:
        return None

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
