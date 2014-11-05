from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
from operator import itemgetter
from sharedClasses import contestantClass
import csv, threading, time, os.path, network, misc

status = [] #A list storing the current status messages where each element is a status line
socketList = [] # Alist of client socket objects returned by the network apis serverListner() function

#Define a generator for defualt contestant names
#Contestants names follow the format "contestantX" where x is a number between 0 and the (total number of contestants - 1)
def contestantGenerator():
  for i in range(0, config['questions']['contestantCnt']):
    #config['questions']['contestantCnt'] is the total number of contestants in the game
    yield contestantClass('Contestant' + str(i), i) #Return a contestan class with the given name and a uuid

#The roundController for the main (non-final) rounds
#One instance of this deals with a single round
class mainRoundControllerClass():
  #roundCnt => the round number of the round this roundController is for
  def __init__(self, roundCnt):
    self.money = [0, 50,100,200,300,400,500,1000,2500,5000] #A list of the different integer money values that can be acheived ordered first (smallest), last (biggest)
    self.moneyCounter = 0 #The index in self.money which contains the value of the current money => the current money is given by teh getCurMoney() func
    self.correct = 0 #The counter for the number of correctly awnsered questions this round
    self.rQuestions = 1 #The counter for the number of questions asked this round (inc the current question)
    self.round = roundCnt #The round number
    self.createQuestionGen() #Create the question generator for the round
    
  def createQuestionGen(self, questionNo=0): #Create the question generator for the round
    if config['questions']['sortQuestions'] == True: #Col 3 of the data file can contain an integer value specifing the dificulty of question which is also the round it should be asked in
      #Convert the questionFile path to an absoloute path
      if os.path.isabs(config['questions']['mainQ']):
        questionPath = config['questions']['mainQ']
      else:
        questionPath = os.path.abspath(config['questions']['mainQ'])
      #store a question generator object and its length
      self.questionGenerator, self.questionLen = createQuestionGenerator(questionPath, questionNo, self.round)
    #if sortQuestions is not True the self.questionGenerator attribute needs to be configured to point to the main questionGenerator
    
  def getCurMoney(self): #Return the current ammount of money in the round
    return self.money[self.moneyCounter]
    
  def testAllCorrect(self): #Check if all questions in the round are correct
    return len(self.money) - 1 == self.moneyCounter #If the index of the current money is equal to the number of different money values there are no greater money values so all questions in the round are correct
    
