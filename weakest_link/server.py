from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
from collections import OrderedDict
import csv, threading, time, sys, os.path

path = os.path.dirname(__file__)
try:
    import network, misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("network", os.path.join(path, "network.py"))
    network = loader.load_module("network")
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

variables = {
    'cntQuestions': 0, #row counter for csv file
    'correct': 0, #correct counter per round
    'cntRounds': 1,
    'cntRquestions': 1, #question counter per round
    'bank': 0,
    'question': '',
    'contestants': OrderedDict({'bill': 0,'ben': 0,'bob': 0,'cat': 0,'hat': 0,'matt': 0,'mouse': 0,'man': 0}), #list of contestants creating OrderedDict randomises the order
    'money': [0, 50,100,200,300,400,500,1000,2500,5000],
    'crtContestant': -1, #current contestant key index
    'gamemode': -1, #-1 = still listing, 0 = starting, 1 = questions, 2 = voting, 3 = contestant succesfully removed
    'time': False, #time up
    }
status = []
socketList = []

def statusUpdate(info):
    global displayStatus, status
    
    status_lines = config['Tk']['status_lines']
    
    status.append(info)
    
    misc.log(info)
    
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
        global socketList
        while not self.end:
            while self.running:
                    clientsocket, address = network.serverListner(self.serversocket) 
                    if clientsocket:
                        socketList.append(clientsocket)
                        statusUpdate(address[0] + ' Succesfully Connected')
    def startListner(self):
        global status
        if not self.running:
            self.serversocket = network.initServerSocket(config['server']['bindAddress'],config['server']['bindPort'])
            self.running = True
            statusUpdate('Started Listner')
        else:
            statusUpdate('Cannot start Listner - Listner is already Running!')
    def stopListner(self, join):
        global status
        if join and self.isAlive():
            self.join()
            if hasattr(self, 'serversocket'): network.closeSocket(self.serversocket)
            statusUpdate('Terminated Listner Thread')
        elif self.running:
            self.running = False
            time.sleep(0.1)
            if hasattr(self, 'serversocket'): network.closeSocket(self.serversocket)
            statusUpdate('Stopped Listner')
        else:
            statusUpdate('Cannot stop Listner - Listner is not Running')
    def join(self):
        self.running = False
        time.sleep(0.1)
        self.end = True
        threading.Thread.join(self)

class questionControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.newQuestion = False
    def run(self):
        global socketList
        while True:
            self.question, self.awnser = askQuestion()
            self.newQuestion = False
            while not self.newQuestion:
                receivedCommand = network.getMessageofType('cmd', socketList, False)
                if isinstance(receivedCommand, int) and receivedCommand > 0 and receivedCommand <= 4 and questionHandler(receivedCommand, self.question, self.awnser) == True:
                    self.newQuestion = True

def start():
    global variables, listner, questionThread
    listner.stopListner(True)
    startFrame.grid_remove()
    mainFrame.grid()
    variables['gamemode'] = 0
    questionThread = questionControl()
    questionThread.start()

def initListner():
    global listner
    listner = serverListner()
    listner.start()

def initTk(parent):
    global displayStatus, startFrame, mainFrame, listner
    print('Initiating GUI...')
    
    startFrame = ttk.Frame(parent, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)

    startMenu = Menu(parent)
    parent['menu'] = startMenu
    startFile = Menu(startMenu, tearoff=0)
    startTools = Menu(startMenu, tearoff=0)
    startHelp = Menu(startMenu, tearoff=0)
    startMenu.add_cascade(menu=startFile, label='File')
    startMenu.add_cascade(menu=startTools, label='Tools')
    startMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=lambda: close(parent))
    
    startTools.add_command(label='Select Main Question File', command=selectMainQuestionFile)
    startTools.add_command(label='Select Final Question File', command=selectFinalQuestionFile)
    startTools.add_command(label='Goto Question', command=gotoQuestion)
    startTools.add_separator()
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    
    mainFrame = ttk.Frame(parent, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)
    mainFrame.grid_forget()

    displayStatus = StringVar()

    ttk.Label(startFrame, text='The Weakest Link Server', width=100).grid(column=0, row=0, sticky=N)
    ttk.Label(startFrame, text='Status', width=100).grid(column=0, row=1, sticky=N)
    ttk.Label(startFrame, textvariable=displayStatus, width=100).grid(column=0, row=2, sticky=N)
    ttk.Button(startFrame, text='Start', command=start).grid(column=1, row=0, sticky=N)
    ttk.Button(startFrame, text='Start Listner', command=lambda: listner.startListner()).grid(column=1, row=1, sticky=N)
    ttk.Button(startFrame, text='Stop Listner', command=lambda: listner.stopListner(False)).grid(column=1, row=2, sticky=N)
    
    ttk.Label(mainFrame, text='Status', width=100).grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=displayStatus, width=100).grid(column=1, row=2, sticky=N)
    
    parent.protocol("WM_DELETE_WINDOW", lambda: close(parent))
    
    print('GUI Initiated')

def gotoQuestion():
    global variables, questionThread
    variables['cntQuestions'] = simpledialog.askinteger("Go to question...", "Question Number:", initialvalue=variables['cntQuestions'])
    questionThread.newQuestion = True
    
def selectMainQuestionFile():
    global config
    #this needs to be validated
    config['questions']['mainQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def selectFinalQuestionFile():
    global config
    #this needs to be validated
    config['questions']['finalQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def close(topLevel):
    listner.stopListner(True)
    if topLevel.config()['class'][4] == 'Toplevel': topLevel.root.deiconify()
    topLevel.destroy()
    
def askQuestion():
    global variables, questions, status
    
    mainQ = os.path.join(path, "..\\", config['questions']['mainQ'])
    
    #if the questions are not already imported import them
    try:
        questions
    except:
        print('Importing Questions')
        questions = importQuestions(mainQ)
    
    #cycle through each contestant in turn
    if variables['crtContestant'] < len(variables['contestants']) - 1:
        variables['crtContestant'] += 1
    else:
        variables['crtContestant'] = 0
    
    #if there are still questions left ask the question
    if variables['cntQuestions'] < len(questions):
        if variables['cntRquestions'] == 1:
            for i in list(variables['contestants'].keys()): #set each contestatnts score to 0
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
    global variables, socketList, status
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
        variables['time'] = True
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
        variables['time'] = False
        while True:
            receivedCommand = network.getMessageofType('cmd', socketList)
            if isinstance(receivedCommand, int) and receivedCommand >= 0 and receivedCommand < len(variables['contestants']):
                statusUpdate(list(variables['contestants'].keys())[receivedCommand] + ' you are the Weakest Link! Goodbye')
                variables['contestants'].pop(list(variables['contestants'].keys())[receivedCommand])
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
    global variables, socketList
    try:
        misc.log('Update Client')
    except:
        print('Update Client')
    for socketObj in socketList:
        network.sendMessage('variables', variables, socketObj)

def setup():
    global config
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')
        
if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    initListner()
    root.mainloop()
