from tkinter import *
from tkinter import ttk, messagebox, font
import os.path

path = os.path.dirname(__file__)
try:
    import network, misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("network", os.path.join(path, "network.py"))
    network = loader.load_module("network")
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

class timedLabel(ttk.Label):
    #grid on calling
    def __init__(self, frame, **kwargs):
        global mainTopLevel
        kwargs['background'] = 'red'
        kwargs['font'] = font.Font(family="Arial", size=12)
        super().__init__(frame, **kwargs)
        try:
            #run this function again in 1000ms
            if mainTopLevel.config()['class'][4] == 'Tk':
                mainTopLevel.after(5000, self.grid_forget)
            elif mainTopLevel.config()['class'][4] == 'Toplevel':
                mainTopLevel.root.after(5000, self.grid_forget)
        except TclError:
            #dont call the function again
            pass
    
def variableUpdates():
    global status, question, awnser, nextQuestion, nextAwnser, contestants, round, contestantList, mainFrame
    
    if network.messageInBuffer('rndStart'):
        [round] = network.getMessageofType('rndStart', False)
        status.set('Round ' + str(round) + ' starting')
        
    if network.messageInBuffer('askQuestion'):
        rQuestion, contestant, questionStr, awnserStr = network.getMessageofType('askQuestion', False)
        question.set(contestant + ': ' + questionStr)
        awnser.set(awnserStr)
        status.set('Round ' + str(round) + ' Question ' + str(rQuestion))
        
    if network.messageInBuffer('nxtQuestion'):
        nxtRQuestion, nxtContestant, nxtQuestionStr, nxtAwnserStr = network.getMessageofType('nxtQuestion', False)
        nextQuestion.set(nxtContestant + ': ' + nxtQuestionStr)
        nextAwnser.set(nxtAwnserStr)
        
    if network.messageInBuffer('rndScoreUpdate'):
        moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False)
        
    if network.getMessageofType('timeUp', False):
        timedLabel(mainFrame, text='Time Up! - You must now choose the Weakest Link!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S))
    
    if network.getMessageofType('allCorrect', False):
        timedLabel(mainFrame, text='All Questions Correct! - You must now choose the Weakest Link!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S))
        
    if network.messageInBuffer('contestantEliminated'):
        [lastEliminated] = network.getMessageofType('contestantEliminated', False)
        timedLabel(mainFrame, text=lastEliminated.name + ' has been eliminated!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S))
        
    if network.messageInBuffer('contestantUpdate'):
        contestantList = network.getMessageofType('contestantUpdate', False)
        contestants.set('\n'.join([': '.join([contestant.name, str(contestant.score)]) for contestant in contestantList]))
        
    # if network.getMessageofType('eliminationWait', False):
        # mainTopLevel.withdraw()
        # for i in range(0, 8):
            # try:
                # voteVar[i].set(contestantList[i].name)
            # except IndexError:
                # voteButton[i].grid_forget()
        # voteTopLevel.deiconify()
        
    if network.getMessageofType('finalStart', False):
        status.set('Final Round starting')
        
    if network.messageInBuffer('askFinalQuestion'):
        rQuestion, contestant, questionValue, awnserValue = network.getMessageofType('askFinalQuestion', False)
        question.set(contestant + ': ' + questionValue)
        awnser.set(awnserValue)
        status.set('Final Question ' + str(rQuestion))
        
    if network.messageInBuffer('nxtFinalQuestion'):
        nxtRQuestion, nxtContestant, nxtQuestion, nxtAwnser = network.getMessageofType('nxtFinalQuestion', False)
        nextQuestion.set(nxtContestant + ': ' + nxtQuestion)
        nextAwnser.set(nxtAwnser)
        
    if network.getMessageofType('headStart', False):
        status.set('Going to Head to Head Round')
        
    if network.messageInBuffer('winner'):
        [winner] = network.getMessageofType('winner', False)
        status.set(winner.name + ' is the winner!')
        timedLabel(mainFrame, text=winner.name + ' is the Winner!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S))
            
    if network.messageInBuffer('promtMsg'):
        timedLabel(mainFrame, text=network.getMessageofType('promtMsg', False)).grid(column=1, row=4, columnspan=3, sticky=(W, N, S))
    
    try:
        #run this function again in 1000ms
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(1000, variableUpdates)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, variableUpdates)
    except TclError:
        #dont call the function again
        pass
    
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
    global mainTopLevel
    if network.getMessageofType('gameStart', False): #if no longer listning for conections
        network.addUsedType('rndStart')
        network.addUsedType('askQuestion')
        network.addUsedType('nxtQuestion')
        network.addUsedType('rndScoreUpdate')
        network.addUsedType('timeUp')
        network.addUsedType('contestantEliminated')
        network.addUsedType('allCorrect')
        network.addUsedType('contestantUpdate')
        network.addUsedType('finalStart')
        network.addUsedType('askFinalQuestion')
        network.addUsedType('nxtFinalQuestion')
        network.addUsedType('headStart')
        network.addUsedType('winner')
        network.addUsedType('promtMsg')
        network.removeUsedType('gameStart')
        waitFrame.grid_forget()
        mainFrame.grid()
        variableUpdates()
    else:
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, isServerRunning)
        
def initTk(parent):
    global address, startFrame, waitFrame, mainFrame, mainTopLevel, status, question, awnser, nextQuestion, nextAwnser, contestants
    
    mainTopLevel = parent
    
    mainFont = font.Font(family="Arial", size=12)
    titleFont = font.Font(family="Arial", size=16, underline=True)
    
    startFrame = ttk.Frame(parent, padding="3 3 3 3")
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
    mainFrame.grid_remove()
    
    status = StringVar()
    question = StringVar()
    awnser = StringVar()
    nextQuestion = StringVar()
    nextAwnser = StringVar()
    contestants = StringVar()
    message = StringVar()
    
    columnWidth = 25
    wrapMultipilcationConst = 9
    wrapWidth = columnWidth * wrapMultipilcationConst
    
    ttk.Label(mainFrame, textvariable=status, font=titleFont).grid(column=0, row=0, columnspan=4, sticky=N)
    ttk.Label(mainFrame, text="Question", width=columnWidth, font=titleFont).grid(column=1, row=1, sticky=(W, N))
    ttk.Label(mainFrame, text="Awnser", width=columnWidth, font=titleFont).grid(column=2, row=1, sticky=(W, N))
    ttk.Label(mainFrame, text="Current", font=titleFont).grid(column=0, row=2, sticky=(W, N))
    ttk.Label(mainFrame, text="Next", font=titleFont).grid(column=0, row=3, sticky=(W, N))
    ttk.Label(mainFrame, textvariable=question, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=1, row=2, sticky=(W, N))
    ttk.Label(mainFrame, textvariable=awnser, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=2, row=2, sticky=(W, N))
    ttk.Label(mainFrame, textvariable=nextQuestion, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=1, row=3, sticky=(W, N))
    ttk.Label(mainFrame, textvariable=nextAwnser, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=2, row=3, sticky=(W, N))
    ttk.Label(mainFrame, text="Contestants", font=titleFont).grid(column=3, row=1, sticky=(W, N))
    ttk.Label(mainFrame, textvariable=contestants, font=mainFont).grid(column=3, row=2, rowspan=2, sticky=(W, N))
    ttk.Label(mainFrame, text="Messages", font=titleFont).grid(column=0, row=4, sticky=N)
    #timedLabels).grid(column=1, row=4, columnspan=3, sticky=(W, N, S))
    ttk.Label(mainFrame, text="Game Updates", font=titleFont).grid(column=0, row=5, sticky=N)
    #timedLabels.grid(column=1, row=5, columnspan=3, sticky=(W, N, S))
    
    mainMenu = Menu(parent)
    parent['menu'] = mainMenu
    startFile = Menu(mainMenu, tearoff=0)
    startTools = Menu(mainMenu, tearoff=0)
    startHelp = Menu(mainMenu, tearoff=0)
    mainMenu.add_cascade(menu=startFile, label='File')
    mainMenu.add_cascade(menu=startTools, label='Tools')
    mainMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=close)
    
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    waitFrame = ttk.Frame(parent, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    parent.protocol("WM_DELETE_WINDOW", close)
    
def close():
    global mainTopLevel
    if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify()
    mainTopLevel.destroy()
    
def setup():
    global config, socket
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')
    socket = network.initClientSocket()

if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    root.mainloop()