#Class for controlling the entire game
class gameControllerClass():
  def __init__(self):
    self.end = False #End the game? -> defaults to false
    self.bank = 0 #The current bank value
    self.roundCnt = 0 #The current round number
    self.contestantCnt = config['questions']['contestantCnt'] #The number of contestants in the game
    self.contestants = [] #A blank list to contain a list of contestants
    self.removedContestants = [] #A blank list to contain a list of removed contestants
    for contestant in contestantGenerator():
      self.contestants.append(contestant) #get a list of contestants with default names and append them to the list of conestants
    self.roundControllers = {} #A blank dictionary to store all the round controllers for the main round
    for i in range(1, self.contestantCnt + 1):
      self.roundControllers[i] = mainRoundControllerClass(i) #Create a round controller for each round
    self.crtContestantIndex = -1 #The current contestant index
    self.nextRound() #Go to the first round
    self.createQuestionGen() #Create a list of questions
    
    # init ClienSide Variables
    sendClientEvent('rndScoreUpdate', [self.getCurRndCtrl().moneyCounter, self.getCurRndCtrl().money, self.bank]) #Update the clients with the inital round stats
    sendClientEvent('contestantUpdate', self.contestants) #Update the clients with a list of contestant classes
    
  def gotoQuestion(self, questionNo):
    if self.checkFinalRound():
      self.createFinalQuestionGen(questionNo)
    else:
      self.createQuestionGen(questionNo)
    
  #Create a generator to yeild the questions one by one
  #questionNo = row number of question file to start importing questions from
  def createQuestionGen(self, questionNo=0):
    if config['questions']['sortQuestions'] == False:
      #If the questions don't need to be sorted import them all to the same question generator
      #Ensure the path to the question file is an absoloute path
      if os.path.isabs(config['questions']['mainQ']):
        #If its an absoloute path use the given path
        questionPath = config['questions']['mainQ']
      else:
        #If the given path is not an absoloute path convert it to an absoloute path
        questionPath = os.path.abspath(config['questions']['mainQ'])
      #get a question generator and the number of questions in the question generator
      self.questionGenerator, self.questionLen = createQuestionGenerator(questionPath, questionNo)
    elif self.getCurRndCtrl().rQuestions != questionNo + 1: #If not the questions have not already been imported
      self.getCurRndCtrl().createQuestionGen(questionNo) #Import the questions for the current round only
  
  #Create a generator to yield the final questions one by one
  #questionNo = row number of the question file to start importing the questions from
  def createFinalQuestionGen(self, questionNo=0):
    #Conver the question file path to an absoloute path
    if os.path.isabs(config['questions']['finalQ']):
      #If its an absoloute path use the given path
      questionPath = config['questions']['finalQ']
    else:
      #If the given path is not an absoloute path convert it to an absoloute path
      questionPath = os.path.abspath(config['questions']['finalQ'])
    #get a question generator and the number of questions in the question generator
    self.questionGenerator, self.questionLen = createQuestionGenerator(questionPath, questionNo)
    
  #Get the round controller object for the current round
  def getCurRndCtrl(self):
    #get the n th round controller in the list where n is the current round number
    return self.roundControllers[self.roundCnt]
    
  #Get the round question number
  def getRQuestionNo(self):
    return self.getCurRndCtrl().rQuestions
  
  #get the number of questions
  def getQuestionLen(self):
    if config['questions']['sortQuestions'] == True:
      #If the questions are sorted then return the number of questions in the current round
      return self.getCurRndCtrl().questionLen
    else:
      #If the questions are not sorted then return the number of questions in the entire game
      return self.questionLen
    
  #Setup the game vars for the next round
  def nextRound(self):
    self.roundCnt += 1 #Increment the round counter
    for i in self.contestants:
      #clear the score of each contestant in turn
      i.clrScore()
    sendClientEvent('contestantUpdate', self.contestants) #Update the clients with the latest list of contestants
    sendClientEvent('rndScoreUpdate', [self.getCurRndCtrl().moneyCounter, self.getCurRndCtrl().money, self.bank]) #Update the clients with the latest list of game stats
    if config['questions']['sortQuestions'] == True: #get the question generator for the new round if sorting questions
      self.questionGenerator = self.getCurRndCtrl().questionGenerator
    self.nextContestant() #cycle the contestants to get the next contestant
    if self.checkFinalRound(): #check if the next round is the final round
      self.startFinal() #start the final round
    else:
      statusUpdate('Round ' + str(self.roundCnt) + ' starting')
      sendClientEvent('rndStart', [self.roundCnt]) #update the clients with the current round number
    time.sleep(1) #give the clients a second to display "round starting"
    
  #generate and ask a question for one of the main rounds
  def askQuestion(self):
    question, self.answer, nxtQuestion, nxtanswer = next(self.questionGenerator) #get two questions and awnsers from the question generator
    statusUpdate('Round ' + str(self.roundCnt) + ' Question ' + str(self.getRQuestionNo())) #update the status with the round and questions numbers
    statusUpdate(self.curContestant.name + ': ' + question) #update the status with the question directed at the current contestant
    sendClientEvent('askQuestion', [self.getRQuestionNo(), self.curContestant.name, question, self.answer]) #update the client with the question number , current contestant, current question, and awnser for the current question
    sendClientEvent('nxtQuestion', [self.getRQuestionNo() + 1, self.nxtContestant.name, nxtQuestion, nxtanswer]) #update the client with the question number , current contestant, current question, and awnser for the next question
    return question, self.answer, nxtQuestion, nxtanswer #return the questions and awnsers
    
  #handle the responce to a question in the main rounds
  def questionHandler(self, event):
    global socketList
    if event == 1: #event 1 == correct awnser
      self.correctAns(self.answer)
    elif event == 2: #event 2 == incorrect awnser
      self.incorrectAns(self.answer)
    elif event == 3: #event 3 == bank
      self.bankMoney()
      return False #stop handling the responce here; return false to indicate not to move onto the next question
    elif event == 4: #event 4 == time up (end of the round)
      self.timeUp()
    event = '' #clear the event
    return True #return true to move onto the next question
    
  #generate and ask a question for the final round
  def askFinalQuestion(self):
    question, self.answer, nxtQuestion, nxtanswer = next(self.questionGenerator) #get two questions and awnsers from the question generator
    statusUpdate('Final Question ' + str(self.getRQuestionNo()) + ': ' + str(question)) #update the status with the round and questions numbers
    statusUpdate(self.curContestant.name + ': ' + question) #update the status with the question directed at the current contestant
    sendClientEvent('askFinalQuestion', [self.getRQuestionNo(), self.curContestant.name, question, self.answer]) #update the client with the question number , current contestant, current question, and awnser for the current question
    sendClientEvent('nxtFinalQuestion', [self.getRQuestionNo() + 1, self.nxtContestant.name, nxtQuestion, nxtanswer]) #update the client with the question number , current contestant, current question, and awnser for the next question
    return question, self.answer, nxtQuestion, nxtanswer #return the questions and awnsers
    
  #handle the response to a question in the final round
  def finalQuestionHandler(self, event):
    if event == 1: #event 1 == correct awsner
      self.finalCorrect(self.answer)
    elif event == 2: #event 2 == incorrect awnser
      self.finalIncorrect(self.answer)
    if self.getRQuestionNo() == config['questions']['finalRndQCnt'] + 1: #if all final questions have been asked determine the winner or go head2head
      self.detFinalEnd()
    
  #ask the user to choose a weakest link
  def weakestLink(self):    
    statusUpdate('You must now choose the Weakest Link')
    i = 1 #index of the contestant currently being examined
    while i - 1 < len(self.contestants): #loop through each of the contestants
      statusUpdate(str(i) + '\t' + self.contestants[i-1].name + '\t' + str(self.contestants[i-1].score)) #update the status with the contestant index, name and score
      i += 1 #increment the index of the contestant currently being examined
    sendClientEvent('contestantUpdate', self.contestants) #update the clients with the latest list of contestants
    sendClientEvent('eliminationWait', [None]) #update the clients to select a contestant to eliminate
    while not self.end: #while the game should not end
      if network.messageInBuffer('removeContestant'): #wait for a contestant to be removed by one of the clients
        index = [contestant.uuid for contestant in self.contestants].index(network.getMessageofType('removeContestant', False)) #get the index of the contestant in the list of contestants to be removed
        eliminated = self.contestants[index] #get the contestant to be eliminated from the index
        statusUpdate(eliminated.name + ' you are the Weakest Link! Goodbye') #update the status with the eliminated contestant
        self.removedContestants.append(self.contestants.pop(index)) #remove the contestant from the list of contestants in the game and add it to the list of contestants removed from the game
        sendClientEvent('contestantEliminated', [eliminated]) #update the clients with the details of the eliminated contestant
        time.sleep(1) #give the clients time to display that the contestant has been eliminated
        break #no need to wait for another contestant to be eliminated so break out of the receive loop
        
      #server acts as a relay for prompt message
      if network.messageInBuffer('promptMsg'): #if a prompt message is in the network buffer
        promptMessage = network.getMessageofType('promptMsg', False) #get the message from the buffer
        misc.log('Relaying promptMessage \'' + promptMessage + '\'') #display the prompt message in the status log
        for socketObj in socketList:
          network.sendMessage('promtMsg', promptMessage, socketObj) #send the message to all the clients
    
  def nextContestant(self): #cycle the current and next contestants
    self.crtContestantIndex, nxtContestantIndex = cycleContestants(self.crtContestantIndex, len(self.contestants)) #cycle the contestant indexes from the current contestant index
    self.curContestant = self.contestants[self.crtContestantIndex] #get the current contestant from the list
    self.nxtContestant = self.contestants[nxtContestantIndex] #get the next contestant from the list
  
  #callback for a correct awnser
  def correctAns(self, answer):
    statusUpdate('Correct - ' + answer) #update the status with the awnser
    self.getCurRndCtrl().correct += 1 #increment the correct counter in the current round controller
    self.getCurRndCtrl().moneyCounter += 1 #increment the money counter in the current round controller
    self.curContestant.incScore() #increment the score of the current contestant
    sendClientEvent('correctAns', [answer]) #update the clients with the correct awnser
    time.sleep(1) #give the clients time to display "correct awnser"
    if self.getCurRndCtrl().testAllCorrect(): #check if all questions in the round are correct
      sendClientEvent('rndScoreUpdate', [self.getCurRndCtrl().moneyCounter, self.getCurRndCtrl().money, self.bank]) #update the clients with the current money and bank values
      time.sleep(1) # allow client display time to udpsdate before moving to elimination
      self.allCorrect()
    else:
      self.ans()
    
  #callback for an incorrect awnser
  def incorrectAns(self, answer):
    statusUpdate('Incorrect - ' + answer) #update the status with the awnser
    self.getCurRndCtrl().moneyCounter = 0 #rest the money counter for the current round
    sendClientEvent('incorrectAns', [answer]) #update the clients that the awnser was incorrect and provifde the correct awnser
    time.sleep(1) #give the clients time to display "incorrect awnser"
    self.ans()
    
  #shared functionality of all awnserrs
  def ans(self):
    self.getCurRndCtrl().rQuestions += 1 #incremen the question number counter for the current round
    self.nextContestant() #select teh next contestant
    sendClientEvent('contestantUpdate', self.contestants) #provide the client with an updated list of contestants
    sendClientEvent('rndScoreUpdate', [self.getCurRndCtrl().moneyCounter, self.getCurRndCtrl().money, self.bank]) #update the clients with the money and bank stats for the current round
    statusUpdate('You now have £' + str(self.getCurRndCtrl().getCurMoney())) #display the value of the money the contestant currently has
    
  #place all the money the contestant currently has in the bank
  def bankMoney(self):
    statusUpdate('Banked £' + str(self.getCurRndCtrl().getCurMoney())) #update the status with the ammount banked
    statusUpdate('£' + str(self.bank) + ' now in bank') #update the status with the total ammount of money now in the bank
    statusUpdate('You now have £0') #updaet the status with the current value of money (0)
    self.bank += self.getCurRndCtrl().getCurMoney() #increment the bank by the current ammount of money
    self.getCurRndCtrl().moneyCounter = 0 #reset the money counter
    sendClientEvent('rndScoreUpdate', [0, self.getCurRndCtrl().money, self.bank]) #update the clients with the new money and bank values
    
  #time up (end of round) handler
  def timeUp(self):
    statusUpdate('Time Up')
    statusUpdate('You have £' + str(self.bank) + ' in the bank') #update the status with the ammount of money currently in the bank
    sendClientEvent('timeUp', [None]) #update the clients with the time up event
    time.sleep(1) #give the clients time to display the end of round messages
    self.weakestLink() #choose the weakest link and eliminate them
    self.nextRound() #goto the next round
  
  #all correct (end of round) handler
  def allCorrect(self):
    statusUpdate('You have got all questions in round ' + str(self.roundCnt) + ' correct')
    statusUpdate('You have £' + str(self.bank) + ' in the bank') #update the status with the ammount of money currently in the bank
    sendClientEvent('rndScoreUpdate', [self.getCurRndCtrl().moneyCounter, self.getCurRndCtrl().money, self.bank]) #updaet the clients with the ammount of money and bank values
    sendClientEvent('allCorrect', [None]) #update the clients with the allcorrect event
    time.sleep(1) #give the clients time to display the end of round message
    self.weakestLink() #choose the weakest link and eliminate them
    self.nextRound() #goto the next round
    
  #check if it is time to start the final round
  def checkFinalRound(self):
    return len(self.contestants) <= 2 #if the number of contestants is less than or equal to 2 they should go up against each other in the final round
    
  #start the final round (pre-round setup)
  def startFinal(self):
    statusUpdate('Final Round starting')
    self.createFinalQuestionGen() #create the question generator object for the final round
    sendClientEvent('finalStart', [None]) #update the clients with the start final round event
    
  #correct awnser handler for the final round
  def finalCorrect(self, answer):
    statusUpdate('Correct - ' + answer) #update the status with the awnser
    self.getCurRndCtrl().correct += 1 #increment the number of correct awnsers for the current round
    self.curContestant.correctFinalQu(self.getCurRndCtrl().rQuestions) #update the curent contestants score with a correct awnser in the final round
    sendClientEvent('finalCorrectAns', [answer]) #update the clients with the correct awnser
    self.finalAns()
    
  #incorrect awnser handler for the final round
  def finalIncorrect(self, answer):
    statusUpdate('Incorrect - ' + answer) #update the status with the awnser
    sendClientEvent('finalIncorrectAns', [answer]) #updaet the clients with the incorrect awnser
    #if head2head remove the first incorrect answering contestant
    if self.getCurRndCtrl().rQuestions > config['questions']['finalRndQCnt']: #if the number of questions asked is greater than the number of questions asked (as defined by the config file) it is the head2head round so eliminate an incorrectly awnsering conrestant
      statusUpdate(self.contestants[self.crtContestantIndex].name + ' you are the Weakest Link! Goodbye') #update the status with the contestant being eliminated
      sendClientEvent('contestantEliminated', [self.contestants[self.crtContestantIndex]]) #update the clients with the contestant that has just been eliminated
      self.removedContestants.append(self.contestants.pop(self.crtContestantIndex)) #move the contestant to the list of eliminated contestants
      time.sleep(1) #give the clients time to display that contestant x has just been eliminated
    else: #if it is not the head2head round mark the question as incorrectly answered
      self.curContestant.incorrectFinalQu(self.getCurRndCtrl().rQuestions)
      self.finalAns()
  
  #shared functionality of all final awnsers
  def finalAns(self):
    self.getCurRndCtrl().rQuestions += 1 #increment the question counter for the current round
    self.nextContestant() #select the next (other) contestant
    sendClientEvent('contestantUpdate', self.contestants) #pass the updated list of contestants to the clients
    
  #check if it is the end of the final round
  def detFinalEnd(self):
    i = topScore = 0 #i => counter for while loop; topScore => score of top scoring contestant
    head2head = False #bool for weather or not to go to head2head
    while i < len(self.contestants): #loop though each contestant in turn
      if self.contestants[i].score > topScore:
        topScore = self.contestants[i].score #get the top scoring contestant and store the score
      elif self.contestants[i].score == topScore and topScore != 0:
        head2head = True #if there are multiple contestants with the same topScore goto head to head
      i += 1 #increment the contestant counter
    if head2head: #goto head to head round
      statusUpdate('Going to Head to Head Round')
      sendClientEvent('headStart', [None]) #update the clients with the start of the head to head round
      time.sleep(1) #give the clients time to display that the head to head round is starting
    else: #if it is not the head to head round
      for i in range(0, len(self.contestants)): #loop through eachh contestant in turn
        if self.contestants[i].score != topScore: #if the contestant did not acheive the topScore eliminate them
          statusUpdate(self.contestants[i].name + ' you are the Weakest Link! Goodbye') #update the status with the eliminated contestants
          sendClientEvent('contestantEliminated', [self.contestants[i]]) #update the clients with the eliminated contestant
          self.removedContestants.append(self.contestants.pop(i)) #remove the eliminated contestant from the list of contestants and add them to the list of removed contestants
          time.sleep(1) #give the clients time to display the name of the eliminated contestant
          
  #check if there is a winner
  def isWinner(self):
    return len(self.contestants) == 1 # there is a winner when there is only 1 contestant left in the game
          
  #display the name of the winning player
  def winner(self):
    statusUpdate(self.contestants[0].name + ' is the winner!') #update the status with the name of the winning contestantt
    sendClientEvent('winner', [self.contestants[0]]) #update the clients with the winning contestant

