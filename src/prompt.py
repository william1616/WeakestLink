from tkinter import *
from tkinter import ttk, messagebox, font
import os.path, network, misc

#Extend the ttk.Label class to create a label that disapears 5 seconds after creation
class timedLabel(ttk.Label):
  #when this class is created it should be grided on calling as it will ungrid after 5 seconds
  def __init__(self, frame, **kwargs):
    global mainTopLevel
    #overide some kwargs
    kwargs['background'] = 'red' #set the background to red
    kwargs['font'] = font.Font(family="Arial", size=12) #set the font to Arial size 12
    super().__init__(frame, **kwargs) #call the super constructor
    try:
      #if the mainTopLevel is a Tk root instance use it to ungrid this object in 5000ms
      if mainTopLevel.config()['class'][4] == 'Tk':
        mainTopLevel.after(5000, self.grid_forget)
      #if the mainTopLevel is a TopLevel widget use its parent to ungrid this object in 5000ms
      elif mainTopLevel.config()['class'][4] == 'Toplevel':
        mainTopLevel.root.after(5000, self.grid_forget)
    except TclError:
      #if Tkinter errors occur exit silently
      pass
  
def variableUpdates():
  global status, question, answer, nextQuestion, nextanswer, contestants, round, contestantList, mainFrame
  
  if network.messageInBuffer('rndStart'): #if a rndStart message exists
    [round] = network.getMessageofType('rndStart', False) #set the local round variable to the value in the message
    status.set('Round ' + str(round) + ' starting') #update the status with the new round
    
  if network.messageInBuffer('askQuestion'): #if an askQuestion message exists
    rQuestion, contestant, questionStr, answerStr = network.getMessageofType('askQuestion', False) #set the question number, contestant the question is being asked to, question and awnser to the values in the message
    question.set(contestant + ': ' + questionStr) #set the current question to the values in the message
    answer.set(answerStr) #set the awnser to the value given in the message
    status.set('Round ' + str(round) + ' Question ' + str(rQuestion)) #update the status with the round and question numbers
    
  if network.messageInBuffer('nxtQuestion'): #if a nxtQuestion message exists
    nxtRQuestion, nxtContestant, nxtQuestionStr, nxtanswerStr = network.getMessageofType('nxtQuestion', False) #set the next question number, contestant the next question is being asked to, next question and next awnser to the values in the message
    nextQuestion.set(nxtContestant + ': ' + nxtQuestionStr) #set the next question to the values in the message
    nextanswer.set(nxtanswerStr) #set the next awnser to the value given in the message
    
  if network.messageInBuffer('rndScoreUpdate'): #if a "rndScoreUpdate" message exists
    moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False) #update the moneyCount, money and bankValue with the values given in the message
    
  if network.getMessageofType('timeUp', False): #if a timeUp message exists
    timedLabel(mainFrame, text='Time Up! - You must now choose the Weakest Link!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S)) #create a timed label displaying that it is time up and place it in the 5th row of the 1-3 columns
  
  if network.getMessageofType('allCorrect', False): #if an allCorrect message exists
    timedLabel(mainFrame, text='All Questions Correct! - You must now choose the Weakest Link!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S)) #create a timed label displaying that all questions in the current round have been awnsered correctly and place it in the 5th row of the 1-3 columns
    
  if network.messageInBuffer('contestantEliminated'): #if a contestantEliminated message exists
    [lastEliminated] = network.getMessageofType('contestantEliminated', False) #store the lastEliminated contestant class as a local variable
    timedLabel(mainFrame, text=lastEliminated.name + ' has been eliminated!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S)) #create a timed label displaying that it is time up and place it in the 5th row of the 1-3 columns
    
  if network.messageInBuffer('contestantUpdate'): #if a contestantUpdate message exists
    contestantList = network.getMessageofType('contestantUpdate', False) #store the list of contestant classes in a local variable
    contestants.set('\n'.join([': '.join([contestant.name, str(contestant.score)]) for contestant in contestantList])) #set the string variable containg the list of contestants to a string of multiple rows where each row contains a contestants name and there score
    
  if network.getMessageofType('finalStart', False): #if a final start message exists
    status.set('Final Round starting') #update the status with a message to this effect
    
  if network.messageInBuffer('askFinalQuestion'): #if an askFinalQuestion message exists
    rQuestion, contestant, questionValue, answerValue = network.getMessageofType('askFinalQuestion', False) #set the question number, contestant the question is being asked to, question and awnser to the values in the message
    question.set(contestant + ': ' + questionValue) #set the current question to the values given in the message
    answer.set(answerValue) #set the current awnser to the value given in the question
    status.set('Final Question ' + str(rQuestion)) #set the status to question number
    
  if network.messageInBuffer('nxtFinalQuestion'):
    nxtRQuestion, nxtContestant, nxtQuestion, nxtanswer = network.getMessageofType('nxtFinalQuestion', False) #set the next question number, contestant the next question is being asked to, next question and next awnser to the values in the message
    nextQuestion.set(nxtContestant + ': ' + nxtQuestion) #set the next question to the values given in the message
    nextanswer.set(nxtanswer) #set the next awnser to the value given in the message
    
  if network.getMessageofType('headStart', False): #if a message of type headStart exists
    status.set('Going to Head to Head Round') #update the status with a message indicating the start of the head2head round
    
  if network.messageInBuffer('winner'): #if a message of type winner exists
    [winner] = network.getMessageofType('winner', False) #set the variable winner to the contestant class of the winner
    status.set(winner.name + ' is the winner!') #update the status with the winning contestants name
    timedLabel(mainFrame, text=winner.name + ' is the Winner!').grid(column=1, row=5, columnspan=3, sticky=(W, N, S)) #create a timed label displaying that there is a winner and place it in the 5th row of the 1-3 columns
    
  if network.messageInBuffer('promtMsg'): #if a message of type promptMsg exists
    timedLabel(mainFrame, text=network.getMessageofType('promtMsg', False)).grid(column=1, row=4, columnspan=3, sticky=(W, N, S)) #create a timed label displaying the message and place it in the 4th row of the 1-3 columns
  
  try:
    if mainTopLevel.config()['class'][4] == 'Tk': #if the mainTopLevel is a root tk instance use it to run this function again in 1000ms
      mainTopLevel.after(1000, variableUpdates)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a toplevl instance use its parent to run this function again in 1000ms
      mainTopLevel.root.after(1000, variableUpdates)
  except TclError:
    #if there are any tkinter errors then exit cleanly
    pass
  
#attempt to connect to the server specified by the address Entry widget in the tkinter GUI
def start():
  global address, socket, startFrame, waitFrame
  if network.attemptConnect(socket, address.get(), config['server']['bindPort']): #attempt to connect to the address specified in the GUI, port specified in the config using the socket created by setup()
    startFrame.grid_forget() #remove the startFrame from the grid
    waitFrame.grid() #add the waitFrame to the grid
    network.addUsedType('gameStart') #add gameStart as a usedType
    isServerRunning() #check if the server has started and perform the relevant tasks if it has
  else: #if the connection failed display a message to that affect
    messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"") 
      
#check if the server has started running and if it has perform the relevant tasks          
def isServerRunning():
  global mainTopLevel
  if network.getMessageofType('gameStart', False): #get a message of type "gameStart" with a non-blocking call
    network.addUsedType('rndStart') #add types of message that we want to receive to the usedTypes list
    network.addUsedType('askQuestion')
    network.addUsedType('nxtQuestion')
    network.addUsedType('rndScoreUpdate')
    network.addUsedType('timeUp')
    network.addUsedType('contestantEliminated')
    network.addUsedType('allCorrect')
    network.addUsedType('contestantUpdate')
    network.addUsedType('finalStart')
    network.addUsedType('askFinalQuestion')
    network.addUsedType('nxtFinalQuestion')
    network.addUsedType('headStart')
    network.addUsedType('winner')
    network.addUsedType('promtMsg')
    network.removeUsedType('gameStart')
    waitFrame.grid_forget() #remove the waitFrame from the grid
    mainFrame.grid() #add the mainFrame to the grid
    variableUpdates() #update local variables with those variables from the server
  else: #if no such messages exist
    if mainTopLevel.config()['class'][4] == 'Tk': #if the server is a Tk root instance use it to call this function again in 100 ms
      mainTopLevel.after(100, isServerRunning)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the server is a TopLevel instance use its parent to call this function again in 100ms
      mainTopLevel.root.after(100, isServerRunning)
    
#initialise the tkinter GUI
def initTk(parent):
  global address, startFrame, waitFrame, mainFrame, mainTopLevel, status, question, answer, nextQuestion, nextanswer, contestants
  
  mainTopLevel = parent #save the parent as a global variable: mainTopLevel
  
  #define two fonts for use in the GUI
  mainFont = font.Font(family="Arial", size=12)
  titleFont = font.Font(family="Arial", size=16, underline=True)
  
  startFrame = ttk.Frame(parent, padding="3 3 3 3") #create a frame with 3 pixels of padding on all 4 sides
  startFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #grid the frame in the 0th row and 0th column of its parent
  startFrame.columnconfigure(0, weight=1) #configure the 0th column of the startFrame to expand at the same rate as the parents width
  startFrame.rowconfigure(0, weight=1) #configure the 0th row of the startFrame to expand at the same rate as the parents height
  
  address = StringVar() #create a string variable to hold the address of the server to connect to
  address.set(config['server']['bindAddress']) #set the default value of the server address to the value specified in the config file
  
  ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N) #create a button entitled Connect that will call the start function to attempt to connect to the server
  ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N) #create a button entitled Exit that will call the close function to close the GUI
  ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N) #create a text entry widget holding the address of the server to connect to
  ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N) #create a label identifying the Entry widget as containing the servers ip address
  
  mainFrame = ttk.Frame(parent, padding="3 3 3 3") #create a frame with 3 pixels of padding on all 4 sides
  mainFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #grid the frame in the 0th row and 0th column of its parent
  mainFrame.columnconfigure(0, weight=1) #configure the 0th column of the startFrame to expand at the same rate as the parents width
  mainFrame.rowconfigure(0, weight=1) #configure the 0th row of the startFrame to expand at the same rate as the parents height
  mainFrame.grid_remove() #remove the mainFrame from the grid but remember the properties by which it is gridded so the next call to mainFrame.grid() will not require any parameters to be specified
  
  #create local string variables to hold game variables from teh server
  status = StringVar()
  question = StringVar()
  answer = StringVar()
  nextQuestion = StringVar()
  nextanswer = StringVar()
  contestants = StringVar()
  message = StringVar()
  
  columnWidth = 25 #specify the width of the main columns
  wrapMultipilcationConst = 9 #the wrapMultipilcationConst is the link between columnWidth, the size of the text and the number of pixels after which to wrap the text. The wrap width can be determined using it and the column width
  wrapWidth = columnWidth * wrapMultipilcationConst
  
  ttk.Label(mainFrame, textvariable=status, font=titleFont).grid(column=0, row=0, columnspan=4, sticky=N) #create a label holding the game status string variable; the status should take up columns 0-4 of the 0th row
  ttk.Label(mainFrame, text="Question", width=columnWidth, font=titleFont).grid(column=1, row=1, sticky=(W, N)) #create a label "Question" and place it in the 1st column of the 1st row
  ttk.Label(mainFrame, text="Answer", width=columnWidth, font=titleFont).grid(column=2, row=1, sticky=(W, N)) #create a label "Awnser" and place it in the 2nd column of the 1st row
  ttk.Label(mainFrame, text="Current", font=titleFont).grid(column=0, row=2, sticky=(W, N)) #create a label "Current" and place it in the 0th column of the 2nd row
  ttk.Label(mainFrame, text="Next", font=titleFont).grid(column=0, row=3, sticky=(W, N)) #create a label "Next" and place it in the 0th column of the 3rd row
  ttk.Label(mainFrame, textvariable=question, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=1, row=2, sticky=(W, N)) #create a label holding the contents of the current question and place it in the 1st column of the 2nd row
  ttk.Label(mainFrame, textvariable=answer, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=2, row=2, sticky=(W, N)) #create a label holding the contents of the current awnser and place it in the 2nd column of the 2nd row
  ttk.Label(mainFrame, textvariable=nextQuestion, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=1, row=3, sticky=(W, N)) #create a label holding the contents of the next question and place it in the 1st column of the 3rd row
  ttk.Label(mainFrame, textvariable=nextanswer, wraplength=wrapWidth, width=columnWidth, font=mainFont).grid(column=2, row=3, sticky=(W, N)) #create a label holding the contents of the next awnser and place it in the 2nd column of the 3rd row
  ttk.Label(mainFrame, text="Contestants", font=titleFont).grid(column=3, row=1, sticky=(W, N)) #create a label "Contestants" and place it in the 3rd column of the first row
  ttk.Label(mainFrame, textvariable=contestants, font=mainFont).grid(column=3, row=2, rowspan=2, sticky=(W, N)) #create a label containing the list of contestants and their scores (as a string)
  ttk.Label(mainFrame, text="Messages", font=titleFont).grid(column=0, row=4, sticky=N) #create a label "Messages" and place it in the 0th column of the 4th row
  ttk.Label(mainFrame, text="Game Updates", font=titleFont).grid(column=0, row=5, sticky=N) #create a label "Game Updates" and place it in the 0th column of the 5th row
  
  mainMenu = Menu(parent) #create a menu
  parent['menu'] = mainMenu #attach the menu to the parent as a menubar
  startFile = Menu(mainMenu, tearoff=0) #create some more menus
  startTools = Menu(mainMenu, tearoff=0)
  startHelp = Menu(mainMenu, tearoff=0)
  mainMenu.add_cascade(menu=startFile, label='File') #attach the additional menus to the menubar with the relevant labels
  mainMenu.add_cascade(menu=startTools, label='Tools')
  mainMenu.add_cascade(menu=startHelp, label='Help')
  
  startFile.add_command(label='Exit', command=close) #add a command to the file menu "Exit" which calls the close function to cleanly close the tkinter window
  
  startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress()))) #add a command to the tools menu "What is my IP?" and display the machines ip addresses in an infobox
  
  startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink")) #add a command to the help menu "About" displaying information about the application
  
  waitFrame = ttk.Frame(parent, padding="3 3 3 3") #create a frame with 3 pixels of space between it and its parent on all 4 sides
  waitFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the frame in the 0th column and 0th row of its parent
  waitFrame.columnconfigure(0, weight=1) #configure the 0th column of the waitFrame to expand at the same rate as the parents width
  waitFrame.rowconfigure(0, weight=1) #configure the 0th row of the waitFrame to expand at the same rate as the parents height
  
  ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N) #create a label "Connected to Server" and place it in the 0th column of the 0th row on the waitFrame
  ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N) #create a label "Waiting for Server to Start" and place it in the 0th column of the 1th row on the waitFrame
  
  waitFrame.grid_remove() #remove the waitFrame from the grid but remember the grid options used so waitFrame.grid() can be called in future without any arguments
  
  parent.protocol("WM_DELETE_WINDOW", close) #bind the X at the top right of the screen to the close function so that when it is pressed the GUI closses quickly
  
#close the window cleanly
def close():
  global mainTopLevel
  if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify() #if the mainTopLevel is a topLevel class show the parent of the toplevel
  mainTopLevel.destroy() #destroy the mainTopLevel

#Initialize the setup of the network and config
def setup():
  global socket, config
  socket = network.initClientSocket() #create a clientsocket and save it as a global variable
  print('Importing Config...')
  config = misc.initConfig() #Save the config to a global variable as a dictionary
  print('Config Imported')

#If the gui script it called directly create a root Tk() object
if __name__ == '__main__':
  setup() #Initial setup of the config and network
  root = Tk() #Create the root Tk() object
  root.title(config['Tk']['window_title']) #Set the title of the root Tk() object to the config value for window title
  initTk(root) #Create rest of the Tk windows with the root Tk() object as their parent
  root.mainloop() #Enter the Tk main loop handling any Tk events / callback