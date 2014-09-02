from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
from math import ceil
from sharedClasses import contestantClass
import time, os.path, network, misc, sharedClasses

socket = network.initClientSocket()
running = False

def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        network.addUsedType('gameStart')
        isServerRunning()
    else:
        messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"")

def isServerRunning():
    global socket, startTopLevel, mainTopLevel, running
    if network.getMessageofType('gameStart', False): #if no longer listning for conections
        network.addUsedType('rndStart')
        network.addUsedType('askQuestion')
        network.addUsedType('responseWait')
        network.addUsedType('rndScoreUpdate')
        network.addUsedType('contestantUpdate')
        network.addUsedType('eliminationWait')
        network.addUsedType('finalStart')
        network.addUsedType('askFinalQuestion')
        network.addUsedType('headStart')
        network.addUsedType('winner')
        network.removeUsedType('gameStart')
        variableUpdates()
        startTopLevel.withdraw()
        mainTopLevel.deiconify()
        running = True
    else:
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, isServerRunning)

def toggleContestant(contestantClass):
    global socket, voteTopLevel
    disableButton()
    if contestantClass.uuid in [contestant.uuid for contestant in contestantList]:
        if messagebox.askokcancel("Confirm", "Remove " + contestantClass.name + " from the Game?", parent=voteTopLevel):
            network.sendMessage("removeContestant", contestantClass.uuid, socket)
    else:
        if messagebox.askokcancel("Confirm", "Re-add " + contestantClass.name + " to the Game?", parent=voteTopLevel):
            network.sendMessage("addContestant", contestantClass.uuid, socket)
    
def sendQuestionResponse(response):
    global socket
    disableButton()
    network.sendMessage('quResponse', response, socket)
    
def enableButton():
    global mainButton
    misc.log('enable button')
    for key, value in mainButton.items():
        misc.log('enabled ' + key)
        value.config(state='normal')
        
def disableButton():
    global mainButton
    misc.log('disable button')
    for key, value in mainButton.items():
        misc.log('disabled ' + key)
        value.config(state='disabled')
        