#questions => list of questions, start => questionNo with which to start
def questionGenerator(questions, start=0):
  questionCnt = len(questions)
  for i in range(start, questionCnt - 1):
    yield questions[i][0], questions[i][1], questions[i + 1][0], questions[i + 1][1] #Yield the question, awnser, next question, next awnser
  #For the last question there is no next question
  yield questions[questionCnt - 1][0], questions[questionCnt - 1][1], None, None #if there is only a single question left the next question can't be returned
    
#update the Tk status label with text info
def statusUpdate(info):
  global displayStatus, status
  status_lines = config['Tk']['status_lines'] #get the max number of lines the status should be
  status.append(info) #append the latest status to the list
  misc.log(info) #log the status
  while len(status) > status_lines: #if the status is larger than it should be remove the earlier statuses
    status.pop(0) #remove the first status from the list
  displayStatus.set('') #clear the statu diaplyed to the user
  
  for info in status: #for all the 
    displayStatus.set(displayStatus.get()+info+'\n')

#path => path to questionfile, questionStart => questionNo at which to start, roundCnt => return question generator for questions where round == roundCnt, if not specified return question generator for all questions in the file
def createQuestionGenerator(path, questionStart=0, roundCnt=None):
  if roundCnt: #if roundCnt is specified return question generator for that round
    print('Importing Questions for Round ', roundCnt)
    questions = getListFromColumn(importQuestions(path), 2, roundCnt)
    return questionGenerator(questions, questionStart), len(questions)
  else: #return question generator for all questions
    print('Importing Questions')
    questions = importQuestions(path)
    return questionGenerator(questions), len(questions)
    
