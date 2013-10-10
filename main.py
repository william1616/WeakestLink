from tkinter import *
from tkinter import ttk
import csv
import socket
import hashlib
import threading
import time
import select
import sys
import json

window_title = 'The Weakest Link'
status_lines = 25
mainQ = 'questions.csv'
finalQ = 'questions.csv'
receive = ''
variables = {}
variables['cntQuestions'] = 0
variables['correct'] = 0
variables['cntRounds'] = 1
variables['cntRquestions'] = 1
variables['bank'] = 0
variables['question'] = ''
variables['contestants'] = {'bill': 0,'ben': 0,'bob': 0,'cat': 0,'hat': 0,'matt': 0,'mouse': 0,'man': 0}
variables['money'] = [0, 50,100,200,300,400,500,1000,2500,5000]
questions = []
status = []
questions = []
peripherals = []
receivedCommand = ''
crtContestant = -1

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 1024))
serversocket.listen(5)
serversocket.setblocking(False)

def status_update():
    i = 0
    start_status.set('')
    while True:
        if i == len(status): break
        if i > len(status) - status_lines:
            start_status.set(start_status.get()+status[i]+'\n')
        i += 1

class connectListner (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        while True:
            print('server loop')
            readable, writable, err = select.select([serversocket.fileno()], [], [], 1)
            if readable:
                clientsocket, address = serversocket.accept()
                status.append(address[0] + ' Succesfully Connected')
                status_update()
                peripherals.append(clientsocket)
            if self.end == True:
                break
    def join(self):
            self.end = True

class receiveCommand (threading.Thread):
    def __init__(self, clientsocket):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.end = False
    def run(self):
        global receivedCommand
        while True:
            print('server receive loop')
            readable, writable, err = select.select([self.clientsocket.fileno()], [], [], 1)
            if readable:
                msg = self.clientsocket.recv(4096)
                #check = self.clientsocket.recv(40).decode('UTF-8')
                #assert(hashlib.sha1(msg).hexdigest() == check)
                receivedCommand = json.loads(msg.decode('UTF-8'))
            if self.end == True:
                break
    def join(self):
            self.end = True

class questionControl(threading.Thread):
    def __init__(self, ):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global receivedCommand
        while True:
            askQuestion()
            updateClient()
            i = 0
            while True:
                if self.end == True:
                    break
                if receivedCommand != '':
                    if questionHandler(receivedCommand) == True:
                        receivedCommand = ''
                        break
                    receivedCommand = ''
            if self.end == True:
                break
    def join(self):
            self.end = True

def start():
    global peripherals
    peripheralThreads = []
    disconnect()
    startFrame.grid_forget()
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    for i in peripherals:
        peripheralThreads.append(receiveCommand(i))
    for i in peripheralThreads:
        i.start()
    run = questionControl()
    run.start()

def connect():
        global listner
        listner = connectListner()
        listner.start()
        status.append('Started Listner')
        status_update()
        
def disconnect():
    global listner
    if listner.isAlive():
        listner.join()
        status.append('Stopped Listner')
        status_update()

root = Tk()
root.title(window_title)

startFrame = ttk.Frame(root, padding="3 3 3 3")
startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
startFrame.columnconfigure(0, weight=1)
startFrame.rowconfigure(0, weight=1)

mainFrame = ttk.Frame(root, padding="3 3 3 3")
mainFrame.columnconfigure(0, weight=1)
mainFrame.rowconfigure(0, weight=1)

start_status = StringVar()

ttk.Label(startFrame, text='Status', font=font.Font(size=16, underline=True)).grid(column=1, row=1, sticky=N)
ttk.Label(startFrame, textvariable=start_status, width=100).grid(column=1, row=2, sticky=N)
ttk.Button(startFrame, text='Start', command=start).grid(column=2, row=1, sticky=N)
ttk.Button(startFrame, text='Start Listner', command=connect).grid(column=2, row=2, sticky=N)
ttk.Button(startFrame, text='Stop Listner', command=disconnect).grid(column=2, row=3, sticky=N)

ttk.Label(mainFrame, text='Status', width=100).grid(column=1, row=1, sticky=N)
ttk.Label(mainFrame, textvariable=start_status, width=100).grid(column=1, row=2, sticky=N)

def askQuestion():
    global questions, mainQ, variables, crtContestant
    importQuestions(mainQ)
    if crtContestant <= len(variables['contestants']):
        crtContestant += 1
    else:
        crtContestant = 0
    if variables['cntQuestions'] < len(questions):
        if variables['cntRquestions'] == 1:
            for i in list(variables['contestants'].keys()):
                variables['contestants'][i] = 0
            status.append('Round ' + str(variables['cntRounds']) + ' starting')
            status_update()
            time.sleep(1)
        status.append('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        status.append(list(variables['contestants'].keys())[crtContestant] + ': ' + questions[variables['cntQuestions']][0])
        variables['question'] = questions[variables['cntQuestions']][0]
        status_update()
    else:
        status.append('So this is Embarasing')
        status.append('We seam to have run out of questions')
        status.append('Exiting...')
        status_update()
        sys.exit()

def questionHandler(event):
    global questions, variables, receivedCommand, crtContestant
    if event == 1:
        status.append('Correct')
        variables['correct'] += 1
        variables['contestants'][list(variables['contestants'].keys())[crtContestant]] += 1
    elif event == 2:
        status.append('Incorrect - ' + questions[variables['cntQuestions']][1])
        variables['correct'] = 0
    elif event == 3:
        variables['bank'] += variables['money'][variables['correct']]
        status.append('Banked £' + str(variables['money'][variables['correct']]))
        status.append('£' + str(variables['bank']) + ' now in bank')
        variables['correct'] = 0
        status.append('You now have £' + str(variables['money'][variables['correct']]))
        #variables['cntQuestions'] =- 1 double check if this is needed?
        status_update()
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
        status.append('You must now choose the Weakest Link')
        i = 1
        while i - 1 < len(variables['contestants']):
            status.append(str(i) + '\t' + list(variables['contestants'].keys())[i-1] + '\t' + str(list(variables['contestants'].values())[i-1]))
            i += 1
        while True:
            if receivedCommand != '':
                if isinstance(receivedCommand, int) and receivedCommand > 0 and receivedCommand <= len(variables['contestants']):
                    variables['contestants'].pop(list(variables['contestants'].keys())[receivedCommand - 1])
                    receivedCommand = ''
                    break
                receivedCommand = ''
    status_update()
    return True

def importQuestions(file):
    global questions
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1]:
                questions.append([row[0], row[1]])
    # with statement automatically closes the csv file cleanly even in event of unexpected script termination

def updateClient():
    global variables
    jsonVariables = json.dumps(variables)
    assert(variables == json.loads(jsonVariables))
    jsonBytes = jsonVariables.encode('UTF-8')
    check = hashlib.sha1(jsonBytes).hexdigest().encode('UTF-8')
    for clientsocket in peripherals:
        bytesSent = clientsocket.send(jsonBytes)
        bytesSent = clientsocket.send(check)
    
root.mainloop()
