from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
from math import ceil
from sharedClasses import contestantClass
import time, os.path, network, misc, sharedClasses

running = False

#attempt to connect to the server using the address specified in the tkinter GUI
def start():
  global address, socket, startFrame, waitFrame
  if network.attemptConnect(socket, address.get(), config['server']['bindPort']): #attempt to connect to the server at the address specified in the tkinter GUI on the port specified in the config file using the clientsocket created
    startFrame.grid_forget() #remove the startFrame from the grid
    waitFrame.grid() #add the waitFrame to the grid
    network.addUsedType('gameStart') #add the type gameStart to the used types list
    isServerRunning() #check if the game has started and perform the relevant tasks if it has
  else: #if the connection was unsucessful
    messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"") #show an error message to this affect

#check if the game has started yet and perform the relevant tasks if it has
def isServerRunning():
  global startTopLevel, guiStartTopLevel, voteTopLevel, mainTopLevel
  if network.getMessageofType('gameStart', False): #get any messages of type gameStart with a non-blocking call
    network.removeUsedType('gameStart') #remove the gameStart type from the used types list
    network.addUsedType('rndStart') #add any types of message that we want to receive to the used types list
    network.addUsedType('askQuestion')
    network.addUsedType('responseWait')
    network.addUsedType('rndScoreUpdate')
    network.addUsedType('contestantUpdate')
    network.addUsedType('eliminationWait')
    network.addUsedType('finalStart')
    network.addUsedType('askFinalQuestion')
    network.addUsedType('headStart')
    network.addUsedType('winner')
    variableUpdates() #update the client variables with variables from the server
    startTopLevel.withdraw() #hide the startTopLevel
    voteTopLevel.deiconify() #show the voteTopLevel, guiStartTopLevel and mainTopLevel
    guiStartTopLevel.deiconify() 
    mainTopLevel.deiconify()
    disableButton() #disable any button presses
  else:
    if mainTopLevel.config()['class'][4] == 'Tk': #if the mainTopLevel is a root Tk instance use it to run this function again in 100ms
      mainTopLevel.after(100, isServerRunning)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a toplevel instance use its parent to run this function again in 100ms
      mainTopLevel.root.after(100, isServerRunning)
      
def startGUI():
  global socket, guiStartTopLevel, running
  network.sendMessage('startGUI', [None], socket)
  guiStartTopLevel.withdraw()
  running = True
  #Wait for a request from the server for a response before enabling the response buttons

#add or remove the given contestantClass to/from the game
#send a message to the server with the contestant class to remove as payload
def toggleContestant(contestantClass):
  global socket, voteTopLevel
  disableButton() #disable all button presses
  if contestantClass.uuid in [contestant.uuid for contestant in contestantList]: #if the given contestant class is in the list of contestants (ie if they are in the game) send a message to the server to remove the contestant from the game
    if messagebox.askokcancel("Confirm", "Remove " + contestantClass.name + " from the Game?", parent=voteTopLevel): #confirm the user wants to remove the contetant from the game
      network.sendMessage("removeContestant", contestantClass.uuid, socket)
  else: #if the given contestantClass is not in the game send a message to the server to add the contestant to the game
    if messagebox.askokcancel("Confirm", "Re-add " + contestantClass.name + " to the Game?", parent=voteTopLevel): #confirm the user wants to re-add the contestnt to the game
      network.sendMessage("addContestant", contestantClass.uuid, socket)
  
#send a question response to the server: response => response to send
def sendQuestionResponse(response):
  global socket
  disableButton() #disable all button presses
  network.sendMessage('quResponse', response, socket) #send the question response to the server
  
#enable all button presses
def enableButton():
  global mainButton
  misc.log('enable button')
  for name, button in mainButton.items():
    #for each button in the list of buttons log the enabling of the buttons name and enable the button
    misc.log('enabled ' + name)
    button.config(state='normal')
    
#disable all button presses
def disableButton():
  global mainButton
  misc.log('disable button')
  for name, button in mainButton.items():
    #for each button in the list of buttons log the disabling of the buttons name and disable the button
    misc.log('disabled ' + name)
    button.config(state='disabled')
    