def initTk(parent):
    global address, mainQuestion, status, cur_money, bank, voteVar, voteButton, voteScore, voteLabel, config, startFrame, startTopLevel, mainTopLevel, voteTopLevel, waitFrame, mainFrame, finalFrame, mainButton, finalQuestion, finalStatus, finalName1, finalName2, finalScore1, finalScore2

    mainTopLevel = parent
    parent.title(config['Tk']['window_title'])
    parent.resizable(False, False)
    parent.withdraw()
    
    startTopLevel = Toplevel(parent)
    startTopLevel.title(config['Tk']['window_title'])
    startTopLevel.resizable(False, False)
    
    startMenu = Menu(startTopLevel)
    startTopLevel['menu'] = startMenu
    startFile = Menu(startMenu, tearoff=0)
    startTools = Menu(startMenu, tearoff=0)
    startHelp = Menu(startMenu, tearoff=0)
    startMenu.add_cascade(menu=startFile, label='File')
    startMenu.add_cascade(menu=startTools, label='Tools')
    startMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=close)
    
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    startTools.add_command(label='Send Message to Prompt', command=promptMessage)
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    startFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)
    
    address = StringVar()
    address.set(config['server']['bindAddress'])
    
    ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N)
    ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N)

    mainFrame = ttk.Frame(parent, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)

    mainQuestion = StringVar()
    status = StringVar()
    cur_money = IntVar()
    bank = IntVar()

    ttk.Label(mainFrame, textvariable=status, width=100, background='red').grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=mainQuestion, width=100).grid(column=1, row=2, sticky=N)
    ttk.Label(mainFrame, text='Money: ').grid(column=4, row=1, sticky=N)
    ttk.Label(mainFrame, text='Bank: ').grid(column=4, row=2, sticky=N)
    ttk.Label(mainFrame, textvariable=cur_money).grid(column=5, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=bank).grid(column=5, row=2, sticky=N)
    
    mainButton = {}
    
    mainButton['correct'] = ttk.Button(mainFrame, text="Correct", command=lambda: sendQuestionResponse(1))
    mainButton['correct'].grid(column=2, row=1, sticky=N)
    mainButton['incorrect'] = ttk.Button(mainFrame, text="Incorrect", command=lambda: sendQuestionResponse(2))
    mainButton['incorrect'].grid(column=2, row=2, sticky=N)
    mainButton['bank'] = ttk.Button(mainFrame, text="Bank", command=lambda: sendQuestionResponse(3))
    mainButton['bank'].grid(column=3, row=2, sticky=N)
    mainButton['time'] = ttk.Button(mainFrame, text="Time Up", command=lambda: sendQuestionResponse(4))
    mainButton['time'].grid(column=3, row=1, sticky=N)
    
    mainMenu = Menu(mainTopLevel)
    mainTopLevel['menu'] = mainMenu
    mainFile = Menu(mainMenu, tearoff=0)
    mainTools = Menu(mainMenu, tearoff=0)
    mainHelp = Menu(mainMenu, tearoff=0)
    mainMenu.add_cascade(menu=mainFile, label='File')
    mainMenu.add_cascade(menu=mainTools, label='Tools')
    mainMenu.add_cascade(menu=mainHelp, label='Help')
    
    mainFile.add_command(label='Exit', command=close)
    
    mainTools.add_command(label='Goto Question...', command=gotoQuestion)
    mainTools.add_command(label='Send Message to Prompt', command=promptMessage)
    
    mainHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    finalFrame = ttk.Frame(parent, padding="3 3 3 3")
    finalFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    finalFrame.columnconfigure(0, weight=1)
    finalFrame.rowconfigure(0, weight=1)
    finalFrame.grid_remove()

    finalQuestion = StringVar()
    finalStatus = StringVar()
    finalName1 = StringVar()
    finalName2 = StringVar()
    finalScore1 = IntVar()
    finalScore2 = IntVar()

    ttk.Label(finalFrame, textvariable=finalStatus, width=100, background='red').grid(column=1, row=1, sticky=N)
    ttk.Label(finalFrame, textvariable=finalQuestion, width=100).grid(column=1, row=2, sticky=N)
    ttk.Label(finalFrame, textvariable=finalName1).grid(column=5, row=1, sticky=N)
    ttk.Label(finalFrame, textvariable=finalName2).grid(column=5, row=2, sticky=N)
    ttk.Label(finalFrame, textvariable=finalScore1).grid(column=6, row=1, sticky=N)
    ttk.Label(finalFrame, textvariable=finalScore2).grid(column=6, row=2, sticky=N)
    
    mainButton['finalCorrect'] = ttk.Button(finalFrame, text="Correct", command=lambda: sendQuestionResponse(1))
    mainButton['finalCorrect'].grid(column=2, row=1, sticky=N)
    mainButton['finalIncorrect'] = ttk.Button(finalFrame, text="Incorrect", command=lambda: sendQuestionResponse(2))
    mainButton['finalIncorrect'].grid(column=2, row=2, sticky=N)
    
    voteTopLevel = Toplevel(parent)
    voteTopLevel.title(config['Tk']['window_title'])
    voteTopLevel.resizable(False, False)
    
    voteFrame = ttk.Frame(voteTopLevel, padding="3 3 3 3")
    voteFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    voteFrame.columnconfigure(0, weight=1)
    voteFrame.rowconfigure(0, weight=1)
    
    ttk.Label(voteFrame, text="Contestants").grid(column=0, row=0)
    ttk.Label(voteFrame, text="Score").grid(column=1, row=0)
    
    voteVar = []
    voteButton = []
    voteScore = []
    voteLabel = []
    
    for i in range(0, 8):
        voteVar.append(StringVar())
        voteScore.append(IntVar())
        voteLabel.append(ttk.Label(voteFrame, textvariable=voteScore[i]))
        voteLabel[i].grid(column=1, row=i+1, sticky=N)
        voteButton.append(ttk.Button(voteFrame, textvariable=voteVar[i]))
        voteButton[i].grid(column=0, row=i+1, sticky=N)
        voteButton[i].config(state='disabled')
        
    waitFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    mainTopLevel.protocol("WM_DELETE_WINDOW", close)
    startTopLevel.protocol("WM_DELETE_WINDOW", close)
    voteTopLevel.protocol("WM_DELETE_WINDOW", close)
   
