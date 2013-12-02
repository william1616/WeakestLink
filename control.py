from tkinter import *
from tkinter import ttk
import socket, threading, select, json, time, hashlib

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
uID = 0
messages = {}
check = {}

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables, clientsocket, messages, check
        while True:
            temp, index = receiveCommand([clientsocket])
            if temp['name'] == 'variables':
                    variables = temp
                    messages.pop(index)
                    check.pop(index)
                    status_update()
                    print('wow')
            if self.end == True:
                break
    def join(self):
            self.end = True

def receiveCommand(socketList, loop=True):
    global messages, check, uID
    received = []
    while loop:
        for socket in socketList:
            readable, writable, err = select.select([socket.fileno()], [], [], 0.1)
            if readable:
                received = clientsocket.recv(4096).split(b'|')
                while received.count(b'') > 0:
                  received.remove(b'')
                for i in range(0, len(received)):
                  if i % 2 == 0:
                    messages[uID] = json.loads(received[i].decode('UTF-8'))
                  if i % 2 == 1:
                    check[uID] = json.loads(received[i].decode('UTF-8'))
                  uID += 1
        for key in list(messages.keys()):
            print(hashlib.sha1(messages[key]).hexdigest())
            print(check[key])
            if hashlib.sha1(messages[key]).hexdigest() == check[key]:
                send({'name': 'check', 'check': check[key]}, socket, False)
                return messages[key], key
            else:
                messages.pop(key)
                check.pop(key)

def send(msg, socket, doCheck=True):
    msg = json.dumps(msg).encode('UTF-8')
    check = json.dumps(hashlib.sha1(msg).hexdigest()).encode('UTF-8')
    socket.send(b'|' + msg + b'|' + check + b'|')
    while doCheck:
        temp, index = receiveCommand([socket], False)
        if temp['name'] == 'check':
            if temp['check'] == check:
                messages.pop(index)
                check.pop(index)
                break
        socket.send(b'|' + msg + b'|' + check + b'|')

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
    global voteFrame, mainFrame, clientsocket
    voteFrame.grid_remove()
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    send({'name': 'control', 'signal': contestantIndex}, clientsocket)
  
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
ttk.Button(mainFrame, text="Correct", command=lambda: send({'name': 'control', 'signal': 1}, clientsocket)).grid(column=2, row=1, sticky=N)
ttk.Button(mainFrame, text="Incorrect", command=lambda: send({'name': 'control', 'signal': 2}, clientsocket)).grid(column=2, row=2, sticky=N)
ttk.Button(mainFrame, text="Bank", command=lambda: send({'name': 'control', 'signal': 3}, clientsocket)).grid(column=3, row=2, sticky=N)
ttk.Button(mainFrame, text="Time Up", command=lambda: send({'name': 'control', 'signal': 4}, clientsocket)).grid(column=3, row=1, sticky=N)

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
