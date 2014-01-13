from tkinter import *
from tkinter import ttk
import threading, time, network, datetime, math

socket = network.initClientSocket()

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables, root
        while True:
            variables = network.getMessageofType('variables', [socket])
            root.quit()
            if self.end == True:
                break
    def join(self):
            self.end = True

def start():
    global socket, voteFrame, mainFrame
    if network.attemptConnect(socket, address.get(), 1024):
        receive = listner()
        receive.start()
        startFrame.grid_remove()
        mainFrame.grid()

def removeContestant(contestantIndex):
    global voteFrame, mainFrame, socket
    voteFrame.grid_remove()
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    network.sendMessage('cmd', contestantIndex, socket)

def initTk():
    global root, startFrame, address, mainFrame, question, status, cur_money, bank, voteFrame, voteVar, voteButton
    root = Tk()
    root.title("Control")

    startFrame = ttk.Frame(root, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)
    startFrame.grid_remove()

    address = StringVar()
    address.set('localhost')

    ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text="Exit", command=root.destroy).grid(column=2, row=2, sticky=N)
    ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N)

    mainFrame = ttk.Frame(root, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)
    mainFrame.grid_remove()

    question = StringVar()
    status = StringVar()
    cur_money = IntVar()
    bank = IntVar()

    ttk.Label(mainFrame, textvariable=status, width=100, background='red').grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=question, width=100).grid(column=1, row=2, sticky=N)
    ttk.Label(mainFrame, text='Money: ').grid(column=4, row=1, sticky=N)
    ttk.Label(mainFrame, text='Bank: ').grid(column=4, row=2, sticky=N)
    ttk.Label(mainFrame, textvariable=cur_money).grid(column=5, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=bank).grid(column=5, row=2, sticky=N)
    ttk.Button(mainFrame, text="Correct", command=lambda: network.sendMessage('cmd', 1, socket)).grid(column=2, row=1, sticky=N)
    ttk.Button(mainFrame, text="Incorrect", command=lambda: network.sendMessage('cmd', 2, socket)).grid(column=2, row=2, sticky=N)
    ttk.Button(mainFrame, text="Bank", command=lambda: network.sendMessage('cmd', 3, socket)).grid(column=3, row=2, sticky=N)
    ttk.Button(mainFrame, text="Time Up", command=lambda: network.sendMessage('cmd', 4, socket)).grid(column=3, row=1, sticky=N)
    
    voteFrame = ttk.Frame(root, padding="3 3 3 3")
    voteFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    voteFrame.columnconfigure(0, weight=1)
    voteFrame.rowconfigure(0, weight=1)
    voteFrame.grid_remove()
    
    voteVar = []
    voteButton = []
    
    for i in range(0, 8):
        voteVar.append(StringVar())
        voteButton.append(ttk.Button(voteFrame, textvariable=voteVar[i], command=lambda index=i: removeContestant(index)))
        voteButton[i].grid(column=i % 4, row=math.ceil((1 + i) / 4), sticky=N)
    
if __name__ == '__main__':
    mainLoop = True
    initTk()
    startFrame.grid()
    while True:
        root.mainloop()
        try:
            if variables['gamemode'] == 0:
                voteFrame.grid_remove()
                status.set('Round ' + str(variables['cntRounds']) + ' starting')
                mainFrame.grid()
            elif variables['gamemode'] == 1:
                voteFrame.grid_remove()
                status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
                question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
                cur_money.set(list(variables['money'])[variables['correct']])
                bank.set(variables['bank'])
                mainFrame.grid()
            elif variables['gamemode'] == 2:
                mainFrame.grid_remove()
                contestantList = list(variables['contestants'].keys())
                for i in range(0, 8):
                    try:
                        voteVar[i].set(contestantList[i])
                    except IndexError:
                        voteButton[i].grid_forget()
                voteFrame.grid()
        except:
            pass