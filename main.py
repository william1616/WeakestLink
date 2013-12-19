from tkinter import *
from tkinter import ttk
import csv, socket, hashlib, threading, time, select, sys, json, os

variables = {}
variables['name'] = 'variables'
variables['cntQuestions'] = 0
variables['correct'] = 0
variables['cntRounds'] = 1
variables['cntRquestions'] = 1
variables['bank'] = 0
variables['question'] = ''
variables['contestants'] = {'bill': 0,'ben': 0,'bob': 0,'cat': 0,'hat': 0,'matt': 0,'mouse': 0,'man': 0}
variables['money'] = [0, 50,100,200,300,400,500,1000,2500,5000]
variables['crtContestant'] = -1
variables['gamemode'] = 0
#0 = starting, 1 = questions, 2 = voting, 3 = contestant succesfully removed
status = []
peripherals = []
messages = {}
check = {}
uID = 0

def initServer():
    global status
    bindAddress = config['server']['bindAddress']
    bindPort = config['server']['bindPort']

    #bindAddresses.append(socket.gethostname())
    #bindAddresses.append(socket.gethostbyname(socket.gethostname()))
    
    status.append('Server bound to ' + bindAddress)
    status_update()
    
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((bindAddress, bindPort))
    serversocket.listen(5)
    serversocket.setblocking(False)
    
    return serversocket

def status_update():
    global displayStatus, status
    
    status_lines = config['Tk']['status_lines']
    
    while len(status) > status_lines:
        status.pop(0)
    
    displayStatus.set('')
    
    for info in status:
        displayStatus.set(displayStatus.get()+info+'\n')

class serverListner (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = self.end = False
    def run(self):
        global peripherals, status
        serversocket = initServer()
        while not self.end:
            while self.running:
                readable, writable, err = select.select([serversocket.fileno()], [], [], 1)
                if readable:
                    clientsocket, address = serversocket.accept()
                    status.append(address[0] + ' Succesfully Connected')
                    status_update()
                    peripherals.append(clientsocket)
    def startListner(self):
        global status
        if not self.running:
            status.append('Started Listner')
            self.running = True
        else:
            status.append('Cannot start Listner - Listner is already Running!')
        status_update()
    def stopListner(self, join):
        global status
        if join and self.isAlive():
            self.join()
            status.append('Terminated Listner Thread')
        elif self.running and self.isAlive():
            self.running = False
            status.append('Stopped Listner')
        else:
            status.append('Cannot stop Listner - Listner is not Running')
        status_update()
    def join(self):
        self.end = True
        self.running = False
        threading.Thread.join(self)

class questionControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.newQuestion = False
    def run(self):
        global peripherals, messages, check
        while True:
            self.question, self.awnser = askQuestion()
            self.newQuestion = False
            while not self.newQuestion:
                receivedCommand, index = receiveCommand(peripherals)
        if receivedCommand['name'] == 'control' and receivedCommand['signal'] != '' and isinstance(receivedCommand['signal'], int) and receivedCommand['signal'] > 0 and receivedCommand['signal'] <= 4:
          if questionHandler(receivedCommand['signal'], self.question, self.awnser) == True:
            self.newQuestion = True
            messages.pop(index)
            check.pop(index)

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

def start():
    global variables
    listner.stopListner(True)
    startFrame.grid_remove()
    mainFrame.grid()
    variables['gamemode'] = 1
    questionThread = questionControl()
    questionThread.start()

def initListner():
    global listner
    listner = serverListner()
    listner.start()

def initTk():
    global displayStatus, root, startFrame, mainFrame, listner
    print('Initiating GUI...')
    
    window_title = config['Tk']['window_title']
    
    root = Tk()
    root.title(window_title)

    startFrame = ttk.Frame(root, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)

    mainFrame = ttk.Frame(root, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)
    mainFrame.grid_forget()

    displayStatus = StringVar()

    ttk.Label(startFrame, text='Status').grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, textvariable=displayStatus, width=100).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text='Start', command=start).grid(column=2, row=1, sticky=N)
    ttk.Button(startFrame, text='Start Listner', command=lambda: listner.startListner()).grid(column=2, row=2, sticky=N)
    ttk.Button(startFrame, text='Stop Listner', command=lambda: listner.stopListner(False)).grid(column=2, row=3, sticky=N)

    ttk.Label(mainFrame, text='Status', width=100).grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=displayStatus, width=100).grid(column=1, row=2, sticky=N)

    print('GUI Initiated')

