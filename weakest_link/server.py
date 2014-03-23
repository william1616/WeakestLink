from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
from collections import OrderedDict
from operator import itemgetter
from math import floor
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
    
status = []
socketList = []

def contestantGenerator():
    for i in range(0, config['questions']['contestantCnt']):
        yield contestantClass(str(i))
        
class contestantClass():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.totalScore = 0
        self.finalScore = [None] * int(config['questions']['finalRndQCnt'] / 2)
        
    def incScore(self, ammount=1):
        self.score += ammount
        self.totalScore += ammount
        
    def correctFinalQu(self, questionNo):
        self.incScore()
        if questionNo <= config['questions']['finalRndQCnt']:
            self.finalScore[floor((questionNo - 1) / 2)] = True
        
    def incorrectFinalQu(self, questionNo):
        if questionNo <= config['questions']['finalRndQCnt']:
            self.finalScore[floor((questionNo - 1) / 2)] = False
        
    def clrScore(self):
        self.score = 0
        
    def finalQuestionsCorrect(self):
        return self.finalScore.count(True)
        
class roundControllerClass():
    def __init__(self):
        self.money = [0, 50,100,200,300,400,500,1000,2500,5000]
        self.moneyCounter = 0
        self.correct = 0
        self.rQuestions = 1
    
    def getCurMoney(self):
        return self.money[self.moneyCounter]
        
    def testAllCorrect(self):
        return len(self.money) - 1 == self.moneyCounter
        
