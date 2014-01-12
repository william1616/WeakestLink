from tkinter import *
from tkinter import ttk
import threading, time, network, datetime

socket = network.initClientSocket()

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables
        while True:
            variables = network.getMessageofType('variables', [socket])
            status_update()
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
  
def status_update():
    global root
    root.quit()

def initTk():
    global root, startFrame, address, mainFrame, question, status, cur_money, bank, voteFrame, vote1name, vote2name, vote3name, vote4name, vote5name, vote6name, vote7name, vote8name
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

    vote1name = StringVar()
    vote2name = StringVar()
    vote3name = StringVar()
    vote4name = StringVar()
    vote5name = StringVar()
    vote6name = StringVar()
    vote7name = StringVar()
    vote8name = StringVar()

    vote1name.set('')
    vote2name.set('')
    vote3name.set('')
    vote4name.set('')
    vote5name.set('')
    vote6name.set('')
    vote7name.set('')
    vote8name.set('')

    ttk.Button(voteFrame, textvariable=vote1name, command=lambda: removeContestant(1)).grid(column=1, row=1, sticky=N)
    ttk.Button(voteFrame, textvariable=vote2name, command=lambda: removeContestant(2)).grid(column=2, row=1, sticky=N)
    ttk.Button(voteFrame, textvariable=vote3name, command=lambda: removeContestant(3)).grid(column=3, row=1, sticky=N)
    ttk.Button(voteFrame, textvariable=vote4name, command=lambda: removeContestant(4)).grid(column=4, row=1, sticky=N)
    ttk.Button(voteFrame, textvariable=vote5name, command=lambda: removeContestant(5)).grid(column=1, row=2, sticky=N)
    ttk.Button(voteFrame, textvariable=vote6name, command=lambda: removeContestant(6)).grid(column=2, row=2, sticky=N)
    ttk.Button(voteFrame, textvariable=vote7name, command=lambda: removeContestant(7)).grid(column=3, row=2, sticky=N)
    ttk.Button(voteFrame, textvariable=vote8name, command=lambda: removeContestant(8)).grid(column=4, row=2, sticky=N)
    
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
                voteFrame.grid()
        except:
            pass