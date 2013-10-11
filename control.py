from tkinter import *
from tkinter import ttk
import socket
import threading
import select
import json
import time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables
        while True:
            print('receive loop')
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
    msg = json.dumps(msg).encode('UTF-8')
    clientsocket.send(msg)

def correctAns():
    send(1)

def incorrectAns():
    send(2)
    
def bankEvent():
    send(3)

def timeEvent():
    send(4)

def start():
    global startButton, correctButtton, incorrectButtton, timeButtton, bankButtton, clientsocket
    try:
        print('Attempting to connect to ' + address.get())
        clientsocket.connect((address.get(),1024))
    except:
        print('Failed to connect to ' + address.get())
        return
    receive = listner()
    receive.start()
    startButton.grid_forget()
    addressEntry.grid_forget()
    addressLabel.grid_forget()
    correctButton.grid(column=2, row=1, sticky=N)
    incorrectButton.grid(column=2, row=2, sticky=N)
    timeButton.grid(column=3, row=1, sticky=N)
    bankButton.grid(column=3, row=2, sticky=N)
    statusValue.grid(column=1, row=1, sticky=N)
    questionValue.grid(column=1, row=2, sticky=N)
    moneyLabel.grid(column=4, row=1, sticky=N)
    bankLabel.grid(column=4, row=2, sticky=N)
    moneyValue.grid(column=5, row=1, sticky=N)
    bankValue.grid(column=5, row=2, sticky=N)   

root = Tk()
root.title("Control")

mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

question = StringVar()
status = StringVar()
cur_money = IntVar()
bank = IntVar()
address = StringVar()

statusValue = ttk.Label(mainframe, textvariable=status, width=100, background='red')
questionValue = ttk.Label(mainframe, textvariable=question, width=100)
moneyLabel = ttk.Label(mainframe, text='Money: ')
bankLabel = ttk.Label(mainframe, text='Bank: ')
moneyValue = ttk.Label(mainframe, textvariable=cur_money)
bankValue = ttk.Label(mainframe, textvariable=bank)

startButton = ttk.Button(mainframe, text="Connect", command=start)
startButton.grid(column=1, row=2, sticky=N)
exitButton = ttk.Button(mainframe, text="Exit", command=root.destroy)
exitButton.grid(column=2, row=2, sticky=N)
addressEntry = ttk.Entry(mainframe, textvariable=address)
addressEntry.grid(column=1, row=1, sticky=N)
addressLabel = ttk.Label(mainframe, text="Server IP address")
addressLabel.grid(column=2, row=1, sticky=N)
correctButton = ttk.Button(mainframe, text="Correct", command=correctAns)
incorrectButton = ttk.Button(mainframe, text="Incorrect", command=incorrectAns)
timeButton = ttk.Button(mainframe, text="Time Up", command=timeEvent)
bankButton = ttk.Button(mainframe, text="Bank", command=bankEvent)

def status_update():
    if variables['cntRquestions'] == 1:
        status.set('Round ' + str(variables['cntRounds']) + ' starting')
        time.sleep(1)
    status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
    question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
    cur_money.set(list(variables['money'])[variables['correct']])
    bank.set(variables['bank'])

root.mainloop()