def askQuestion():
    global variables, questions, status
    
    mainQ = config['questions']['mainQ']
    
    try:
        questions
    except:
        print('Importing Questions')
        questions = importQuestions(mainQ)
    if variables['crtContestant'] < len(variables['contestants']) - 1:
        variables['crtContestant'] += 1
    else:
        variables['crtContestant'] = 0
    if variables['cntQuestions'] < len(questions):
        if variables['cntRquestions'] == 1:
            for i in list(variables['contestants'].keys()):
                variables['contestants'][i] = 0
            status.append('Round ' + str(variables['cntRounds']) + ' starting')
            variables['gamemode'] = 0
            status_update()
            updateClient()
            time.sleep(1)
        variables['gamemode'] = 1
        status.append('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        variables['question'] = questions[variables['cntQuestions']][0]
        status.append(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
        status_update()
        updateClient()
        # return question, awnser
        return questions[variables['cntQuestions']][0], questions[variables['cntQuestions']][1]
    else:
        status.append('So this is Embarasing')
        status.append('We seam to have run out of questions')
        status.append('Exiting...')
        status_update()
        sys.exit()

def questionHandler(event, question, awnser):
    global variables, peripherals, messages, check, status
    if event == 1:
        status.append('Correct')
        variables['correct'] += 1
        variables['contestants'][list(variables['contestants'].keys())[variables['crtContestant']]] += 1
    elif event == 2:
        status.append('Incorrect - ' + awnser)
        variables['correct'] = 0
    elif event == 3:
        variables['bank'] += variables['money'][variables['correct']]
        status.append('Banked £' + str(variables['money'][variables['correct']]))
        status.append('£' + str(variables['bank']) + ' now in bank')
        variables['correct'] = 0
        status.append('You now have £' + str(variables['money'][variables['correct']]))
        status_update()
        updateClient()
        return False
    elif event == 4:
        status.append('Time Up')
        status.append('You have £' + str(variables['bank']) + ' in the bank')
        variables['cntRounds'] += 1
        variables['correct'] = variables['cntRquestions'] = 0
    event = ''
    variables['cntRquestions'] += 1
    variables['cntQuestions'] += 1
    if variables['correct'] == len(variables['money']) - 1:
        status.append('You have got all questions in round ' + str(variables['cntRounds']) + ' correct')
        status.append('You have £' + str(variables['bank']) + ' in the bank')
        variables['cntRounds'] += 1
        variables['cntRquestions'] = 1
        variables['correct'] = 0
    status.append('You now have £' + str(variables['money'][variables['correct']]))
    if variables['cntRquestions'] == 1:
        variables['gamemode'] = 2
        status.append('You must now choose the Weakest Link')
        i = 1
        while i - 1 < len(variables['contestants']):
            status.append(str(i) + '\t' + list(variables['contestants'].keys())[i-1] + '\t' + str(list(variables['contestants'].values())[i-1]))
            i += 1
        status_update()
        updateClient()
        while True:
            receivedCommand, index = receiveCommand(peripherals)
            if receivedCommand['name'] == 'control' and receivedCommand['signal'] != '' and isinstance(receivedCommand['signal'], int) and receivedCommand['signal'] > 0 and receivedCommand['signal'] <= len(variables['contestants']):
                status.append(list(variables['contestants'].keys())[receivedCommand['signal'] - 1] + ' you are the Weakest Link! Goodbye')
                variables['contestants'].pop(list(variables['contestants'].keys())[receivedCommand['signal'] - 1])
                variables['gamemode'] = 3
                updateClient()
                messages.pop(index)
                check.pop(index)
                break
        variables['gamemode'] = 1
    status_update()
    updateClient()
    return True

def importQuestions(file):
    global status
    status.append('Importing Questions...')
    status_update()
    questions = []
    cnt = 0
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1]:
                questions.append([row[0], row[1]])
                cnt += 1
        status.append('Imported ' + str(cnt) + ' Questions')
        status_update()
        # with statement automatically closes the csv file cleanly even in event of unexpected script termination
        return questions

def updateClient():
    global variables, peripherals
    for socket in peripherals:
        send(variables, socket)

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

def initConfig():
    global config
    
    #config settings
    fileName = 'config.json'
    
    print('Importing Config...')
    with open(fileName) as configFile:
        config = json.loads(configFile.read())
    print('Config Imported')

if __name__ == '__main__':
    initConfig()
    initTk()
    initListner()
    root.mainloop()