#Threaded listner class which listnens for connections to the server from clients
class serverListner (threading.Thread): #Extend the Thread class
  def __init__(self):
    super().__init__() #Call the thread constructor to Initiate the thread class
    self.running = self.end = False #Setup some variables for use in while loop conditions
    
  #threaded code is contained within this function which is started by the serverListner.start() method
  def run(self):
    global socketList
    while not self.end: #keep looping until the thread is asked to terminate
      while self.running: #don't run the main code until the main part of the thread is asked to stop running
          clientsocket, address = network.serverListner(self.serversocket) #get a clientscoket and its address from the serversocket
          if clientsocket:
            socketList.append(clientsocket) #if the serversocket returns a valid clientsocket add it to the list of sockets
            statusUpdate(address[0] + ' Succesfully Connected') #update the status with the address of the clientsocket
            
  def startListner(self): #start the listner
    global status
    if not self.running: #if the listner is not already running
      self.serversocket = network.initServerSocket(config['server']['bindAddress'],config['server']['bindPort']) #create a serversocket with the parameters specified in the config file
      self.running = True #start running the main threaded code
      statusUpdate('Started Listner') #update the status with the relevant message
    else: #if the listner is already running
      statusUpdate('Cannot start Listner - Listner is already Running!') #update the status wuth the relevant message
      
  def stopListner(self, join): #stop the listner: join => stop the thread running as well if true
    global status
    if join and self.isAlive(): #if the thread is currently running (ifs its start() function has been called) and the thread is to be joined
      self.join() #join/terminate the thread
      if hasattr(self, 'serversocket'): network.closeSocket(self.serversocket) #close the serversocket is it exsits
      statusUpdate('Terminated Listner Thread') #update the status with the relevant message
    elif self.running: #if the listner is currently running but the thread is not to be terminated
      self.running = False #stop the listner
      time.sleep(0.1) #allow any socket waiting to be conntected time to connect fullu
      if hasattr(self, 'serversocket'): network.closeSocket(self.serversocket) #close the serversocket if it exists
      statusUpdate('Stopped Listner')
    else:
      statusUpdate('Cannot stop Listner - Listner is not Running') #if the listner is not running and the thread is not to be joined update the status with the relevant message
      
  def join(self): #join/terminate the listner thread
    self.running = False #stop the listner from running
    time.sleep(0.1) #allow any socket waiting to be conntected time to connect fullu
    self.end = True #stop the threaded code from running
    threading.Thread.join(self) #terminate the thread

