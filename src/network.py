import socket, hashlib, select, pickle, misc
from  threading import Thread
from queue import Queue, Empty
from time import sleep

usedTypes = [] #create a list to contain the names of the types currently in use

class messageQueue(Queue): #overwrite the Queue class with a custom implementation that prevents unused types from being returned/queued
  def __init__(self, maxsize=0): #mimic the Queue constructor by using the same parameters
    super().__init__(maxsize) #create the queue object
    self.types = {} #create a dictionary to store count the number of each type curretly stored in the Queue
    
  def put(self, item, block=True, timeout=None): #mimic Queue.put()
    super().put(item, block, timeout) #put the item in the queue
    #add 1 to the counter for that paticular type
    if item.type in self.types: #check if the type is in the dictionary
      self.types[item.type] += 1 #increment the counter for the type
    else: #if the type is unrecognised add it to the dictionary
      self.types[item.type] = 1 #this is the first message of this type so the total number of this type of message in the dictionary is 1
    
  def get(self, type=None, block=True, timeout=None): #mimic Queue.get() but with an extra optional parameter to allow the type of message to be retrieved to be specififed
    global usedTypes #get the list of types which are accepted
    try:
      if type: #if we want a message of a specific type
        while block or self.types[type] > 0: #check if that message exists or if we should wait until is exists (block)
          item = super().get(block, timeout) #get the item (message) from the stack
          misc.log('Got item \'' + str(item.type) + '\' from Stack') #log the item type
          self.types[item.type] -= 1 #decrease the number of that type in the queue as we just removed an item of that type from the queue
          self.task_done() #mark the item as processed
          if item.type in usedTypes: #check if the item we just got from the stack is of a type that we want to listen for
            if item.type == type: #if the item is of the type that we are looking for
              misc.log('Stack Size: ' + str(self.qsize())) #log an estimate for the size of the stack
              return item #return the item
            else: #if the item is not of the type thatwe are looking for but is in the usedTypes list (ie we don't want it now but we will want it later) put it back in the stack
              self.put(item) #put the item back in the stack
              misc.log('Putting Item \'' + str(item.type) + '\' back into Stack') #log the item type
          else:
            misc.log('Removing Item \'' + str(item.type) + '\' from Stack as type not in usedTypes List') #don't put the item back in the stack if it is not in the used types list and log a message to this affect
        raise Empty() #if no items of that type exist in the Queue throw an exception
      else: #if we don't want a message of a specific type (i.e behave like a normal Queue whilst still respection the global usedTypes list)
        while True: #if there are no items left in the Queue and we are not blocking super().get() will raise the Empty() exception
          item = super().get(block, timeout) #get an item from the Queue
          misc.log('Got item \'' + str(item.type) + '\' from Stack') #log the items type
          self.types[item.type] -= 1 #decrease the number of that type in the queue as we just removed an item of that type from the queue
          self.task_done() #mark the item as processed
          if item.type in usedTypes: #check if the item we just got from the stack is of a type that we want to listen for
            return item #return the item
          else:
            misc.log('Removing Item \'' + str(item.type) + '\' from Stack as type not in usedTypes List') #don't put the item back in the stack if it is not in the used types list and log a message to this affect
    except KeyError: #if the type is not a key in self.types then no items of that type exist in the queue so raise an exception
      raise Empty()

#create a queue for received messaged using the class extended above
receivedMessages = messageQueue()

#class containing the messaes sent/received
class msgClass():
  def __init__(self, type, content):
    self.type = type #store the message type
    self.content = pickle.dumps(content) #pickle the content into bytes to allow a hash to be generated of it
    self.hash = self.generateHash() #create a hash of the content
    
  def generateHash(self): #calculate a sha1 hash of the content and return it as a string containing only hexidecimal digits
    return hashlib.sha1(self.content).hexdigest()
    
  def checkHash(self): #check if the hash of the content matches the hash of the content when the object was initialized
    return self.generateHash() == self.hash
    
  #unpickle the content bytes into their original form
  def getContent(self):
    return pickle.loads(self.content)

def getMessage(socketObj): #get any messages in the sockets buffer
  global receivedMessages
  while True: #loop until a break
    try:
      received = socketObj.recv(4096) #blocking call waiting for their to be data in the sockets buffer
    except ConnectionResetError as exception: #if the conection is closed
      misc.log(str(exception)) #log the exception
      misc.log('Stopping Listning Daemon')
      break #break out of the loop (stop listning for messages)
    try:
      received = pickle.loads(received) #unpickle the message
      if received.checkHash() == False: #check if the message was correctly transmitted
        raise ValueError('The Checksum Failed') #raise an exception if the message was not transmitted correctly
    except (EOFError, ValueError, AttributeError) as exception:
      misc.log('Message Check Failed: \'' + str(exception) + '\'') #log any errors
    else: #if no errors occured
      receivedMessages.put(received, block=False) #put the message in the message Queue
      misc.log('Received the following Message: \''+ str(received.getContent()) + '\' of type \'' + str(received.type) + '\'') #log the receipt of the message 
      
def addListningDaemon(*args): #create a Daemon (thread) listning for messages
  global receivedMessages
  for socket in args: #create a listner for each socket
    listner = Thread(target=getMessage, args=(socket,)) #thread te getMessage() function and pass the socket object as an argument
    listner.setDaemon(True) #when the main thread exists close the threads immediatly don't wait for them to finish running
    listner.start() #start the thread
    
