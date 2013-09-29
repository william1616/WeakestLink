import csv
import sys
import time

contestants = 8 # change to listcontestants
questions = []
money = [0, 50,100,200,300,400,500,1000,2500,5000]
mainQ = 'questions.csv'
finalQ = 'questions.csv'

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
    global money, questions, contestants, mainQ
    importQuestions(mainQ)
    cntQuestions = 0
    correct = 0
    cntRounds = 1
    cntRquestions = 1
    bank = 0
    while cntQuestions < len(questions['main']):
        if cntRquestions == 1:
            print('Round ' + str(cntRounds) + ' starting')
        print('Round ' + str(cntRounds) + ' Question ' + str(cntRquestions))
        print(questions[cntQuestions][0])
        while True:
            event = getEvent()
            print(event)
            if event == '1':
                print('Correct')
                correct += 1
                break
            elif event == '2':
                print('Incorrect - ' + questions[cntQuestions][1])
                correct = 0
                break
            elif event == '3':
                bank += money[correct]
                print('Banked £' + str(money[correct]))
                print('£' + str(bank) + ' now in bank')
                correct = 0
                print('You now have £0')
            elif event == '4':
                print('Time Up')
                print('You have £' + str(bank) + ' in the bank')
                cntRounds += 1
                correct = cntRquestions = 0
                break
            event = ''
        cntRquestions += 1
        cntQuestions += 1
        print('You now have £' + str(money[correct]))
        if correct == len(money) - 1:
            print('You have got all questions in round ' + str(cntRounds) + ' correct')
            cntRounds += 1
            cntRquestions = 1
            correct = 0
        if contestants -  cntRounds == 2:
            final()
    print('So this is Embarasing')
    print('We seam to have run out of questions')
    print('Exiting...')
    sys.exit()

def final():
    global finalQ, questions, contestants
    cntQuestions = 0
    print('Congratulations - You are through to the final')
    print('x and y will now go head to head')
    importQuestions(finalQ)
    while cntQuestions < len(questions['main']):
        # ask questions
    print('So this is Embarasing')
    print('We seam to have run out of questions')
    print('Exiting...')
    sys.exit()

def getEvent():
    return input()

askQuestion()