#Threaded question control instance which runs the main game code
class questionControl(threading.Thread): #Extend the Thread class
  def __init__(self):
    super().__init__() #Call the thread constructor to Initiate the thread class
    self.end = False #setup a couple of variable for while loop conditions
    self.startGame = False
    
  #threaded code is contained within this function which is started by the serverListner.start() method
  def run(self):
    self.gameController = gameControllerClass() #create a game controller class
    while not self.end and not self.gameController.checkFinalRound(): #whilst the thread is running and it is not time for the final round
      self.mainLoop() #run the main game loop code
      
    while not self.end: #whilst the thread is running
      self.finalLoop() #run the final round game loop code
      if self.gameController.isWinner(): #if there is a winner
        self.gameController.winner() #run the winner callback function
        break #break out of the while loop as the game is over
      
    if not self.end: #whilst the thread is running
      pass #do nothing
      #do something at the end of the program?
    
  #Code for the main game loop
  def mainLoop(self):
    self.gameController.askQuestion() #If the game has not started the Data is not sent to GUI as it is not listning; so send it the question data after the the startGame event is received
    if not self.startGame and not self.end: #if the game has not started and the thread is running
      self.waitForGameStart() #Wait for startGame event before requesting a response
      self.gameController = gameControllerClass() #Resend the Data for GUI
      self.gameController.askQuestion()
    sendClientEvent('responseWait', [None]) #Wait for a response to the question
    while not self.end: #while the thread is running
      if network.messageInBuffer('quResponse'): #if there is a response to the question
        quResponse = network.getMessageofType('quResponse', False) #get the question response
        if quResponse > 0 and quResponse <= 4: #ensure the question response is valid
          if self.gameController.questionHandler(quResponse) == True: #run the calback for the question resonse
            break #if the callback returns true move onto the next question
          else:
            sendClientEvent('responseWait', [None]) #otherwise wait for another response
      
      self.checkPromptMsg() #check if there is a prompt message to relay
      if self.checkGotoQuMsg(): break
      
  #Code for the final main loop
  def finalLoop(self):
    self.gameController.askFinalQuestion() #ask a final round question
    sendClientEvent('responseWait', [None]) #wait for a response to the question
    while not self.end: #if the thread is still running
      if network.messageInBuffer('quResponse'): #check for a response to the question
        quResponse = network.getMessageofType('quResponse', False) #get the response
        if quResponse > 0 and quResponse <= 2: #check the response is valid
          self.gameController.finalQuestionHandler(quResponse) #handle the response
          break #exit the loop as a response has been received
      
      self.checkPromptMsg() #check if there is a prompt message to relay
      if self.checkGotoQuMsg(): break
      
  #Check for a prompt message and re-broadcast it to the clients if it exists
  def checkPromptMsg(self):
    if network.messageInBuffer('promptMsg'): #if a prompt message exists
      promptMessage = network.getMessageofType('promptMsg', False) #get the message
      misc.log('Relaying promptMessage \'' + promptMessage + '\'') #log the message
      for socketObj in socketList:
        #send the message to each socket in the socketList
        network.sendMessage('promtMsg', promptMessage, socketObj)
  
  def checkGotoQuMsg(self):
    #goto question
    if network.messageInBuffer('gotoQu'):
      questionNo = network.getMessageofType('gotoQu', False)
      if questionNo > 0 and questionNo <= self.gameController.getQuestionLen():
        self.gameController.gotoQuestion(questionNo)
        return True
    return False
    
  #Wait for the game to start
  def waitForGameStart(self):
    misc.log('Waiting for Game Start')
    if network.getMessageofType('startGUI'): #wait for a message of type startGUI with a blocking call
      self.startGame = True #allow the game to start
      misc.log('Relaying startGUI Command')
      for socketObj in socketList:
        #send a message to each socket in the socketList
        network.sendMessage('startGUI', [None], socketObj)
      network.removeUsedType('startGUI') #remove the startGUI message type from the list of used types
    
  #terminate the thread
  def join(self):
    #set the end variables that allow the loops to iterate to false so that the loops terminate
    self.end = True
    self.gameController.end = True
    super().join() #terminate the thread