class gameControllerClass()
    def __init__(self):
        self.bank = 0
        self.round = 0
        self.contestantCnt = config['questions']['contestantCnt']
        self.contestants = []
        self.removedContestants = []
        for contestant in contestantGenerator():
            self.contestants.append(contestant)
        self.roundControllers = {}
        for i in range(1, self.contestantCnt + 1):
            self.roundControllers[i] = roundControllerClass()
        self.nextRound()
            
    def getCurRndCtrl(self):
        self.curRndCtrl = self.roundControllers[self.round]
        
    def getRQuestionNo(self):
        return self.curRndCtrl.rQuestions
        
    def nextRound(self):
        self.round += 1
        self.getCurRndCtrl()
        for i in contestants:
            i.clrScore()
        sendClientEvent('contestantUpdate', self.contestants)
        self.nextContestant()
        if checkFinalRound():
            self.nextFinal()
        else:
            statusUpdate('Round ' + str(self.round) + ' starting')
            sendClientEvent('rndStart', [self.round])
        time.sleep(1)
        
    def weakestLink(self):    
        statusUpdate('You must now choose the Weakest Link')
        i = 1
        while i - 1 < len(self.contestants):
            statusUpdate(str(i) + '\t' + self.contestants[i-1] + '\t' + self.contestants[i-1])
            i += 1
        sendClientEvent('eliminationWait', [None])
        while True:
            index = network.getMessageofType('removeContestant', socketList)
            if isinstance(index, int) and index >= 0 and index < len(self.contestants):
                eliminated = self.contestants[index]
                statusUpdate(eliminated.name + ' you are the Weakest Link! Goodbye')
                self.removedContestants.append(self.contestants.pop(index))
                sendClientEvent('contestantEliminated', [eliminated])
                time.sleep(1)
                break
        
    def nextContestant(self):
        self.crtContestantIndex, nxtContestantIndex = cycleContestants(crtContestant, len(self.contestants))
        self.curContestant = self.contestants[self.crtContestantIndex]
        self.nxtContestant = self.contestants[nxtContestantIndex]
    
    def correctAns(self, awnser):
        statusUpdate('Correct - ' + awnser)
        self.curRndCtrl.correct += 1
        self.curRndCtrl.moneyCounter += 1
        self.curContestant.incScore()
        if self.curRndCtrl.testAllCorrect:
            self.allCorrect()
        else:
            self.ans()
        sendClientEvent('correctAns', [awnser])
        time.sleep(1)
        
    def incorrectAns(self, awnser):
        statusUpdate('Incorrect - ' + awnser)
        self.curRndCtrl.moneyCounter = 0
        self.ans()
        sendClientEvent('incorrectAns', [awnser])
        time.sleep(1)
        
    def ans(self):
        self.curRndCtrl.rQuestions += 1
        self.nextContestant()
        sendClientEvent('contestantUpdate', [self.contestants])
        sendClientEvent('rndScoreUpdate', [self.curRndCtrl.moneyCounter, self.curRndCtrl.money, self.bank])
        statusUpdate('You now have £' + self.curRndCtrl.getCurMoney())
        
    def bank(self):
        statusUpdate('Banked £' + str(change))
        statusUpdate('£' + str(self.bank) + ' now in bank')
        statusUpdate('You now have £0')
        self.bank += self.curRndCtrl.getCurMoney()
        self.curRndCtrl.moneyCounter = 0
        sendClientEvent('rndScoreUpdate', [0, self.curRndCtrl.money, self.bank])
        
    def timeUp(self):
        statusUpdate('Time Up')
        statusUpdate('You have £' + str(self.bank) + ' in the bank')
        sendClientEvent('timeUp', [None])
        time.sleep(1)
        self.weakestLink()
        self.nextRound()
    
    def allCorrect(self):
        statusUpdate('You have got all questions in round ' + str(self.round) + ' correct')
        statusUpdate('You have £' + str(self.bank) + ' in the bank')
        sendClientEvent('rndScoreUpdate', [self.curRndCtrl.moneyCounter, self.curRndCtrl.money, self.bank])
        sendClientEvent('allCorrect', [None])
        time.sleep(1)
        self.weakestLink()
        self.nextRound()
        
    def checkFinalRound(self):
        return len(self.contestants) == 2:
        
    def nextFinal(self):
        statusUpdate('Final Round starting')
        sendClientEvent('finalStart', [None])
        
    def finalCorrect(self):
        statusUpdate('Correct - ' + awnser)
        self.curRndCtrl.correct += 1
        self.curContestant.correctFinalQu(self.curRndCtrl.rQuestions)
        sendClientEvent('finalCorrectAns', [awnser])
        time.sleep(1)
        self.finalAns()
        
    def finalIncorrect(self):
        statusUpdate('Incorrect - ' + awnser)
        sendClientEvent('finalIncorrectAns', [awnser])
        time.sleep(1)
        #if head2head remove the first incorect awnsering contestant
        if self.curRndCtrl.rQuestions > config['questions']['finalRndQCnt']:
            self.removedContestants.append(self.contestants.pop(self.crtContestantIndex))
            statusUpdate(self.crtContestant.name + ' you are the Weakest Link! Goodbye')
            sendClientEvent('contestantEliminated', [self.crtContestant])
            time.sleep(1)
        else: #otherwise mark the question as incorectly awnsered
            self.curContestant.incorrectFinalQu(self.curRndCtrl.rQuestions)
            self.finalAns() #and go to the next question
    
    def finalAns(self):
        self.curRndCtrl.rQuestions += 1
        self.nextContestant()
        sendClientEvent('contestantUpdate', [self.contestants])
        
    def detFinalEnd(self):
        i = topScore = 0
        head2head = False
        while i < len(self.contestants):
            if self.contestants[i].score > topScore:
                topScore = self.contestants[i].score #get the top scoring contestant and store the score
            elif self.contestants[i].score == topScore and topScore != 0:
                head2head = True
            i += 1
        if head2head:
            statusUpdate('Going to Head to Head Round')
            sendClientEvent('headStart', [None])
            time.sleep(1)
        else:
            for contestant in self.contestants:
                if contestant.score != topScore:
                    statusUpdate(contestant.name + ' you are the Weakest Link! Goodbye')
                    sendClientEvent('contestantEliminated', [contestant])
                    self.removedContestants.append(self.contestants.pop(key))
                    time.sleep(1)
                    
    def isWinner(self):
        return len(self.contestants) == 1
                    
    def winner(self):
        statusUpdate(self.contestants[0].name + ' is the winner!')
        sendClientEvent('winner', [self.contestants[0]])
        
def questionGenerator(questions, start=0):
    questionCnt = len(questions)
    for i in range(start, questionCnt - 1)
        yield questions[i][0], questions[i][1], questions[i + 1][0], questions[i + 1][1]
    yield questions[questionCnt - 1][0], questions[questionCnt - 1][1], None, None #if there is only a single question left the next question can't be returned
        
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