def getMessageofType(type=None, waitForMessage=True): #get a message of a specfic type
  global receivedMessages
  try:
    msg = receivedMessages.get(type, waitForMessage) #get a mesasge of the requsted type from the Queue
  except Empty:
    return None #if no messages of the requested type exist return an empty value
  else: #if a message of the requested type exists get and return it
    misc.log('Retreived Message: \'' + str(msg.getContent()) + '\' of type \'' + str(msg.type) + '\'') #log the message and its type
    return msg.getContent() 
    
def messageInBuffer(type=None): #check if a mesasge of a specfic type is in the messageQueue
  global receivedMessages, usedTypes
  #return True for the following conditions:
  #->no type is specified AND the Queue not empty
  #->the type is in the Queues list of types AND their are messaged of that type in the Queue AND that type is in the global usedTypes list
  return (not type and not receivedMessages.empty() or type in receivedMessages.types and receivedMessages.types[type] > 0 and type in usedTypes)
  
#send a message
#type => sting identifying what the content of the message pertains to; content => message content (can be any data type), socketObj => socket through which to send the message
def sendMessage(type, content, socketObj):
  msg = msgClass(type, content) #create a message class container for the message
  socketObj.send(pickle.dumps(msg)) #send the message through the socket converting it into a bytes object first
  misc.log('Sent the following Message: \''+ str(content) + '\' of type \'' + str(msg.type) + '\'') #log the sending of the message
  sleep(0.005) #allow time for the message to be processed before sending another message
  
#type => sting identifying used when sending messages
def addUsedType(type): #add a type of message that should be accepted by the listner
  global usedTypes
  usedTypes.append(type) #append the type name to the end of the list
  misc.log('Adding type: ' + type + ' to usedType list') #log the action
  
#type => sting identifying used when sending messages
def removeUsedType(type): #specify a type of message that you no longer want to listen for that is currently being listned for
  global usedTypes
  try:
    usedTypes.remove(type) #remove the type from the list
    misc.log('Removing type: ' + type + ' from usedType list') #log the removal
  except ValueError: #if the type is not in the list log the error and continue as normal
    misc.log('Type: \'' + type + '\' not in list - ignoring')
  
#create a serversocket which clients connect to when initializing a connection
#bindAddress => string ip address to create the socket on
#bindPort => string TCP port to create the socket on
def initServerSocket(bindAddress, bindPort):
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create the socket
  serversocket.bind((bindAddress, bindPort)) #bind the socket to the address and port provided
  serversocket.listen(socket.SOMAXCONN) #start listing for connections -> set the number of queued connections (backlog) as high as possible. Queued connections are those connections waiting to be processed => processing is done by serverListner()
  return serversocket #return the socket object
  
def serverListner(serversocket): #process any connection to the socket passed as a parameter
  readable, writable, err = select.select([serversocket.fileno()], [], [], 0.01) #check if their is data in the sockets buffer
  if readable: #if there is data in the sockets buffer
    clientsocket, address = serversocket.accept() #accept any connections
    clientsocket.setblocking(True) #setup the socket as a blocking socket
    addListningDaemon(clientsocket) #create a listner for the socket
    return clientsocket, address #return the socket and its address
  return None, None #otherwise return null
  
#attempt to connect to a serversocket with a clientsocket
#socketObj => clientSocket
#address => address of the serverSocket
#port => TCP port of the serverSocket
def attemptConnect(socketObj, address, port):
  try:
    misc.log('Attempting to connect to ' + str(address) + ' on port ' + str(port)) #log the attempt to connect
    socketObj.connect((address, port)) #connect to the serversocket
    misc.log('Successfully connected to ' + str(address) + ' on port ' + str(port))
    addListningDaemon(socketObj) #add a listner for the connection
    misc.log('Starting Listning Daemon')
    return True #return True => connection succesful
  except OSError as exception: #if the connection failed
    misc.log('Failed to connect to ' + str(address) + ' on port ' + str(port) + ' - \'' + str(exception) + '\'') #log the failure
    return False #reuturn False => connection unsuccesful
  
def initClientSocket(): #create  a clientsocket
  clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create the socket object
  clientsocket.setblocking(True) #make the socket a blocking socket
  return clientsocket #return the socket object
  
#port => TCP port to attempt to connect to
def localClient(port=1024): #create a clientsocket and connect it to localhost
  clientsocket = initClientSocket() #create the clientsocket
  if attemptConnect(clientsocket, 'localhost', port): #attempt to connect to localhost
    return clientsocket #return the socket object
  else:
    return None #if no object exists return a null value

#port => TCP port to attempt to bind to
def localServer(port=1024): #create a serversocket running on localhost
  serversocket = initServerSocket('localhost', port)
  return serversocket #return the socket object
    
#socketObj => socket object to close
def closeSocket(socketObj): #close a socket
  try:
    socketObj.shutdown(socket.SHUT_RDWR) #shutdown both reading and writing to the socket
  except OSError: #if the socket is not initialized continue as normal
    pass
  socketObj.close() #close the socket object
  
def getIPAddress(): #get the IP address of the current machine
  return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1] #return a list of all the ip address that the machine has