#start the servers main loop
def start():
  global listner, questionThread
  listner.stopListner(True) #terminate the listner thread
  startFrame.grid_remove() #remove the startFrame and its contents from the tkinter GUI
  mainFrame.grid() #add the mainFrame to the tkinter GUI
  sendClientEvent('gameStart', [None]) #start the main game loop in all the clients
  questionThread = questionControl() #create the thread to control the question flow
  questionThread.start() #start the question thread

#start the listner thread
def initListner():
  global listner
  listner = serverListner() #create the listner thread and save it to a global variable
  listner.start() #start the listner thread

#Inititalise the GUI with the given parent
def initTk(parent):
  #List the global variables that need to be accessed in other scopes
  global displayStatus, startFrame, mainFrame, contestantTopLevel, listner
  print('Initiating GUI...')
  
  startFrame = ttk.Frame(parent, padding="3 3 3 3") #Create a frame for the start GUI to be placed in => The frame should have 3 pixels of space on all 4 sides of it between itself and the parent
  startFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #Place the frame within its parent making it attach to all four sides of the parrent window
  startFrame.columnconfigure(0, weight=1) #The 0th column should expand at the same rate as the main window
  startFrame.rowconfigure(0, weight=1) #The 0th row should expand at the same rate as the main window

  startMenu = Menu(parent) #Create a Toolbar
  parent['menu'] = startMenu #The toolbar should be on the startFrame
  startFile = Menu(startMenu, tearoff=0) #Create a menu on the toolbar
  startTools = Menu(startMenu, tearoff=0)
  startHelp = Menu(startMenu, tearoff=0)
  startMenu.add_cascade(menu=startFile, label='File') #Label each menu appropriatly
  startMenu.add_cascade(menu=startTools, label='Tools')
  startMenu.add_cascade(menu=startHelp, label='Help')
  
  startFile.add_command(label='Exit', command=lambda: close(parent)) #Add a command labled Exit to the File menu and call the close function when it is clicked
  
  startTools.add_command(label='Select Main Question File', command=selectMainQuestionFile) #Add a command labeled Select Main Question File to the Tools Menu and call the selectMainQuestionFile function when it is clicked
  startTools.add_command(label='Select Final Question File', command=selectFinalQuestionFile) #Add a command labeled Select Final Question File to the Toosl Menu selectFinalQuestionFile function when it is clicked
  #startTools.add_command(label='Goto Question...', command=gotoQuestion)
  startTools.add_command(label='Edit Contestant List', command=editContestants) #Add a command labeled Edit Contestant List to the Tools Menu and call the editContestant function when it is clicked
  startTools.add_separator() #Add a seperator to the menu
  startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress()))) #Add a command labeled What is My IP to the Tools Menu and display an information box containing a list of IP addresses the computer has
  
  startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink")) #Add a command labeled About to the Help Menu and display an information box containing a link to the Source Code Repo
  
  displayStatus = StringVar() #Create a variable to store the status
  
  ttk.Label(startFrame, text='The Weakest Link Server', width=100).grid(column=0, row=0, sticky=N) #Create a label, used as a title, with content The Weakest Link Server and place this label at the top left of the startFrame
  ttk.Label(startFrame, text='Status', width=100).grid(column=0, row=1, sticky=N) #Create a label with the content Status and place this label just below the title in the startFrame
  ttk.Label(startFrame, textvariable=displayStatus, width=100).grid(column=0, row=2, sticky=N) #Display the content of the status underneath the status label
  ttk.Button(startFrame, text='Start', command=start).grid(column=1, row=0, sticky=N) #Add a button labeled Start and calling the start function to the top right of the startFrame
  ttk.Button(startFrame, text='Start Listner', command=lambda: listner.startListner()).grid(column=1, row=1, sticky=N) #Create a button labeled Start Listner to the startFrame and start the Listner when it is pressed (Listner is a Global Variable and an instance of the ServerListner class
  ttk.Button(startFrame, text='Stop Listner', command=lambda: listner.stopListner(False)).grid(column=1, row=2, sticky=N) #Create a buttib labeled Stop Listner to the startFrame and stop the Listner when the button is pressed
  
  mainFrame = ttk.Frame(parent, padding="3 3 3 3") #Create a frame for the main GUI with 3 pixels spacing between the frame and the parent on all 4 sides
  mainFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #Place the frame in the top left of the parent and attach it to all four sides of the parent
  mainFrame.columnconfigure(0, weight=1) #The 0th column should expand at the same rate as the main window
  mainFrame.rowconfigure(0, weight=1) #The 0th row should expand at the same rate as the main window
  mainFrame.grid_forget() #Remember the grid options for the frame but remove it from the grid
  
  ttk.Label(mainFrame, text='Status', width=100).grid(column=1, row=1, sticky=N) #Create a label Status and place it in the topLeft of the mainFrame
  ttk.Label(mainFrame, textvariable=displayStatus, width=100).grid(column=1, row=2, sticky=N) #Display the content of the status underneath the status label
  
  
  contestantTopLevel = Toplevel() #create a toplevel to display a list of contestants and allow their names to be edited
  contestantTopLevel.title(config['Tk']['window_title']) #set the title of the toplevel to the value specified in the config file
  contestantTopLevel.resizable(False, False) #make the toplevels sized fixed (unchangable in both directions)
  contestantTopLevel.withdraw() #hide the toplevel
  
  contestantTopLevel.bind("<Return>", lambda event: updateContestants()) #bind the return key to the update function
  contestantTopLevel.bind("<Escape>", lambda event: contestantTopLevel.withdraw()) #bind the escape key to the close function
  
  ttk.Button(contestantTopLevel, text='Update', command=updateContestants).grid(column=0, row=config['questions']['contestantCnt'], sticky=N) #create a button to update the contetants names and place it in the row beneath the contestant names
  ttk.Button(contestantTopLevel, text='Cancel', command=contestantTopLevel.withdraw).grid(column=1, row=config['questions']['contestantCnt'], sticky=N) #create a button to close the toplevel and place it in the row beneath the contestant names
  
  parent.protocol("WM_DELETE_WINDOW", lambda: close(parent)) #bind the X at the top right corner of the parent window to the close function to ensure the window closes cleanly
  
  print('GUI Initiated')
  
