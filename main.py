from tkinter import *
from tkinter import ttk
import csv, threading, time, sys, json, os, network, datetime

debug = True
variables = {}
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

def statusUpdate(info):
    global displayStatus, status
    
    status_lines = config['Tk']['status_lines']
    
    status.append(info)
    
    log(info)
    
    while len(status) > status_lines:
        status.pop(0)
    
    displayStatus.set('')
    
    for info in status:
        displayStatus.set(displayStatus.get()+info+'\n')

def log(text):
	if debug:
		with open('log.txt', 'a') as file:
			file.write(str(datetime.datetime.now()) + ' [' + os.path.basename(__file__) + '] ' + text + '\n')	

class serverListner (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = self.end = False
    def run(self):
        global peripherals
        serversocket = network.localServer()
        while not self.end:
            while self.running:
                    clientsocket, address = network.serverListner(serversocket) 
                    if clientsocket:
                        peripherals.append(clientsocket)
                        statusUpdate(address[0] + ' Succesfully Connected')
    def startListner(self):
        global status
        if not self.running:
            statusUpdate('Started Listner')
            self.running = True
        else:
            statusUpdate('Cannot start Listner - Listner is already Running!')
    def stopListner(self, join):
        global status
        if join and self.isAlive():
            self.join()
            statusUpdate('Terminated Listner Thread')
        elif self.running and self.isAlive():
            self.running = False
            statusUpdate('Stopped Listner')
        else:
            statusUpdate('Cannot stop Listner - Listner is not Running')
    def join(self):
        self.end = True
        self.running = False
        threading.Thread.join(self)

class questionControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.newQuestion = False
    def run(self):
        global peripherals
        while True:
            self.question, self.awnser = askQuestion()
            self.newQuestion = False
            while not self.newQuestion:
                receivedCommand = network.getMessageofType('cmd', peripherals)
                if isinstance(receivedCommand, int) and receivedCommand > 0 and receivedCommand <= 4 and questionHandler(receivedCommand, self.question, self.awnser) == True:
                    self.newQuestion = True

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
            statusUpdate('Round ' + str(variables['cntRounds']) + ' starting')
            variables['gamemode'] = 0
            updateClient()
            time.sleep(1)
        variables['gamemode'] = 1
        statusUpdate('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        variables['question'] = questions[variables['cntQuestions']][0]
        statusUpdate(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
        updateClient()
        # return question, awnser
        return questions[variables['cntQuestions']][0], questions[variables['cntQuestions']][1]
    else:
        statusUpdate('So this is Embarasing')
        statusUpdate('We seam to have run out of questions')
        statusUpdate('Exiting...')
        sys.exit()

def questionHandler(event, question, awnser):
    global variables, peripherals, status
    if event == 1:
        statusUpdate('Correct')
        variables['correct'] += 1
        variables['contestants'][list(variables['contestants'].keys())[variables['crtContestant']]] += 1
    elif event == 2:
        statusUpdate('Incorrect - ' + awnser)
        variables['correct'] = 0
    elif event == 3:
        variables['bank'] += variables['money'][variables['correct']]
        statusUpdate('Banked £' + str(variables['money'][variables['correct']]))
        statusUpdate('£' + str(variables['bank']) + ' now in bank')
        variables['correct'] = 0
        statusUpdate('You now have £' + str(variables['money'][variables['correct']]))
        updateClient()
        return False
    elif event == 4:
        statusUpdate('Time Up')
        statusUpdate('You have £' + str(variables['bank']) + ' in the bank')
        variables['cntRounds'] += 1
        variables['correct'] = variables['cntRquestions'] = 0
    event = ''
    variables['cntRquestions'] += 1
    variables['cntQuestions'] += 1
    if variables['correct'] == len(variables['money']) - 1:
        statusUpdate('You have got all questions in round ' + str(variables['cntRounds']) + ' correct')
        statusUpdate('You have £' + str(variables['bank']) + ' in the bank')
        variables['cntRounds'] += 1
        variables['cntRquestions'] = 1
        variables['correct'] = 0
    statusUpdate('You now have £' + str(variables['money'][variables['correct']]))
    if variables['cntRquestions'] == 1:
        variables['gamemode'] = 2
        statusUpdate('You must now choose the Weakest Link')
        i = 1
        while i - 1 < len(variables['contestants']):
            statusUpdate(str(i) + '\t' + list(variables['contestants'].keys())[i-1] + '\t' + str(list(variables['contestants'].values())[i-1]))
            i += 1
        updateClient()
        while True:
            receivedCommand = network.getMessageofType('cmd', peripherals)
            if isinstance(receivedCommand, int) and receivedCommand > 0 and receivedCommand <= len(variables['contestants']):
                statusUpdate(list(variables['contestants'].keys())[receivedCommand - 1] + ' you are the Weakest Link! Goodbye')
                variables['contestants'].pop(list(variables['contestants'].keys())[receivedCommand - 1])
                variables['gamemode'] = 3
                updateClient()
                break
        variables['gamemode'] = 1
    updateClient()
    return True

def importQuestions(file):
    global status
    statusUpdate('Importing Questions...')
    questions = []
    cnt = 0
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1]:
                questions.append([row[0], row[1]])
                cnt += 1
        statusUpdate('Imported ' + str(cnt) + ' Questions')
        # with statement automatically closes the csv file cleanly even in event of unexpected script termination
        return questions

def updateClient():
    global variables, peripherals
    try:
        log('Update Client')
    except:
        print('Update Client')
    for socketObj in peripherals:
        network.sendMessage('variables', variables, socketObj)

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
