from tkinter import *
from tkinter import ttk
import csv
import socket
import hashlib
import threading
import time
import select
import sys
import json

window_title = 'The Weakest Link'
status_lines = 10
mainQ = 'questions.csv'
finalQ = 'questions.csv'
variables = {}
variables['cntQuestions'] = 0
variables['correct'] = 0
variables['cntRounds'] = 1
variables['cntRquestions'] = 1
variables['bank'] = 0
variables['question'] = ''
variables['contestants'] = ['bill','ben','bob','cat','hat','matt','mouse','man']
variables['money'] = [0, 50,100,200,300,400,500,1000,2500,5000]
questions = []
status = []
questions = []
peripherals = []

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 1024))
serversocket.listen(5)
serversocket.setblocking(False)

def status_update():
	i = 0
	start_status.set('')
	while True:
		if i == len(status): break
		if i > len(status) - status_lines:
			start_status.set(start_status.get()+status[i]+'\n')
		i += 1

class connectListner (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.end = False
	def run(self):
		while True:
			print('loop')
			readable, writable, err = select.select([serversocket.fileno()], [], [], 1)
			if readable:
					clientsocket, address = serversocket.accept()
					status.append(address[0] + ' Succesfully Connected')
					status_update()
					peripherals.append(clientsocket)
			if self.end == True:
				break
	def join(self):
			self.end = True

# msg = clientsocket.receive(4096)
# check = clientsocket.receive(40).decode()
# if hashlib.sha1(msg).hexdigest() == check:
	# status.append('Succesfully received message from ' + address)
# else:
	# status.append('message from ' + address + ' did not transmit properly')
# status_update()

def start():
	disconnect()
	startFrame.grid_forget()
	mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
	askQuestion()
	updateClient()

def connect():
        global listner
        listner = connectListner()
        listner.start()
        status.append('Started Listner')
        status_update()
        
def disconnect():
	global listner
	if listner.isAlive():
		listner.join()
		status.append('Stopped Listner')
		status_update()

root = Tk()
root.title(window_title)

startFrame = ttk.Frame(root, padding="3 3 3 3")
startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
startFrame.columnconfigure(0, weight=1)
startFrame.rowconfigure(0, weight=1)

mainFrame = ttk.Frame(root, padding="3 3 3 3")
mainFrame.columnconfigure(0, weight=1)
mainFrame.rowconfigure(0, weight=1)

start_status = StringVar()

ttk.Label(startFrame, text='Status', font=font.Font(size=16, underline=True)).grid(column=1, row=1, sticky=N)
ttk.Label(startFrame, textvariable=start_status, width=100).grid(column=1, row=2, sticky=N)
ttk.Button(startFrame, text='Start', command=start).grid(column=2, row=1, sticky=N)
ttk.Button(startFrame, text='Start Listner', command=connect).grid(column=2, row=2, sticky=N)
ttk.Button(startFrame, text='Stop Listner', command=disconnect).grid(column=2, row=3, sticky=N)

ttk.Label(mainFrame, text='Status', width=100).grid(column=1, row=1, sticky=N)
ttk.Label(mainFrame, textvariable=start_status, width=100).grid(column=1, row=2, sticky=N)

def askQuestion():
    global questions, mainQ, variables 
    importQuestions(mainQ)
    #cntContestants = len(variables[1][variables[0].index('contestants')]) + 1
    if variables['cntQuestions'] < len('questions'):
        if variables['cntRquestions'] == 1:
                status.append('Round ' + str(variables['cntRounds']) + ' starting')
                status_update()
                time.sleep(1)
        status.append('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        status.append(questions[variables['cntQuestions']][0])
        variables['question'] = questions[variables['cntQuestions']][0]
        status_update()
    else:
        status.append('So this is Embarasing')
        status.append('We seam to have run out of questions')
        status.append('Exiting...')
        status_update()
        sys.exit()

def questionHandler(event):
    global questions, variables
    if event == 1:
        status.append('Correct')
        correct += 1
    elif event == 2:
        status.append('Incorrect - ' + questions[variables['cntQuestions']][1])
        correct = 0
    elif event == 3:
        variables['bank'] += variables['money'][variables['correct']]
        status.append('Banked £' + str(variables['money'][variables['correct']]))
        status.append('£' + str(variables['bank']) + ' now in bank')
        variables['correct'] = 0
        status.append('You now have £' + variables['money'][variables['correct']])
        #variables[1][variables[0].index('cntQuestions')] =- 1 double check if this is needed?
        return
    elif event == 4:
        status.append('Time Up')
        status.append('You have £' + str(variables['bank']) + ' in the bank')
        variables['cntRounds'] += 1
        variables['correct'] = variables['cntRquestions'] = 0
    event = ''
    variables['cntRquestions'] += 1
    variables['cntQuestions'] += 1
    status.append('You now have £' + str(variables['money'][variables['correct']]))
    if correct == len(money) - 1:
        status.append('You have got all questions in round ' + str(variables['cntRounds']) + ' correct')
        variables['cntRounds'] += 1
        variables['cntRquestions'] = 1
        variables['correct'] = 0
    status_update()
##    if cntRquestions == 1:
##        print('You must now choose the Weakest Link')
##        i = 1
##        while i - 1 < len(contestants):
##            print(str(i) + '\t' + contestants[i-1])
##            i += 1
##        contestants.remove(contestants[int(input('Please enter a selection (1 - ' + str(len(contestants)) + ')\n')) - 1])

def importQuestions(file):
    global questions
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1]:
                questions.append([row[0], row[1]])
    # with statement automatically closes the csv file cleanly even in event of unexpected script termination

def updateClient():
	global variables
	jsonVariables = json.dumps(variables)
	assert(variables == json.loads(jsonVariables))
	jsonBytes = jsonVariables.encode('UTF-8')
	check = hashlib.sha1(jsonBytes).hexdigest().encode('UTF-8')
	for clientsocket in peripherals:
		bytesSent = clientsocket.send(jsonBytes)
		bytesSent = clientsocket.send(check)

root.mainloop()