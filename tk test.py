from tkinter import *
from tkinter import ttk
import csv
import sys
import time

contestants = ['bill','ben','bob','cat','hat','matt','mouse','man'] # change to listcontestants
questions = []
money = [0, 50,100,200,300,400,500,1000,2500,5000]
mainQ = 'questions.csv'
finalQ = 'questions.csv'
cntQuestions = 0
correct = 0
cntRounds = 1
cntRquestions = 1
bank = 0

def correctAns():
    questionHandler(1)
    askQuestion()

def incorrectAns():
    questionHandler(2)
    askQuestion()
    
def time():
    questionHandler(3)
    
def bank():
    questionHandler(4)

root = Tk()
root.title("Control")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

question = StringVar()
rounds = StringVar()

ttk.Label(mainframe, textvariable=rounds).grid(column=1, row=1, sticky=N)
ttk.Label(mainframe, textvariable=question).grid(column=2, row=1, sticky=N)

ttk.Button(mainframe, text="Correct", command=correctAns).grid(column=1, row=2, sticky=N)
ttk.Button(mainframe, text="Incorrect", command=incorrectAns).grid(column=1, row=3, sticky=N)
ttk.Button(mainframe, text="Time Up", command=time).grid(column=2, row=2, sticky=N)
ttk.Button(mainframe, text="Bank", command=bank).grid(column=2, row=3, sticky=N)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

def importQuestions(file):
    global questions
    with open(file) as csvfile: # add search directory for csv
        questionfile = csv.reader(csvfile)
        for row in questionfile:
            # where row[0] = questions & row[1] = awnser
            if row[0] and row[1]:
                questions.append([row[0], row[1]])
    # with statement automatically closes the csv file cleanly even in event of unexpected script termination

def askQuestion():
    global money, questions, contestants, mainQ, cntQuestions, correct, cntRounds, cntRquestions, bank
    importQuestions(mainQ)
    cntContestants = len(contestants) + 1
    if cntQuestions < len(questions):
        if cntRquestions == 1:
            rounds.set('Round ' + str(cntRounds) + ' starting')
            print('Round ' + str(cntRounds) + ' starting')
            time.sleep(1)
        print('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))
        rounds.set('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))
        question.set(questions[cntQuestions][0])
        print(questions[cntQuestions][0])
    else:
        print('So this is Embarasing')
        print('We seam to have run out of questions')
        print('Exiting...')
        sys.exit()

def questionHandler(event):
    global money, questions, contestants, mainQ, cntQuestions, correct, cntRounds, cntRquestions, bank
    if event == 1:
        print('Correct')
        rounds.set('Correct')
        correct += 1
    elif event == 2:
        print('Incorrect - ' + questions[cntQuestions][1])
        rounds.set('Incorrect - ' + questions[cntQuestions][1])
        correct = 0
    elif event == 3:
        bank += money[correct]
        print('Banked £' + str(money[correct]))
        rounds.set('Banked £' + str(money[correct]))
        time.sleep(1)
        print('£' + str(bank) + ' now in bank')
        rounds.set(('£' + str(bank) + ' now in bank'))
        time.sleep(1)
        correct = 0
        print('You now have £0')
        rounds.set('You now have £0')
        time.sleep(1)
        rounds.set('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))
        cntQuestions =- 1
        return
    elif event == 4:
        print('Time Up')
        rounds.set('Time Up')
        time.sleep(1)
        print('You have £' + str(bank) + ' in the bank')
        rounds.set('You have £' + str(bank) + ' in the bank')
        cntRounds += 1
        correct = cntRquestions = 0
    event = ''
    cntRquestions += 1
    cntQuestions += 1
    print('You now have £' + str(money[correct]))
    time.sleep(1)
    rounds.set('You now have £' + str(money[correct]))
    time.sleep(1)
    if correct == len(money) - 1:
        print('You have got all questions in round ' + str(cntRounds) + ' correct')
        rounds.set('You have got all questions in round ' + str(cntRounds) + ' correct')
        time.sleep(1)
        cntRounds += 1
        cntRquestions = 1
        correct = 0
    if cntRquestions == 1:
        time.sleep(1)
        print('You must now choose the Weakest Link')
        rounds.set('You must now choose the Weakest Link')
        i = 1
        while i - 1 < len(contestants):
            print(str(i) + '\t' + contestants[i-1])
            i += 1
        contestants.remove(contestants[int(input('Please enter a selection (1 - ' + str(len(contestants)) + ')\n')) - 1])
    time.sleep(1)
    rounds.set('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))

askQuestion()
root.mainloop()