# def gotoQuestion():
  # global questionThread
  # if variables['gamemode'] != -1:
    # questionNo = simpledialog.askinteger("Go to question...", "Question Number:")
    # if questionNo > 0 and questionNo <= len(questions):
      # variables['cntQuestions'] = questionNo
    # elif questionNo < 0 and abs(questionNo) <= len(questions) and variables['cntQuestions'] - questionNo <= len(questions):
      ##questionNo -ve -> addition
      # variables['cntQuestions'] -= questionNo
    # questionThread.newQuestion = True
  # else:
    # messagebox.showerror("Error", "Server has not Started Running Yet!")
  
#populate the contestant list with the names of the contestants currently in the game
def editContestants():
  global variables, contestantTopLevel, contestantNameValues, questionThread
  contestantNameValues = [] #create/clear a list to hold the values of the contestant names
  for i, contestant in zip(range(0, len(questionThread.gameController.contestants)), questionThread.gameController.contestants): #loop through the index and the contestant at that index in pairs
    contestantNameValues.append(StringVar()) #create s string variable for each contestants name
    contestantNameValues[i].set(contestant.name) #set the value of the string variable to the contestants name
    ttk.Entry(contestantTopLevel, textvariable=contestantNameValues[i]).grid(column=0, row=i, columnspan=2, sticky=N) #create an entry widget containing the contestants name and grid it on the row equal the inecies of the contestants name
  contestantTopLevel.deiconify() #display the cntestant toplevel
  
#update the contestants names from the values specified in the contestant toplevel
def updateContestants():
  global variables, contestantTopLevel, contestantNameEntry, contestantNameValues
  contestantTopLevel.withdraw() #hide the toplevel
  for i, contestantName in zip(range(0, len(questionThread.gameController.contestants)), contestantNameValues): #loop through the index and the stringVars that contain the contestants edited names in pairs
    questionThread.gameController.contestants[i].name = contestantName.get() #set the name of the contestant with index i to the value of the stringVar with index i
  sendClientEvent('contestantUpdate', questionThread.gameController.contestants) #update the clients with the new contestant class including the updates names
  
#select the main question file and save the path of the file to the config
def selectMainQuestionFile():
  global config
  file = filedialog.askopenfilename(title="Open Question File", initialdir=os.path.expanduser("~"), filetypes=[("CSV Files", "*.csv")]) #open a window to allow the user to select a file from their documents; set the users home directory as the directory to display first; allow only csv files to be selected
  if file: #if a file has been selected
    config['questions']['mainQ'] = file #set the path in the config to the value given by the user
    misc.writeConfig(config) #write the new config to file
  
