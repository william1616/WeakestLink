from tkinter import *
from tkinter import ttk
import socket, threading, select, json, time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables, clientsocket
        while True:
            readable, writable, err = select.select([clientsocket.fileno()], [], [], 1)
            if readable:
                msg = clientsocket.recv(4096)
                #check = self.clientsocket.recv(40).decode('UTF-8')
                #assert(hashlib.sha1(msg).hexdigest() == check)
                variables = json.loads(msg.decode('UTF-8'))
                status_update()
            if self.end == True:
                break
    def join(self):
            self.end = True       

def send(msg):
    global clientsocket
    msg = json.dumps(msg).encode('UTF-8')
    clientsocket.send(msg)

def start():
    global clientsocket, voteFrame, mainFrame
    try:
        print('Attempting to connect to ' + address.get())
        clientsocket.connect((address.get(),1024))
    except:
        print('Failed to connect to ' + address.get())
        return
    receive = listner()
    receive.start()
    startFrame.grid_remove()
    mainFrame.grid()

def removeContestant(contestantIndex):
    global voteFrame, mainFrame
    voteFrame.grid_remove()
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    send(contestantIndex)
  
def status_update():
    global voteFrame, mainFrame, status, question, cur_money, bank
    print('gamemode: ' + str(variables['gamemode']))
    if variables['gamemode'] == 0:
	voteFrame.grid_remove()
        status.set('Round ' + str(variables['cntRounds']) + ' starting')
        mainFrame.grid()
    if variables['gamemode'] == 1:
	voteFrame.grid_remove()
        status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
        cur_money.set(list(variables['money'])[variables['correct']])
        bank.set(variables['bank'])
        mainFrame.grid()
    elif variables['gamemode'] == 2:
        mainFrame.grid_remove()
        voteFrame.grid()

root = Tk()
root.title("Control")

startFrame = ttk.Frame(root, padding="3 3 3 3")
startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
startFrame.columnconfigure(0, weight=1)
startFrame.rowconfigure(0, weight=1)
startFrame.grid_remove()

address = StringVar()

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
ttk.Button(mainFrame, text="Correct", command=lambda: send(1)).grid(column=2, row=1, sticky=N)
ttk.Button(mainFrame, text="Incorrect", command=lambda: send(2)).grid(column=2, row=2, sticky=N)
ttk.Button(mainFrame, text="Bank", command=lambda: send(3)).grid(column=3, row=2, sticky=N)
ttk.Button(mainFrame, text="Time Up", command=lambda: send(4)).grid(column=3, row=1, sticky=N)

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

ttk.Button(voteFrame, textvariable=vote1name, command=lambda: removeContestant(1)).grid(column=1, row=1, sticky=N)
ttk.Button(voteFrame, textvariable=vote2name, command=lambda: removeContestant(2)).grid(column=2, row=1, sticky=N)
ttk.Button(voteFrame, textvariable=vote3name, command=lambda: removeContestant(3)).grid(column=3, row=1, sticky=N)
ttk.Button(voteFrame, textvariable=vote4name, command=lambda: removeContestant(4)).grid(column=4, row=1, sticky=N)
ttk.Button(voteFrame, textvariable=vote5name, command=lambda: removeContestant(5)).grid(column=1, row=2, sticky=N)
ttk.Button(voteFrame, textvariable=vote6name, command=lambda: removeContestant(6)).grid(column=2, row=2, sticky=N)
ttk.Button(voteFrame, textvariable=vote7name, command=lambda: removeContestant(7)).grid(column=3, row=2, sticky=N)
ttk.Button(voteFrame, textvariable=vote8name, command=lambda: removeContestant(8)).grid(column=4, row=2, sticky=N)

startFrame.grid()
root.mainloop()