def createQuestionGenerator(path, round=None):
    if round: #if it is a new round create the question generator for that round
        print('Importing Questions for Round ', round)
        return questionGenerator(getListFromColumn(importQuestions(path), 2, round))
    else:
        print('Importing Questions')
        return questionGenerator(importQuestions(path))
        
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
        self.end = False
        self.mainQ = os.path.join(path, "..\\", config['questions']['mainQ'])
        self.finalQ = os.path.join(path, "..\\", config['questions']['finalQ'])
    def run(self):
        global socketList
        self.gameController = gameControllerClass()
        while not self.end or self.gameController.checkFinalRound():
            if self.gameController.getRQuestionNo() == 1 and config['questions']['sortQuestions'] == True: #if it is a new round create the question generator for that round
                self.questionGenerator = createQuestionGenerator(mainQ, gameController.round)
            if not hasattr(self, 'questionGenerator'):
                self.questionGenerator = createQuestionGenerator(mainQ)
            
            question, awnser, nxtQuestion, nxtAwnser = next(self.questionGenerator)
            askQuestion(self.gameController.curContestant.name, question, awnser, self.gameController.round, self.getRQuestionNo(), self.gameController.nxtContestant.name, nxtQuestion, nxtAwnser)
            
            self.newQuestion = False
            sendClientEvent('responseWait', [None])
            while not self.newQuestion:
                receivedCommand = network.getMessageofType('quResponse', socketList, False)
                if receivedCommand and receivedCommand > 0 and receivedCommand <= 4 and questionHandler(receivedCommand, question, awnser, self.gameController) == True:
                    break
                    
                #goto question
                questionNo = network.getMessageofType('gotoQu', socketList, False)
                if questionNo and questionNo > 0 and questionNo <= len(questions):
                    self.questionGenerator = createQuestionGenerator(mainQ, questionNo)
                    break
                    
                #server acts as a relay for prompt message
                promptMessage = network.getMessageofType('promtMsg', socketList, False)
                if promptMessage:
                    for socketObj in socketList:
                        network.sendMessage('promtMsg', promptMessage, socketObj)
                        
        if not self.end:
            self.questionGenerator = createQuestionGenerator(finalQ)
            while True:
                question, awnser, nxtQuestion, nxtAwnser = next(self.questionGenerator)
                askFinalQuestion(self.gameController.curContestant.name, question, awnser, self.gameController.nxtContestant.name, nxtQuestion, nxtAwnser)
                sendClientEvent('responseWait', [None])
                while True:
                    receivedCommand = network.getMessageofType('quResponse', socketList)
                    if isinstance(receivedCommand, int) and receivedCommand > 0 and receivedCommand <= 2:
                        finalQuestionHandler(receivedCommand, question, awnser, self.gameController)
                        break
                        
                if gameController.isWinner()
                    gameController.winner()
                    self.end = True
                    break

def start():
    global listner, questionThread
    listner.stopListner(True)
    startFrame.grid_remove()
    mainFrame.grid()
    sendClientEvent('gameStart', [None])
    questionThread = questionControl()
    questionThread.start()

def initListner():
    global listner
    listner = serverListner()
    listner.start()

def initTk(parent):
    global displayStatus, startFrame, mainFrame, contestantTopLevel, listner
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
    #startTools.add_command(label='Goto Question...', command=gotoQuestion)
    #startTools.add_command(label='Edit Contestant List', command=editContestants)
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
    
    contestantTopLevel = Toplevel()
    contestantTopLevel.title(config['Tk']['window_title'])
    contestantTopLevel.resizable(False, False)
    contestantTopLevel.withdraw()
    
    contestantTopLevel.bind("<Return>", lambda event: updateContestants())
    contestantTopLevel.bind("<Escape>", lambda event: contestantTopLevel.withdraw())
    
    ttk.Button(contestantTopLevel, text='Update', command=updateContestants).grid(column=0, row=8, sticky=N)
    ttk.Button(contestantTopLevel, text='Cancel', command=contestantTopLevel.withdraw).grid(column=1, row=8, sticky=N)
    
    parent.protocol("WM_DELETE_WINDOW", lambda: close(parent))
    
    print('GUI Initiated')
    
# def gotoQuestion():
    # global questionThread
    # if variables['gamemode'] != -1:
        # questionNo = simpledialog.askinteger("Go to question...", "Question Number:")
        # if questionNo > 0 and questionNo <= len(questions):
            # variables['cntQuestions'] = questionNo
        # elif questionNo < 0 and abs(questionNo) <= len(questions) and variables['cntQuestions'] - questionNo <= len(questions):
            ##questionNo -ve -> addition
            # variables['cntQuestions'] -= questionNo
        # questionThread.newQuestion = True
    # else:
        # messagebox.showerror("Error", "Server has not Started Running Yet!")
    
# def editContestants():
    # global variables, contestantTopLevel, contestantNameEntry, contestantNameValues
    # contestantNameEntry = []
    # contestantNameValues = []
    # values wasn't working for some reason hence messy hack around
    # for i, contestant in zip(range(0, len(variables['contestants'])), [contestants for contestants, score in variables['contestants'].items()]):
        # contestantNameValues.append(StringVar())
        # contestantNameValues[i].set(contestant)
        # contestantNameEntry.append(ttk.Entry(contestantTopLevel, textvariable=contestantNameValues[i]))
        # contestantNameEntry[i].grid(column=0, row=i, columnspan=2, sticky=N)
    # contestantTopLevel.deiconify()
    