#initiate the tkinter GUI
def initTk(parent):
  global address, mainQuestion, status, cur_money, bank, voteVar, voteButton, voteScore, voteLabel, config, startFrame, guiStartTopLevel, startTopLevel, mainTopLevel, voteTopLevel, waitFrame, mainFrame, finalFrame, mainButton, finalQuestion, finalStatus, finalName1, finalName2, finalScore1, finalScore2

  mainTopLevel = parent #save the parent as a global variable called mainTopLevl
  parent.title(config['Tk']['window_title']) #give the parent window the title specified in the config file
  parent.resizable(False, False) #setup the parent window so that it cannot be resized in either direction
  parent.withdraw() #hide the parent window
  
  startTopLevel = Toplevel(parent) #create a toplevel instance
  startTopLevel.title(config['Tk']['window_title']) #set the title of the toplevel to the value specified in the config file
  startTopLevel.resizable(False, False) #setup the toplevel so that it cannot be resized in either direction
  
  startMenu = Menu(startTopLevel) #create a menu
  startTopLevel['menu'] = startMenu #set the menu as the menubar for the startTopLevel
  startFile = Menu(startMenu, tearoff=0) #create some more menus
  startTools = Menu(startMenu, tearoff=0)
  startHelp = Menu(startMenu, tearoff=0)
  startMenu.add_cascade(menu=startFile, label='File') #add the menus to the menubar and give them labels
  startMenu.add_cascade(menu=startTools, label='Tools')
  startMenu.add_cascade(menu=startHelp, label='Help')
  
  startFile.add_command(label='Exit', command=close) #add an exit command to the file menu and bind it to the close function which cleanly closes the tkitner GUI
  
  startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress()))) #add a command to the tools menu that displays a list of the machines ip addresses formated as a string
  startTools.add_command(label='Send Message to Prompt', command=promptMessage) #add a command to the tools menu that calls the promptMessage function to allow the user to enter a message to send to the prompt
  
  startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink")) #add an about command to the help menu to display information about the application to the user in an info box
  
  startFrame = ttk.Frame(startTopLevel, padding="3 3 3 3") #create a new frame with 3 pixels of padding between it and the parent on all f4 sides
  startFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the startFrame in the 0th row of the 0th column of its parent
  startFrame.columnconfigure(0, weight=1) #setup the 0th column of the startFrame to expand at the same rate as the width of the window
  startFrame.rowconfigure(0, weight=1) #setup the 0th row of the startFrame to expand at the same rate as the height of the window
  
  address = StringVar() #create a string variable to hold the address of the server to connect to
  address.set(config['server']['bindAddress']) #set the default value of the address to the value specified in the config file
  
  ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N) #create a "Connect" button and place it in the 2nd row of the 1st column of the startFrame; the button calls the start function which attempts to connect to the server at the address specfied in the address entry widget
  ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N) #create an "Exit" button and place it in the 2nd row of the 2nd column of the startFrame; the button calls the close function which cleanly closes the tkinter GUI
  ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N) #create an entry widhet to contain the address of the server to connect to; place the widget in the 1st row of the 1st column of the startFrame
  ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N) #create a label "Server IP address" that identifies what to put in the entry widget; place the widget in the 1st row of the 2nd column
  
  guiStartTopLevel = Toplevel(parent) #create a toplevel instance
  guiStartTopLevel.title(config['Tk']['window_title']) #set the title of the toplevel to the value specified in the config file
  guiStartTopLevel.resizable(False, False) #setup the toplevel so that itssize cannot be altered in either direction
  
  guiStartFrame = ttk.Frame(guiStartTopLevel, padding="3 3 3 3") #create a frame with 3 pixels of padding between it and its parent on all 4 sides
  guiStartFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the frame in the 0th row of the 0th column of the gui toplevel
  guiStartFrame.columnconfigure(0, weight=1) #setup the 0th column of the frame to expand at the same rate as the toplevel
  guiStartFrame.rowconfigure(0, weight=1) #setup the 0th row of the frame to expand at the same rate as the toplevel
  
  ttk.Button(guiStartFrame, text='Start Game', width=100, command=startGUI).grid(column=0, row=0, sticky=N) #create a button to start the game and place it in the 0th row of the 0th column of the gui frame; bind the button to the startGUI function which sends a message to the server to start the gui/proceed with the game
  
  guiStartTopLevel.withdraw() #hide the gui toplevel
  
  mainFrame = ttk.Frame(parent, padding="3 3 3 3") #create a mainframe with 3 pixels of padding on all 4 sides between it and the parent
  mainFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the mainFrame in its parents grid in the 0th row of the 0th column
  mainFrame.columnconfigure(0, weight=1) #setup the 0th column to expand at the same rate as the toplevels width
  mainFrame.rowconfigure(0, weight=1) #setup the 0th row to expand at the same rate as the toplevels height

  #setup some tkinter variable to display game variables
  mainQuestion = StringVar()
  status = StringVar()
  cur_money = IntVar()
  bank = IntVar()

  ttk.Label(mainFrame, textvariable=status, width=100, background='red').grid(column=1, row=1, sticky=N) #create a label containing the status variable and place it in the 1st row of the 1st column of the mainFrame's grid
  ttk.Label(mainFrame, textvariable=mainQuestion, width=100).grid(column=1, row=2, sticky=N) #create a label containing the mainQuestion and place it in the 2nd row of the 1st column of the mainFrame's grid
  ttk.Label(mainFrame, text='Money: ').grid(column=4, row=1, sticky=N) #create a label "Money: " and place it in the 1st row of the 4th column
  ttk.Label(mainFrame, text='Bank: ').grid(column=4, row=2, sticky=N) #create a label "Bank: " and place it in the 2nd row of the 4th column
  ttk.Label(mainFrame, textvariable=cur_money).grid(column=5, row=1, sticky=N) #create a label containing the current money value and place it in the 1st row of the 5th column
  ttk.Label(mainFrame, textvariable=bank).grid(column=5, row=2, sticky=N) #create a label containing the value of money in the bank and place it in the 2nd row of the 5th column
  
  mainButton = {} #create a dictonary to hold the buttons in the mainFrame
  
  mainButton['correct'] = ttk.Button(mainFrame, text="Correct", command=lambda: sendQuestionResponse(1)) #create a button "Correct" and send the question response for correct to the server when it is pressed
  mainButton['correct'].grid(column=2, row=1, sticky=N)  #grid the correct button in the 1st row of the 2nd column of the mainFrame
  mainButton['incorrect'] = ttk.Button(mainFrame, text="Incorrect", command=lambda: sendQuestionResponse(2)) #create a button "Incorrect" and send the question response for incorrect to the server when it is pressed
  mainButton['incorrect'].grid(column=2, row=2, sticky=N)  #grid the incorrect button in the 2st row of the 2nd column of the mainFrame
  mainButton['bank'] = ttk.Button(mainFrame, text="Bank", command=lambda: sendQuestionResponse(3)) #create a button "Bank" and send the question response for bank to the server when it is pressed
  mainButton['bank'].grid(column=3, row=2, sticky=N) #grid the bank button in the 2st row of the 3nd column of the mainFrame
  mainButton['time'] = ttk.Button(mainFrame, text="Time Up", command=lambda: sendQuestionResponse(4)) #create a button "Time Up" and send the question response for time up to the server when it is pressed
  mainButton['time'].grid(column=3, row=1, sticky=N) #grid the time up button in the 1st row of the 3nd column of the mainFrame
  
  mainMenu = Menu(mainTopLevel) #create a menu
  mainTopLevel['menu'] = mainMenu #set the menu as the menubar for the main toplevel
  mainFile = Menu(mainMenu, tearoff=0) #create some more menus
  mainTools = Menu(mainMenu, tearoff=0)
  mainHelp = Menu(mainMenu, tearoff=0)
  mainMenu.add_cascade(menu=mainFile, label='File') #add the menus just created to the menubar with the relevant labels
  mainMenu.add_cascade(menu=mainTools, label='Tools')
  mainMenu.add_cascade(menu=mainHelp, label='Help')
  
  mainFile.add_command(label='Exit', command=close) #add an exit command to the file menu have it call the close function to cleanly close the tkinter gui
  
  mainTools.add_command(label='Goto Question...', command=gotoQuestion)
  mainTools.add_command(label='Send Message to Prompt', command=promptMessage) #add a command to send messages to the prompt and have it call a function to ask the user for the message to send
  
  mainHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink")) #add a command to the help menu "About" displaying information about the application
  
  finalFrame = ttk.Frame(parent, padding="3 3 3 3") #create a frame instance with 3 pixels of padding between it and its parent on all 4 sides
  finalFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the finalframe in the 0th row of the 0th column of its parents grid
  finalFrame.columnconfigure(0, weight=1) #configure the 0th column of the finalFrame to expand at the same rate as its toplevels width
  finalFrame.rowconfigure(0, weight=1) #configure the 0th row of the finalFrame to expand at the same rate as its toplevels height
  finalFrame.grid_remove() #remove the finalFrame from the grid but keep the grid settings so that finalFrame.grid() can be called again without arguments

  #create some tkinter variables to display the game variables
  finalQuestion = StringVar()
  finalStatus = StringVar()
  finalName1 = StringVar()
  finalName2 = StringVar()
  finalScore1 = IntVar()
  finalScore2 = IntVar()

  ttk.Label(finalFrame, textvariable=finalStatus, width=100, background='red').grid(column=1, row=1, sticky=N) #create a label to hold the status for the final round and place it in the 1st row of the 1st column of the finalFrame
  ttk.Label(finalFrame, textvariable=finalQuestion, width=100).grid(column=1, row=2, sticky=N) #create a label to hold the final question and place it in the 2nd row of the 1st column
  ttk.Label(finalFrame, textvariable=finalName1).grid(column=5, row=1, sticky=N) #create a label to hold the name of the 1st contestant in the final round and place it in the 1st row of the 5th column
  ttk.Label(finalFrame, textvariable=finalName2).grid(column=5, row=2, sticky=N) #create a label to hold the name of the 2nd contestant in the final round and place it in the 2st row of the 5th column
  ttk.Label(finalFrame, textvariable=finalScore1).grid(column=6, row=1, sticky=N) #create a label to hold the score of the 1st contestant in the final round and place it in the 1st row of the 6th column
  ttk.Label(finalFrame, textvariable=finalScore2).grid(column=6, row=2, sticky=N) #create a label to hold the score of the 2nd contestant in the final round and place it in the 2st row of the 6th column
  
  #add some more buttons to the dictionary containing all the buttons in the mainFrame
  mainButton['finalCorrect'] = ttk.Button(finalFrame, text="Correct", command=lambda: sendQuestionResponse(1)) #add a "Correct" button that when pressed send the correct question response to the server
  mainButton['finalCorrect'].grid(column=2, row=1, sticky=N) #grid the correct button in the 1st row of the 2nd column
  mainButton['finalIncorrect'] = ttk.Button(finalFrame, text="Incorrect", command=lambda: sendQuestionResponse(2)) #add an "Incorrect" button that when pressed send the incorrect question response to the server
  mainButton['finalIncorrect'].grid(column=2, row=2, sticky=N) #grid the incorrect button in the 2nd row of the 2nd column
  
  voteTopLevel = Toplevel(parent) #create a toplevel
  voteTopLevel.title(config['Tk']['window_title']) #set the title of the toplevel to the value specified in the config file
  voteTopLevel.resizable(False, False) #setup the toplevel so that it cannot be expanded in either direction
  
  voteTopLevel.withdraw() #hide the vore toplevel
  
  voteFrame = ttk.Frame(voteTopLevel, padding="3 3 3 3") #create a frame with 3 pixels of padding on all 4 sides
  voteFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the frame in the 0th row of the 0th column of the voteFrame
  voteFrame.columnconfigure(0, weight=1) #configure the 0th column of the voteFrame to expand at the same rate as its parents width
  voteFrame.rowconfigure(0, weight=1) #configure the 0th row of the voteFrame to expand at the same rate as its parents height
  
  ttk.Label(voteFrame, text="Contestants").grid(column=0, row=0) #create a label "Contestants" and place it in the 0th row of the 0th column of the voteFrame
  ttk.Label(voteFrame, text="Score").grid(column=1, row=0) #create a label "Score" and place it in the 0th row of the 1st column
  
  #create some list variables to hold the vote buttons/labels/variables for each contestant
  voteVar = [] #hold a list of tkinter variables containing the names of each contestant
  voteButton = [] #hold a list of tkinter buttons for each contestant
  voteScore = [] #hold a list of tkinter variables containing the score of each contestant
  voteLabel = [] #hold a list of tkinter labels for each contestant
  
  #for each contestant that will exist
  for i in range(0, config['questions']['contestantCnt']):
    voteVar.append(StringVar()) #create a tkinter variable to hold the contestant name
    voteScore.append(IntVar()) #create a tkinter variable to hold the contestant score
    voteLabel.append(ttk.Label(voteFrame, textvariable=voteScore[i])) #create a label where its value is the contestant score
    voteLabel[i].grid(column=1, row=i+1, sticky=N) #place this label in the 1+(contestants index) row of the 1st column of the voteFrame
    voteButton.append(ttk.Button(voteFrame, textvariable=voteVar[i])) #create a button where its value is the contestants name
    voteButton[i].grid(column=0, row=i+1, sticky=N) #place this button in the 1+(contestants index) row of the 0st column of the voteFrame
    voteButton[i].config(state='disabled') #disable the button so that it cannot be pressed
    
  waitFrame = ttk.Frame(startTopLevel, padding="3 3 3 3") #create a frame with 3 pixels of space between it and its parent on all 4 sides
  waitFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the frame in the 0th column and 0th row of its parent
  waitFrame.columnconfigure(0, weight=1) #configure the 0th column of the waitFrame to expand at the same rate as the parents width
  waitFrame.rowconfigure(0, weight=1) #configure the 0th row of the waitFrame to expand at the same rate as the parents height
  
  ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N) #create a label "Connected to Server" and place it in the 0th column of the 0th row on the waitFrame
  ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N) #create a label "Waiting for Server to Start" and place it in the 0th column of the 1th row on the waitFrame
  
  waitFrame.grid_remove() #remove the waitFrame from the grid but remember the grid options used so waitFrame.grid() can be called in future without any arguments
  
  #bind the red X in the top right hand corner of each of the toplevels to the close function to close the GUI cleanly
  mainTopLevel.protocol("WM_DELETE_WINDOW", close)
  startTopLevel.protocol("WM_DELETE_WINDOW", close)
  voteTopLevel.protocol("WM_DELETE_WINDOW", close)
   
