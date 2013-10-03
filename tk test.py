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

def correctAns():
    questionHandler(1)
    askQuestion()

def incorrectAns():
    questionHandler(2)
    askQuestion()
    
def timeEvent():
    questionHandler(4)
    askQuestion()
    
def bankEvent():
    questionHandler(3)

def start():
    global startB, correctB, incorrectB, timeB, bankB
    startB.grid_forget()
    correctB.grid(column=2, row=1, sticky=N)
    incorrectB.grid(column=2, row=2, sticky=N)
    timeB.grid(column=3, row=1, sticky=N)
    bankB.grid(column=3, row=2, sticky=N)
    l1.grid(column=1, row=1, sticky=N)
    l2.grid(column=1, row=2, sticky=N)
    l3.grid(column=4, row=1, sticky=N)
    l4.grid(column=4, row=2, sticky=N)
    l5.grid(column=5, row=1, sticky=N)
    l6.grid(column=5, row=2, sticky=N)
    askQuestion()

root = Tk()
root.title("Control")

mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

question = StringVar()
state = StringVar()
cur_money = IntVar()
bank = IntVar()

l1 = ttk.Label(mainframe, textvariable=state, width=100, background='red')
l2 = ttk.Label(mainframe, textvariable=question, width=100)
l3 = ttk.Label(mainframe, text='Money: ')
l4 = ttk.Label(mainframe, text='Bank: ')
l5 = ttk.Label(mainframe, textvariable=cur_money)
l6 = ttk.Label(mainframe, textvariable=bank)

startB = ttk.Button(mainframe, text="Start", command=start)
startB.grid(column=1, row=2, sticky=N)
correctB = ttk.Button(mainframe, text="Correct", command=correctAns)
incorrectB = ttk.Button(mainframe, text="Incorrect", command=incorrectAns)
timeB = ttk.Button(mainframe, text="Time Up", command=timeEvent)
bankB = ttk.Button(mainframe, text="Bank", command=bankEvent)

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
            state.set('Round ' + str(cntRounds) + ' starting')
            print(state.get())
            question.set('')
            mainframe.update()
            time.sleep(1)
            cur_money.set(money[correct])
        state.set('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))
        print(state.get())
        question.set(questions[cntQuestions][0])
        print(question.get())
    else:
        print('So this is Embarasing')
        print('We seam to have run out of questions')
        print('Exiting...')
        sys.exit()

def questionHandler(event):
    global money, questions, contestants, mainQ, cntQuestions, correct, cntRounds, cntRquestions, bank
    if event == 1:
        print('Correct')
        state.set('Correct')
        correct += 1
    elif event == 2:
        print('Incorrect - ' + questions[cntQuestions][1])
        correct = 0
    elif event == 3:
        print('Banked £' + str(money[correct]))
        print('£' + str(bank.get()) + ' now in bank')
        bank.set(bank.get() + money[correct])
        correct = 0
        print('You now have £0')
        cur_money.set(money[correct])
        mainframe.update()
        cntQuestions =- 1
        return
    elif event == 4:
        print('Time Up')
        print('You have £' + str(bank.get()) + ' in the bank')
        cntRounds += 1
        correct = cntRquestions = 0
    event = ''
    cntRquestions += 1
    cntQuestions += 1
    print('You now have £' + str(money[correct]))
    cur_money.set(money[correct])
    if correct == len(money) - 1:
        print('You have got all questions in round ' + str(cntRounds) + ' correct')
        cntRounds += 1
        cntRquestions = 1
        correct = 0
##    if cntRquestions == 1:
##        print('You must now choose the Weakest Link')
##        i = 1
##        while i - 1 < len(contestants):
##            print(str(i) + '\t' + contestants[i-1])
##            i += 1
##        contestants.remove(contestants[int(input('Please enter a selection (1 - ' + str(len(contestants)) + ')\n')) - 1])

root.mainloop()