#select the final question file and save the path of the file to the config
def selectFinalQuestionFile():
  global config
  file = filedialog.askopenfilename(title="Open Question File", initialdir=os.path.expanduser("~"), filetypes=[("CSV Files", "*.csv")]) #open a window to allow the user to select a file from their documents; set the users home directory as the directory to display first; allow only csv files to be selected
  if file:
    config['questions']['finalQ'] = file #set the path in the config to the value given by the user
    misc.writeConfig(config) #write the new config to file

#cleanly close the GUI
def close(topLevel):
  listner.stopListner(True) #terminate the listner thread
  if 'questionThread' in globals():
    questionThread.join() #if the question thread is running stop it
  if topLevel.config()['class'][4] == 'Toplevel': topLevel.root.deiconify() #if the toplevel argument is a toplevel then show its root
  topLevel.destroy() #destroy the toplevel

#Get a list where all the values in the specified column are equal to the specified value
#unsortedList => list to get subList from, columnNo => columnNo to sort the list by, value => return all elements where the the subelement in columnNo are equal to value
def getListFromColumn(unsortedList, columnNo, value):
  sortedList = sorted(unsortedList, key=itemgetter(columnNo)) #Sort the list using columnNo as the sort key
  returnList = []
  #Find the index of the sortedList where the values in columnNo start being equal to the specified value
  for i in range(0, len(sortedList)): #
    if sortedList[i][columnNo] == value:
      break
  #From this index until the index where the values in columnNo stop being equal to the specified value append each index to the returnList
  for j in range(i, len(sortedList)):
    if sortedList[j][columnNo] != value:
      break
    returnList.append(sortedList[j])
  return returnList
   
#Cycle Contestant Indecies
#0 becomes 1;1 becomes 2; 2 becomes 3 etc
#If the new index is larger than the number of total Contestants return to the start of the list (index 0)
def cycleContestants(curContestantIndex, totalContestants):
  #cycle through each contestant in turn
  #Inrement the curentContestantIndex
  if curContestantIndex < totalContestants - 1:
    curContestantIndex += 1
  else:
    curContestantIndex = 0
  
  #Increment the nxtContestant to be 1 greater than the curentContestantIndex
  nxtContestantIndex = curContestantIndex #Set the nxtContestantIndex equal to the currentContestantIndex
  #Increment the nextContestantIndex
  if nxtContestantIndex < totalContestants - 1:
    nxtContestantIndex += 1
  else:
    nxtContestantIndex = 0
    
  #Return the current and next contestant indecies        
  return curContestantIndex, nxtContestantIndex

#Import a list of Questions from a CSV file
def importQuestions(file):
  global status
  statusUpdate('Importing Questions...')
  questions = [] #Create an empty list to store the questions in
  cnt = 0 #Cnt the number of questions imported
  with open(file) as csvfile: #Open the CSV file
    questionfile = csv.reader(csvfile) #Return an iter object from the csvfile
    for row in questionfile: #For each item in the iter object / for each row in the csvfile
      try:
        #where row[0] = questions & row[1] = answer & row[2] = round to ask question in / difficulty
        if row[0] and row[1] and row[2]: #If a question difficulty is provided import the question and the difficulty
          questions.append([row[0], row[1], int(row[2])])
        elif row[0] and row[1]: #If a question difficulty is not provided don't import it
          questions.append([row[0], row[1]])
        cnt += 1 #Increment the counter for the number of questions imported -> call this last so that it won't run if an error is caught by the try: except:
      except: #Catch any errors opening/reading the question file
        misc.log('Error importing question - ' + str(sys.exc_info())) #Log the error
    statusUpdate('Imported ' + str(cnt) + ' Questions') #Update the status listing how many questions have been imported
    #with statement automatically closes the csv file cleanly even in event of unexpected script termination
    return questions #Return a list of questions
  
#Send an event to all clientsockets
#event = string eventTypeName, args = list eventArgs
def sendClientEvent(event, args):
  global socketList
  for socketObj in socketList:
    #Loop through all the sockets
    network.sendMessage(event, args, socketObj) #Send the event and its args through that socket

#Declare all the message types that should be received from clientsockets
def netTypesDeclaration():
  network.addUsedType('quResponse') #=> Contains an int coresponding to the contestants last response; allowed values are: 1 - Correct; 2 - Incorrect; 3 - Bank; 4 - Time
  network.addUsedType('gotoQu') #=> Contains the index of the question to go to
  network.addUsedType('promptMsg') #=> Contains the msg to realy onto the prompt gui
  network.addUsedType('removeContestant') #=> Contains the index of the contestant to remove from the game
  network.addUsedType('startGUI') #=> Indicates to start the game
    
#Inital setup of the config and network
def setup():
  global config
  print('Importing Config...')
  config = misc.initConfig() #Save the config to a global variable as a dictionary
  print('Config Imported')
  netTypesDeclaration() #Declare the types of message that should be received by the client
    
#If the server script it called directly create a root Tk() object
if __name__ == '__main__':
  setup() #Initial setup of the config and network
  root = Tk() #Create the root Tk() object
  root.title(config['Tk']['window_title']) #Set the title of the root Tk() object to the config value for window title
  initTk(root) #Create rest of the Tk windows with the root Tk() object as their parent
  initListner() #Start a listner for connections to the server
  root.mainloop() #Enter the Tk main loop handling any Tk events / callbacks