#ask the user for a message to send to the prompt
def promptMessage():
  global socket
  message = simpledialog.askstring("Send Message to Prompt", "Message:") #ask the user for a message to send
  network.sendMessage('promptMsg', message, socket) #send the message to the server as a promptMsg
  
def gotoQuestion():
  global socket, running
  if running:
    questionNo = simpledialog.askinteger("Go to question...", "Question Number:")
    if questionNo:
      disableButton()
      network.sendMessage('gotoQu', questionNo, socket)
  else:
    messagebox.showerror("Error", "Server has not Started Running Yet!")
  
#close the tkinter GUI cleanly
def close():
  global mainTopLevel, startTopLevel, voteTopLevel
  startTopLevel.destroy() #destroy the startTopLevel
  voteTopLevel.destroy() #destroy the voteTopLevel
  if mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a toplevel class show its parent
    mainTopLevel.root.deiconify()
  mainTopLevel.destroy() #destroy the mainTopLevels
  
#update the clientside variables with the values given out by the server
def variableUpdates():
  global mainQuestion, status, cur_money, bank, round, contestantList, mainTopLevel, startTopLevel, mainFrame, finalFrame, voteVar, voteScore, voteButton, voteLabel
  
  if network.messageInBuffer('rndStart'): #if a rndStart message exists in the message buffer
    [round] = network.getMessageofType('rndStart', False) #get the message from the buffer with a non-blocking call and save it to the local variable round
    status.set('Round ' + str(round) + ' starting') #update the status with the current round number
    
  if network.messageInBuffer('askQuestion'): #if an askQuestion message exists in the message buffer
    rQuestion, contestant, question, answer = network.getMessageofType('askQuestion', False) #the the round question number, contestant name, question and awnser from the message buffers
    status.set('Round ' + str(round) + ' Question ' + str(rQuestion)) #update the status with the round and uestion numbers
    mainQuestion.set(contestant + ': ' + question) #ask the current contestant the question
    
  if network.getMessageofType('responseWait', False): #if a message of type responseWait exists in the buffer
    enableButton() #enable button presses
    
  if network.messageInBuffer('rndScoreUpdate'): #if a message of type rndScoreUpdate exists in the message buffer
    moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False) #get the current money index, list of money values and current bank value from the message buffer with a non-blocking call
    cur_money.set(money[moneyCount]) #set the value of the current money to the value given by the message
    bank.set(bankVal) #set the value of the bank to the value given by the message
    
  if network.messageInBuffer('contestantUpdate'): #if a message of type contestantUpdate exists in the message buffer
    contestantList = network.getMessageofType('contestantUpdate', False) #get the message from the buffer with a non-blocking call
    for i in range(0, config['questions']['contestantCnt']): #for each contestant index that can exist (not just the contestants that do exist)
      try: #attempt to...
        voteVar[i].set(contestantList[i].name) #set the voteVar to the name of the contestant
        voteScore[i].set(contestantList[i].score) #set the voreScore to the score of the contestant
        voteButton[i].config(command=lambda contestantClass=contestantList[i]: toggleContestant(contestantClass), state='disabled') #setup a button to remove the contestant from the game
      except IndexError: #if a contestant doesn't exist at the current index (i)
        voteButton[i].grid_forget() #remove the button for the contestant from the grid
        voteLabel[i].grid_forget() #remove the label for the contestant from the grid
    
  if network.getMessageofType('eliminationWait', False): #if a message of type eliminationWait exists in the message buffer
    for button in voteButton: #foreach button in the list
      button.config(state='normal') #enable the button
    
  if network.getMessageofType('finalStart', False): #if a message of type finalStart exists in the buffer
    mainFrame.grid_remove() #remove the mainFrame from its parents grid
    finalStatus.set('Final Round starting') #update the status with the relevant message
    finalFrame.grid() #place the finalFrame in the grid
    
  if network.messageInBuffer('askFinalQuestion'): #if a message of type askFinalQuestion exists in the message buffer
    rQuestion, contestant, question, answer = network.getMessageofType('askFinalQuestion', False) #get the question number, contestant class, question and awnser from the message name
    finalStatus.set('Final Question ' + str(rQuestion)) #update the status with the question number
    finalQuestion.set(contestant + ': ' + question) #ask the current contesant the question
    if finalName1.get() == '': #if the tkinter variables holfing thename of the contestants in the final round are not set; set the names to the 2 contestants in the list of contesatants
      finalName1.set(contestantList[0].name) #set the first contestants name to the name of the first contestant
      finalName2.set(contestantList[1].name) #set the second contestants name to the name of the second contestant
    finalScore1.set(contestantList[0].score) #set the tkinter variable holding the first contestants score to the score of the first contestant
    finalScore2.set(contestantList[1].score) #set the tkinter variable holding the second contestants score to the score of the second contestant
    
  if network.getMessageofType('headStart', False): #if a message of type headStart exists in the message buffer
    finalStatus.set('Going to Head to Head Round') #update the status with the relevant message
    finalQuestion.set('') #clear the finalQuestion tkinter variable
    
  if network.messageInBuffer('winner'): #if a message of type winner exists in the message buffer
    [winner] = network.getMessageofType('winner', False) #save the winning contestant class as a local variable
    finalStatus.set(winner.name + ' is the winner!') #update the status with a relevant message
    finalQuestion.set('') #clear the finalQuestion tkinter variable
    
  try:
    if mainTopLevel.config()['class'][4] == 'Tk': #if the mainTopLevel is a Tk root instance use it to run this function again in 100ms
      mainTopLevel.after(100, variableUpdates)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a TopLevel instance use its parent to run this function again in 100ms
      mainTopLevel.root.after(100, variableUpdates)
  except TclError:
    #on error exit cleanly
    pass

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