# def updateContestants():
    # global variables, contestantTopLevel, contestantNameEntry, contestantNameValues
    # values wasn't working for some reason hence messy hack around
    # contestantTopLevel.withdraw()
    # for contestantEntry, contestantNewName, contestantOldName in zip(contestantNameEntry, contestantNameValues, [contestants for contestants, score in variables['contestants'].items()]):
        # contestantEntry.grid_forget()
        # variables['contestants'][contestantNewName.get()] = variables['contestants'].pop(contestantOldName) 
    
def selectMainQuestionFile():
    global config
    file = filedialog.askopenfilename(title="Open Question File", initialdir=os.path.expanduser("~"), filetypes=[("CSV Files", "*.csv")])
    if file:
        config['questions']['mainQ'] = file
    misc.writeConfig(config)
    
def selectFinalQuestionFile():
    global config
    file = filedialog.askopenfilename(title="Open Question File", initialdir=os.path.expanduser("~"), filetypes=[("CSV Files", "*.csv")])
    if file:
        config['questions']['finalQ'] = file
    misc.writeConfig(config)

def close(topLevel):
    listner.stopListner(True)
    if 'questionThread' in globals():
        questionThread.newQuestion = questionThread.end = True
        questionThread.join()
    if topLevel.config()['class'][4] == 'Toplevel': topLevel.root.deiconify()
    topLevel.destroy()

def getListFromColumn(unsortedList, columnNo, value):
    sortedList = sorted(unsortedList, key=itemgetter(columnNo))
    returnList = []
    for i in range(0, len(sortedList)):
        if sortedList[i][columnNo] == value:
            break
    for j in range(i, len(sortedList)):
        if sortedList[j][columnNo] != value:
            break
        returnList.append(sortedList[j])
    return returnList
    
def cycleContestants(curContestantIndex, totalContestants):
    #cycle through each contestant in turn
    if curContestantIndex < totalContestants - 1:
        curContestantIndex += 1
    else:
        curContestantIndex = 0
        
    nxtContestantIndex = curContestantIndex
    if nxtContestantIndex < totalContestants - 1:
        nxtContestantIndex += 1
    else:
        nxtContestantIndex = 0
        
    return curContestantIndex, nxtContestantIndex
    
def askQuestion(curContestant, question, awnser, roundNo, rQuestionNo, nxtContestant, nxtQuestion, nxtAwnser):
    statusUpdate('Round ' + str(roundNo) + ' Question ' + str(rQuestionNo))
    statusUpdate(curContestant + ': ' + question)
    sendClientEvent('askQuestion', [rQuestionNo, curContestant, question, awnser])
    sendClientEvent('nxtQuestion', [rQuestionNo + 1, nxtContestant, nxtQuestion, nxtAwnser])

def questionHandler(event, question, awnser, gameController):
    global socketList
    if event == 1:
        gameController.correctAns(awnser)
    elif event == 2:
        gameController.incorrectAns(awnser)
    elif event == 3:
        gameController.bank()
        return False
    elif event == 4:
        gameController.timeUp()
    event = ''
    return True    
    
def askFinalQuestion(curContestant, question, awnser, nxtContestant, nxtQuestion, nxtAwnser):
    statusUpdate('Final Question ' + str(question))
    statusUpdate(curContestant + ': ' + question)
    sendClientEvent('askFinalQuestion', [curContestant, question, awnser])
    sendClientEvent('nxtFinalQuestion', [nxtContestant, nxtQuestion, nxtAwnser])
    
def finalQuestionHandler(event, question, awnser, gameController):
    global socketList
    if event == 1:
        gameController.finalCorrect()
    elif event == 2:
        gameController.finalIncorrect()
    if gameController.getRQuestionNo() == config['questions']['finalRndQCnt']: #if all final questions have been asked determine the winner or go head2head
        gameController.detFinalEnd()

def importQuestions(file):
    global status
    statusUpdate('Importing Questions...')
    questions = []
    cnt = 0
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1] and row[2]:
                questions.append([row[0], row[1], int(row[2])])
            elif row[0] and row[1]:
                questions.append([row[0], row[1]])
            cnt += 1
        statusUpdate('Imported ' + str(cnt) + ' Questions')
        # with statement automatically closes the csv file cleanly even in event of unexpected script termination
        return questions
    
def sendClientEvent(event, args):
    global socketList
    try:
        misc.log('Update Client')
    except:
        print('Update Client')
    for socketObj in socketList:
        network.sendMessage(event, args, socketObj)

def netTypesDeclaration():
    network.addUsedType('cmd')
    network.addUsedType('gotoQu')
    network.addUsedType('pmsg')
        
def setup():
    global config
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')
    netTypesDeclaration()
    varDeclaration()
        
if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    initListner()
    root.mainloop()