def promptMessage():
    global socket
    message = simpledialog.askstring("Send Message to Prompt", "Message:")
    network.sendMessage('promptMsg', message, socket)
    
def gotoQuestion():
    global socket, running
    if running:
        questionNo = simpledialog.askinteger("Go to question...", "Question Number:")
        if questionNo:
            disableButton()
            network.sendMessage('gotoQu', questionNo, socket)
    else:
        messagebox.showerror("Error", "Server has not Started Running Yet!")
    
def selectMainQuestionFile():
    global config
    #this needs to be transmitted to server and validated
    config['questions']['mainQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def selectFinalQuestionFile():
    global config
    #this needs to be transmitted to server and validated
    config['questions']['finalQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def close():
    global mainTopLevel, startTopLevel, voteTopLevel
    startTopLevel.destroy()
    voteTopLevel.destroy()
    if mainTopLevel.config()['class'][4] == 'Toplevel': 
        mainTopLevel.root.deiconify()
    mainTopLevel.destroy()
    
def variableUpdates():
    global mainQuestion, status, cur_money, bank, round, contestantList, mainTopLevel, startTopLevel, mainFrame, finalFrame, voteVar, voteScore, voteButton, voteLabel
    
    if network.messageInBuffer('rndStart'):
        [round] = network.getMessageofType('rndStart', False)
        status.set('Round ' + str(round) + ' starting')
        
    if network.messageInBuffer('askQuestion'):
        rQuestion, contestant, question, answer = network.getMessageofType('askQuestion', False)
        status.set('Round ' + str(round) + ' Question ' + str(rQuestion))
        mainQuestion.set(contestant + ': ' + question)
        
    if network.getMessageofType('responseWait', False):
        enableButton()
        
    if network.messageInBuffer('rndScoreUpdate'):
        moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False)
        cur_money.set(money[moneyCount])
        bank.set(bankVal)
        
    if network.messageInBuffer('contestantUpdate'):
        contestantList = network.getMessageofType('contestantUpdate', False)
        for i in range(0, 8):
            try:
                voteVar[i].set(contestantList[i].name)
                voteScore[i].set(contestantList[i].score)
                voteButton[i].config(command=lambda contestantClass=contestantList[i]: toggleContestant(contestantClass), state='disabled')
            except IndexError:
                voteButton[i].grid_forget()
                voteLabel[i].grid_forget()
        
    if network.getMessageofType('eliminationWait', False):
        for i in range(0, 8):
            voteButton[i].config(state='normal')
        
    if network.getMessageofType('finalStart', False):
        mainFrame.grid_remove()
        finalStatus.set('Final Round starting')
        finalFrame.grid()
        
    if network.messageInBuffer('askFinalQuestion'):
        rQuestion, contestant, question, answer = network.getMessageofType('askFinalQuestion', False)
        finalStatus.set('Final Question ' + str(rQuestion))
        finalQuestion.set(contestant + ': ' + question)
        if finalName1.get() == '':
            finalName1.set(contestantList[0].name)
            finalName2.set(contestantList[1].name)
        finalScore1.set(contestantList[0].score)
        finalScore2.set(contestantList[1].score)
        
    if network.getMessageofType('headStart', False):
        finalStatus.set('Going to Head to Head Round')
        finalQuestion.set('')
        
    if network.messageInBuffer('winner'):
        [winner] = network.getMessageofType('winner', False)
        finalStatus.set(winner.name + ' is the winner!')
        finalQuestion.set('')
        
    try:
        #run this function again in 1000ms
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, variableUpdates)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, variableUpdates)
    except TclError:
        #dont call the function again
        pass

def setup():
    global config
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')

if __name__ == '__main__':
    setup()
    root = Tk()
    initTk(root)
    root.mainloop()
