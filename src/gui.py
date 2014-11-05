from tkinter import *
from tkinter import ttk, messagebox
import pygame, operator, os.path, network, misc
from pygame.locals import *

#initiate the pygame GUI
def initPygame():
  global displaySurface, FPS, fpsClock, white, blue, black, yellow
  pygame.init() #setup the pygame display

  FPS = config['pygame']['fps'] #get the FPS from the config file and save it to a global variable
  fpsClock = pygame.time.Clock() #create an fpsClock to limit the number of updates to the display every second

  width = config['pygame']['width'] #get the width of the display from the config file
  height = config['pygame']['height'] #get the height of the display from the config file

  displaySurface = pygame.display.set_mode((width, height), FULLSCREEN if config['pygame']['fullscreen'] == True else 0) #get the main pygame surface and save it to a global variable; setup the display with the parameters specified in the config file
  pygame.display.set_caption(config['pygame']['window_title']) #set the caption of the pygame window to the value specified in the config file

  #setup colours and save them to global variables
  white = pygame.Color(255, 255, 255)
  blue = pygame.Color(0, 100, 255)
  black = pygame.Color(0, 0, 0)
  yellow = pygame.Color(194, 99, 0)

#create a class to hold a money value
class moneyPlaceholder():
  #initialize the class
  #surface => surface onto which to draw the money value
  #coordinates => tuple coordinates to place the centre of the money placeholder at
  #text => value of the money placeholder
  #font => font to render the text in
  #textColour => colour in which to render the text
  #active => bool => money value acheived or not acheived?
  def __init__(self, surface, coordinates, text, font=None, textColour=None, active=False):
    #save the surface, centre coordinates, active (state) as attributes of the class
    self.surface = surface
    self.coordinates = coordinates
    self.active = active
    #draw a placeholder of the current state (active/inactive) passing the values given to the constructor as parameters
    self.draw(text, font, textColour)
    
  #draw the placeholder on the given surface
  #text => text to draw
  #font => font to render the text in
  #textColour => colour to draw the text in
  def draw(self, text=None, font=None, textColour=None):
    if not textColour: textColour = pygame.Color(0, 0, 0) #if no value for the colour of the text is given use black
    if not font: font = pygame.font.SysFont(config['pygame']['font'], int(self.surface.get_height() / 25)) #if no font is specified use the font face specified in the config file and scale it relative to the height of the window
    if self.active: moneyImage = pygame.image.load('resources\\redPlaceholder.png') #if the placeholder is active use the red image from the resources folder
    else: moneyImage = pygame.image.load('resources\\bluePlaceholder.png') #otherwise if the placeholder is inactive use the blue image from the resources folder
    moneyImage = pygame.transform.scale(moneyImage, (int(self.surface.get_width() / (160 / 27)), int(self.surface.get_height() / (40 / 3)))) #scale the image from the file relative to the size of the window
    self.surface.blit(moneyImage, self.coordinates) #place the image at the coordinates specified when the placeholder was initialized
    if text: #if there is text to render
      self.text = font.render(text, True, textColour) #render the text using the font and colour of text specified when the placeholder was initalized and render the text in antiAnalyzing font
      self.textRect = self.text.get_rect() #get the coordinates of the text
      self.textRect.center = tuple(map(operator.add, moneyImage.get_rect().center, self.coordinates)) #set the textRect's centre to the middle of the image we just drew on the surface
    self.surface.blit(self.text, self.textRect) #draw the text on the screen
    
  #activate the placeholder
  def activate(self):
    self.active = True #set the active parameter
    self.draw() #draw the updates object
    
  #deactice the placeholder
  def deactivate(self):
    self.active = False #set the active parameter
    self.draw() #draw the updates object
    
#create a class to hold a final awnser
#state can be correct, incorrect or inactive (neutral as the question has yet to be asked)
class answerPlaceholder():
  #initialize the class
  #surface => surface onto which to draw the money value
  #coordinates => tuple coordinates to place the centre of the money placeholder at
  #font => font to render the text in
  #textColour => colour in which to render the text
  def __init__(self, surface, coordinates, font=None, textColour=None):
    #save the surface and centre coordinates as attributes of the class
    self.surface = surface
    self.coordinates = coordinates
    #draw the placeholder on the surface at the coordinates specifed
    self.draw(None, font, textColour)
    
  #draw the placeholder on the surface at the cooordinates specified
  #state => bool => none - blue no symbo;l true - blue and tick; false - red and cross
  #font => font to render the text in
  #textColour => colour in which to render the text
  def draw(self, state=None, font=None, textColour=None):
    if not textColour: textColour = pygame.Color(0, 0, 0) #if no value for the colour of the text is given use black
    if not font: font = pygame.font.SysFont(config['pygame']['font'], int(self.surface.get_height() / 25)) #if no font is specified use the font face specified in the config file and scale it relative to the height of the window
    if state == False: answerImage = pygame.image.load('resources\\incorrectRed.png') #if the state is false use the red incorrect symbol from the resources folder
    elif state == True: answerImage = pygame.image.load('resources\\correctBlue.png') #if the state is true use the blue correct symbol from the resources folderr
    else: answerImage = pygame.image.load('resources\\neutralBlue.png') #if the state is none use the blue waiting for awnser symbol from the resources folder
    answerImage = pygame.transform.scale(answerImage, (int(self.surface.get_width() / 10), int(self.surface.get_height() / (40 / 3)))) #scale the image from the file relative to the size of the window
    self.surface.blit(answerImage, self.coordinates) #place the image at the cooredinates specified when the object was initialized
    
  #change the state and image of the placeholder to correct
  #font => font to render the text in
  #textColour => colour in which to render the text
  def correct(self, font=None, textColour=None):
    self.draw(True, font, textColour)
    
  #change the state and image of the placeholder to incorrect
  #font => font to render the text in
  #textColour => colour in which to render the text
  def incorrect(self, font=None, textColour=None):
    self.draw(False, font, textColour)

#draw some wrapped text
#surface => surface onto which to draw the text
#rectCoords => tuple (length 4) specifying the text bound
#text => text to draw
#font => font to render the text in
#textColour => colour in which to render the text
#center => bool => aligment to use (false => left; true => center)
def wrapText(surface, rectCoords, text, font, textColour, center=False):
  rect = pygame.Rect(rectCoords) #create a rect object from the coordinates
  lineHeight = font.get_height() #get the height of a single line of text
  lineWidth = 0 #the current line width is 0 as there is no text in the current line
  lineNumber = 0 #the current line is the 0th line
  line = "" #the current line has no content
  
  #get each line one at a time
  for escapeLine in text.split("\n"):
    curLine = escapeLine.split(" ") #get a list of each word in the line
    if len(curLine) == 0: #if there are no words in the current line ie "\n\n" draw a blank space on the current line
      curLine = [" "]
    for word in curLine: #get each woord in the curent line one at a time
      #font.size(word + " ")[0] returns the size of the as a tuple (x, y) and get the x size
      #add the x size to the width of the line and check it is less than or equal to the width of the coordinates specified
      #check if when the word is added to the line the line will still fit in the coordinates specified
      if lineWidth + font.size(word + " ")[0] <= rect.width:
        line += word + " " #add the word to the line together with a space
        lineWidth += font.size(word + " ")[0] #add the size of the word plus a space to the line width
        if word != curLine[-1]: #process the next word if the word is not the last word in the current line
          continue
      
      #if the word will not fit on the line or the word is the last word in the current line then render the line
      if lineWidth + font.size(word + " ")[0] > rect.width or word == curLine[-1]:
        fontSurface = font.render(line, True, textColour) #render the text and get the surface object returned by this function
        fontRect = fontSurface.get_rect() #get the coordinates of the text surface
        if center:
          #align the text centrally
          #rect.top + lineNumber * lineHeight get the y coord of the top of the line of text
          fontRect.midtop = (rect.centerx, rect.top + lineNumber * lineHeight)
        else:
          #align the text to the left
          fontRect.topleft = (rect.left, rect.top + lineNumber * lineHeight)
        surface.blit(fontSurface, fontRect) #place the text surface onto the surface we are drawing onto at the coordinates given in fontRect
        lineNumber += 1 #increment the lineNumber
        line = word + " " #add the word plus a space to the current line
        lineWidth = font.size(word + " ")[0] #set the width of the line to the width of the word
        
        if lineNumber * lineHeight > rect.height: #if the next line will not fit in the space provided don't process any more words
          break
          
    if lineNumber * lineHeight > rect.height: #if breaking break out of both loops
      break    
  
#draw a question onto the displaySurface
#round => round number
#roundQuestion => current question number
#question => the question to draw onto the displaySurface
def drawQuestion(round, roundQuestion, question):
  displaySurface.fill(blue) #fill the display surface with the colour blue -> i.e clear the display
  mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15)) #create a font and scale it to the height of the displaySurface
  titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (120 / 11))) #create another font that is bigger than the mainFont -> again the size is relative to the displaySurface size
  titleFont.set_underline(True) #the title font should be underlined

  titleText = titleFont.render('Round ' + str(round) + ' Question ' + str(roundQuestion), True, yellow) #render the round and question number, antianylizing and in yellow
  titleRect = titleText.get_rect() #get the coordinates of the titleText
  titleRect.topleft = (int(displaySurface.get_width() / (120 / 31)), int(displaySurface.get_height() / 80)) #place the topleft of the titleText at the top of the displaySurface -> the coords are relative to the size of the displaySurface
  displaySurface.blit(titleText, titleRect) #place the title text on the displaySurface

  wrapText(displaySurface, (int(displaySurface.get_width() / (120 / 31)), int(titleRect.bottom + (displaySurface.get_height()  / 80)), int(displaySurface.get_width() - (displaySurface.get_width() / (40 /11))), int(displaySurface.get_height()  - (titleRect.height + (displaySurface.get_height()  / 80)))), question, mainFont, yellow) #draw the question onto the screen using the mainFont, colour yellow, at coords relative to the size of the displaySurface -> the right 5/6 of the screen basically
  
#update the scores for the current round
#correctIndex => the index in the money list of the current money value
#money => list of money values
#bank => current value of the bank
def updateRndScores(correctIndex, money, bank):
  if 0 in money: money.remove(0) #remove the value of 0 if it exists in the money list
  money.reverse() #reverse the order of the list
  moneyPlaceholderList = {} #create a dict to hold the money placeholders

  for value in money: #iterate through each money value in turn
    moneyPlaceholderList[value] = moneyPlaceholder(displaySurface, ((int(displaySurface.get_width() / 80)), int((displaySurface.get_height()  / 60) + (displaySurface.get_height()  / (120 / 11)) * money.index(value))), '£' + str(value), textColour = white) #create a moneyPlaceholder for the money value where the coordinates are relative to the size of the screen and the position of the money value in the list of money values; the value of the moneyPlaceholder is concatanated with a £ sign; the colour of the text is white
  
  money.reverse() #reverse the list of money values so that it is back in its original order

  for i in range(0, correctIndex): #go through each index in turn between the 0th index and the index of the current money value
    moneyPlaceholderList[money[i]].activate() #active the money placeholder for that value
      
  bank = moneyPlaceholder(displaySurface, (int(displaySurface.get_width() / 80), int(displaySurface.get_height()  - (displaySurface.get_height()  / (120 / 13)))), "Bank £" + str(bank), textColour = white, active = True) #create a moneyPlaceholder for the bank value concatanate the value of the bank with "Bank £"; use white text; active the placeholder on creation

#draw a question for the final round
#questionCnt => question number of the current question
#question => the question to draw
#contestants => a list (length 2) of contestantClasses currently in the game
def drawFinalQuestion(questionCnt, question, contestants):
  #lastResult true=correct false=incorrect
  displaySurface.fill(blue) #fill the display surface with the colour blue
  mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15)) #create a font and scale it to the height of the displaySurface
  titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (120 / 11))) #create another font that is bigger than the mainFont -> again the size is relative to the displaySurface size
  titleFont.set_underline(True) #underline the titleFont
  
  titleText = titleFont.render('Final Round Question ' + str(questionCnt), True, yellow) #render the question number; use antianylizing; using text colour yellow
  titleRect = titleText.get_rect() #get the coordinates of the titletext
  titleRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height()  / 80)) #place the titletext at the top of the displaySurface in the middle of the displaySurface => coordinates are relative to the size of displaySurface
  displaySurface.blit(titleText, titleRect) #draw the title text onto the displaySurface at the coordinates specified
  
  wrapText(displaySurface, (int(displaySurface.get_width() / 80), int(titleRect.bottom + (displaySurface.get_height()  / 80)), int(displaySurface.get_width() - (displaySurface.get_width() / 80)), int(displaySurface.get_height()  - (titleRect.height + (displaySurface.get_height()) * 3 / 7))), question, mainFont, yellow) #draw the question in the middle of the displaySurface; coordinates are relative to the size of the screen; text is drawn in yellow mainFont
  
  mainText = mainFont.render(contestants[0].name + ':', True, yellow) #render the first contestants name in antianylizing yellow mainFont
  mainRect = mainText.get_rect() #get the coordinates of the mainText
  mainRect.topright = (int(displaySurface.get_width() * 2 / 5), int((displaySurface.get_height() - titleRect.height) * 5 / 7)) #place the topright corner of the mainText at the bottom left of the displaySurface (coorinates are relative to the size of the displaySurface)
  displaySurface.blit(mainText, mainRect) #draw the mainText onto the displaySurface
  
  mainText = mainFont.render(contestants[1].name + ':', True, yellow) #render the second contestants name in antianylizing yellow mainFont
  mainRect = mainText.get_rect() #get the coordinates of the mainText
  mainRect.topright = (int(displaySurface.get_width() * 2 / 5), int((displaySurface.get_height() - titleRect.height) * 6 / 7)) #place the topright corner of the mainText at the bottom left of the displaySurface (coorinates are relative to the size of the displaySurface)
  displaySurface.blit(mainText, mainRect) #draw the mainText onto the displaySurface
  
  answerPlaceholder1 = {} #create a dict for contestant1's awnsers
  answerPlaceholder2 = {} #create a dict for contestant2's awnsers
  
  for i in range(2, 7):
    answerPlaceholder1[i] = answerPlaceholder(displaySurface, (int(displaySurface.get_width() * ((i+2) / 9)), int((displaySurface.get_height() - titleRect.height) * 5 / 7)))
    if contestants[0].finalScore[i - 2] == True:
      answerPlaceholder1[i].correct()
    elif contestants[0].finalScore[i - 2] == False:
      answerPlaceholder1[i].incorrect()
    answerPlaceholder2[i] = answerPlaceholder(displaySurface, (int(displaySurface.get_width() * ((i+2) / 9)), int((displaySurface.get_height() - titleRect.height) * 6 / 7)))
    if contestants[1].finalScore[i - 2] == True:
      answerPlaceholder2[i].correct()
    elif contestants[1].finalScore[i - 2] == False:
      answerPlaceholder2[i].incorrect()
    
#draw the Head2Head round => draw the name and score for each contestant
#questionCnt => head2head round question number
#contesants => list of all contestants in the game (len should be 2)
def drawHead2Head(questionCnt, contestants):
  displaySurface.fill(blue) #fill the display surface with the colour blue i.e clear the display
  mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15)) #create a font using the font-face specified in the config file and scale it to the height of the display
  titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (160 / 11))) #create another font and scale it to the height of the display so that it is bigger than the mainFont
  titleFont.set_underline(True) #underline the title font
  subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11))) #create a font the same size as the subTitleFont but this time don't underline the font
  
  titleText = titleFont.render('Head To Head Round', True, yellow) #reader a title using yellow antianylising font
  titleRect = titleText.get_rect() #get the size of the title
  titleRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height()  / 80)) #place the title at the top of the screen in the middle
  displaySurface.blit(titleText, titleRect) #draw the title onto the display at the coordinates specified
  
  subText = subTitleFont.render('Question ' + str(questionCnt), True, yellow) #render the question number using yellow antianylising font
  subTextRect = subText.get_rect() #get the size of the question number
  subTextRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (80 / 7))) #place the question number in the middle of the screen just below the title
  displaySurface.blit(subText, subTextRect) #draw the question number onto the screen at the coordinates specified
  
  mainText = mainFont.render(contestants[0].name + ' : ' + str(contestants[0].score), True, yellow) #render the name and score of the first contestant using yellow antianylising mainFont
  mainRect = mainText.get_rect() #get the size of the text
  mainRect.midtop = (int(displaySurface.get_width() / 2), int((displaySurface.get_height() - titleRect.height) * 4 / 7)) #place the text in the middle of the screen just below the tile
  displaySurface.blit(mainText, mainRect) #draw the text onto the screen
  
  mainText = mainFont.render(contestants[1].name + ' : ' + str(contestants[1].score), True, yellow) #render the name and score of the second contestant using yellow antianylising mainFont
  mainRect = mainText.get_rect() #get the size of the text
  mainRect.midtop = (int(displaySurface.get_width() / 2), int((displaySurface.get_height() - titleRect.height) * 5 / 7)) #place the text in the middle of the screen below the text for the first contestant
  displaySurface.blit(mainText, mainRect) #draw the text onto the screen
  
#draw Time Up on a screen for when a round ends becuase Time is Up
#round => round number for the round which has just ended
#contestants => list containing the contestant classes of all the contestants in the round that has just ended
def drawTime(round, contestants):
  drawEnd(round, contestants, 'Time Up') #draw the round number, contestants scores and the message Time Up

#draw All Correct on a screen for when a round ends becuase All the Questions in that round where correctly awnsered
#round => round number for the round which has just ended
#contestants => list containing the contestant classes of all the contestants in the round that has just ended
def drawCorrect(round, contestants):
  drawEnd(round, contestants, 'You got all the Questions Correct') #draw the round number, contestants and the message You got all the Questions Correct

#draw the end of a round
#round => round number for the round which has just ended
#contestants => list containing the contestant classes of all the contestants in the round that has just ended
#line1 => message describing why the round just ended to be drawn at the top of the screen
def drawEnd(round, contestants, line1):
  displaySurface.fill(blue) #fill the display surface with the colour blue i.e clear the display
  mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 20)) #create a font and scale it to the height of the displaySurface
  titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (160 / 11))) #create another font that is bigger than the mainFont -> again the size is relative to the displaySurface size
  titleFont.set_underline(True) #underline the titleFont
  subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11))) #create a font the same size as the titleFont but with no underline
  
  line1Text = titleFont.render(line1, True, yellow) #render the line line1 text in the titleFont with AntiAnylizing yellow text
  line1Rect = line1Text.get_rect() #get the coordinates of the timeUp text
  line1Rect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / 80)) #place midtop of the text rect in the middle of the displaySurface at the top of the displaySurface
  displaySurface.blit(line1Text, line1Rect) #place the line1Text at the coordinates specified
  
  endofRound = subTitleFont.render('End of Round ' + str(round), True, yellow) #render the round number with AntiAnylizing yellow text
  endofRoundRect = endofRound.get_rect() #get the coordinates of the endofRoundRect text
  endofRoundRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (80 / 7))) #place the midtop of the text rect in the middle of the displaySurface immediatly below the line1Text
  displaySurface.blit(endofRound, endofRoundRect) #place the endOfRound text at the coordinates specified
  
  weakestLink = mainFont.render('You must now choose the weakest link', True, yellow) #render the text "You must now choose the weakest link" in the mainFont with AntiAnylizing and in yellow
  weakestLinkRect = weakestLink.get_rect() #get the coordinates of the weakestLink text
  weakestLinkRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (40 / 9))) #place the text in the middle of the displaySurface below the endofRound text => coordinates are relative to the size of the displaySurface
  displaySurface.blit(weakestLink, weakestLinkRect) #place the weakestLink text at the coordinates specified on the displaySurface
  
  y = int(displaySurface.get_height() / (80 / 27)) #set the variable y to be just below the weakestLink text
  
  #loop through the index of each contestant in the list
  for i in range(0, len(contestants)):
    contestantText = mainFont.render(contestants[i].name + ': ' + str(contestants[i].score), True, yellow) #render the name and score of the contestant at the current index with AntiAnylizing text in yellow font
    contestantRect = contestantText.get_rect() #get the coordinates of the contestantText
    #divide the list of contestants into two lists
    if i % 2 == 0: #if the index of the contestant is even (the 0th index counts as even)
      #place the contestantText in the left column
      contestantRect.midtop = (int(displaySurface.get_width() / 3), y)
    else: #otherwise the index of the contestant must be odd
      #place the contestantText in the right column
      contestantRect.midtop = (int(2 * displaySurface.get_width() / 3), y)
      y += int(displaySurface.get_height() / 16) #increase the y coordinate by a distance relative to the height of the display
    displaySurface.blit(contestantText, contestantRect) #draw the name and score of the contesant at the coordinates specified
  
#draw the start of a round onto the screen
#round => round number of the round that is starting
def drawRoundStart(round):
  drawStart("Round " + str(round) + " Starting") #draw the rund number together with a sutiable message onto the screen
  
#draw the start of the final round onto the screen
#contestants => list (of length 2) of contestant classes
def drawFinalStart(contestants):
  drawStart("Final Round Starting", contestants[0].name + " vs " + contestants[1].name) #draw the names of the two contesants together with a sutiable message onto the screen
  
#draw the start of the head2head round onto the screen
def drawHead2HeadStart():
  drawStart("Going to Head to Head Round") #draw a sutiable message onto the screen
  
#draw the start of a round onto the screen
#text1 => first line of text to draw
#text2 => second line of text to draw (optional)
def drawStart(text1, text2=None):
  displaySurface.fill(blue) #fill the display surface with the colour blue i.e. clear the display
  subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11))) #create a font with the font-face specified in the config file and scale it to the height of the display
  
  text1 = subTitleFont.render(text1, True, yellow) #render the text with the font we just created using yellow AntiAnylising text
  textRect1 = text1.get_rect() #get the size of the text
  textRect1.center = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() * 1 / 3)) #place the centre of the text in the centre of the x axis and 1/3 of the way down the screen
  displaySurface.blit(text1, textRect1) #draw the text onto the display at the coordinates specified
  
  if text2: #if a second line of text is specified
    text2 = subTitleFont.render(text2, True, yellow) #render the text with the font we just created using yellow AntiAnylising text
    textRect2 = text2.get_rect() #get the size of the text
    textRect2.center = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() * 2 / 3)) #place the centre of the text in the centre of the x axis and 2/3 of the way down the screen
    displaySurface.blit(text2, textRect2) #draw the text onto the display at the coordinates specified
    
#display the name of the winning contestant on the screen
#winner => name of the contestant who won the game
def displayWinner(winner):
  drawCentreText(winner + ' is the Winner!') #draw the name of the contestant onto the screen together with a sutiable message
  
#display the name of an eliminated contestant on the screen
#contestantName => name of the eliminated contestant
def displayEliminated(contestantName):
  drawCentreText(contestantName + ' you are the Weakest Link Goodbye!') #draw the name of the contestant onto the screen together with a sutiable message
  
#draw the text in the middle of the screen
#text => text to draw onto the screen; will be automatically wrapped to fit onto the screen
def drawCentreText(text):
  displaySurface.fill(blue) #fill the display surface with the colour blue i.e. clear the display
  subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11))) #create a font with the font-face specifed in the config file and scale the height of the font to the height of the display 
  wrapText(displaySurface, (int(displaySurface.get_width() / 80), int(displaySurface.get_height() / 3), int(displaySurface.get_width() - (displaySurface.get_width() / 80)), int(displaySurface.get_height() - (displaySurface.get_height() / 80))), text, subTitleFont, yellow, True) #draw the text onto the screen leaving a small border on the left and right of the text and start the first line of text 1/3 of the way down the screen; use the font that we just created and draw the text with AntiAnylizing yellow font

#main game loop
def gameLoop():
  global socket
  end = head2head = responseWait = False #setup some boolean varaibles used to keep track of the game status, if it is a head2head round and if currently waiting for a response
  while True: #loop until the loop is broken
    for event in pygame.event.get(): #get all the events that have occured and process them
      if event.type == QUIT or event.type == KEYDOWN and event.dict['key'] == 27: #if the red X at the top right of the screem or the ESC key is pressed quit the game (key 27 is the esc key)
        close() #close the GUI cleanly
        end = True #break out of both loops
        break
      elif event.type == KEYDOWN and event.dict['key'] == 292: #key 292 is F11)
        pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), FULLSCREEN) #change the GUI to fullscreen mode
      elif event.type == KEYDOWN and event.dict['key'] == 291: #(key 291 is F10)
        pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), 0) #change the GUI to window mode
    if end: break #break out of the loop
    
    if network.messageInBuffer('rndStart'): #if a message of type rndStart exists in the message buffer
      [round] = network.getMessageofType('rndStart', False) #get the message from the buffer with a non-blocking call and save the round number to a local variable
      drawRoundStart(round) #draw the start of a round using the current round number
      
    if network.messageInBuffer('rndScoreUpdate'): #if a message of type rndScoresUpdate exists in the message buffer
      moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False) #get the message from the buffer with a non-blocking call and save the current money count, list of money values and bank values as local variables
      if responseWait: updateRndScores(moneyCount, money, bankVal) #if currently waiting for a response draw the scores for the current round on the display with the values that have just been received
      
    if network.getMessageofType('correctAns', False): #try to get a message of type correctAns from the message buffer with a non-blocking call
      drawCentreText('Correct') #if successful in getting a message from the buffer update the display with the fact that the awnser was correct
      responseWait = False #no longer waiting for a response as an answer has been received
    
    if network.getMessageofType('incorrectAns', False): #try to get a message of type incorrectAns from the message buffer with a non-blocking call
      drawCentreText('Incorrect') #if successful in getting a message from the buffer update the display with the fact that the awnser was incorrect
      responseWait = False #no longer waiting for a response as an awnser has been received
      
    if network.messageInBuffer('contestantUpdate'): #check if a message of type contestantUpdate exists in the message buffer
      contestantList = network.getMessageofType('contestantUpdate', False) #if a message exists get the message with a non-blocking call and save the list of contestant classes to a local variable
      
    if network.messageInBuffer('askQuestion'): #check if a message of type askQuestion exists in the message buffer
      rQuestion, contestant, question, answer = network.getMessageofType('askQuestion', False) #if a message exists get the message with a non-blocking call and save the round question number, contestant, question and answer from the message buffer
      drawQuestion(round, rQuestion, question) #draw the question on the screen together with the round and question numbers
      updateRndScores(moneyCount, money, bankVal) #draw the scores for the current round onto the screen
      responseWait = True #now waiting for a response
      
    if network.getMessageofType('allCorrect', False): #try to get a message of type allCorrect from the message buffer with a non-blocking call
      drawCorrect(round, contestantList) #if successful in getting a message from the buffer update the display with the fact that all questions in the last round were awnsered correctly
      responseWait = False #no longer waiting for a response as a response has been received
      
    if network.getMessageofType('timeUp', False): #try to get a message of type timeUp from the message buffer with a non-blocking call
      drawTime(round, contestantList) #if successful in getting a message from the buffer update the display with the fact that the time for the last round is up
      responseWait = False #no longer waiting for a response as a response has been received
      
    if network.messageInBuffer('contestantEliminated'): #check if a message of type contestantEliminated exists in the message buffer
      [contestantClass] = network.getMessageofType('contestantEliminated', False) #if a message exists get the message with a non-blocking call and save the contestant class to a local variable
      displayEliminated(contestantClass.name) #update the display with the name of the eliminated contestant
    
    if network.getMessageofType('finalStart', False): #try to get a message of type finalStart with a non-blocking call
      drawFinalStart(contestantList) #if successful in getting a message from the buffer update the display with the fact that the final round is starting and the names of the contestants taking part in the final round
      
    if network.getMessageofType('finalCorrectAns', False): #try to get a message of type finalCorrectAns with a non-blocking call
      drawCentreText('Correct') #if successful in getting a message from the buffer update the display with the fact that the last question was correctly answered
      responseWait = False #no longer waiting for a response as a response has just been received
    
    if network.getMessageofType('finalIncorrectAns', False): #try to get a message of type finalIncorrectAns with a non-blocking call
      drawCentreText('Incorrect') #if successful in getting a message from the buffer update the display with the fact that the last question was incorrectly answered
      responseWait = False #no longer waiting for a response as a response has just been received
      
    if network.messageInBuffer('askFinalQuestion'): #check if a message of type askFinalQuestion exists in the message buffer
      rQuestion, contestant, question, answer = network.getMessageofType('askFinalQuestion', False) #if a message exists save the round question number, contestant, question and answer to local variables
      if head2head: #if it is the head2head round
        drawHead2Head(rQuestion - config['questions']['finalRndQCnt'], contestantList) #draw the name and scores of the contestants in the head2head round
      else: #if it is not the head2head round and is just the normal final round
        drawFinalQuestion(rQuestion, question, contestantList) #draw the round round question number, question and contestant names/scores onto the display
      responseWait = True #wait for a response to the question
      
    if network.getMessageofType('headStart', False): #try to get a message of type headStart with a non-blocking call
      head2head = True #if successful in getting a message from the buffer -> set the head2head bool to true
      drawHead2HeadStart() #draw the start of the head2head round onto the screen
    
    if network.messageInBuffer('winner'): #check if a message of type winner exists in the message buffer
      [winner] = network.getMessageofType('winner', False) #if a message exists get the message with a non-blocking call and save the contestant class of the winner to a local variable
      displayWinner(winner.name) #display the name of winning contestant
    
    pygame.display.update() #update the display
    fpsClock.tick(FPS) #limit the number of display updates per second to the value specified

def start(): #attempt to connect to the server and setup the pygame GUI if the connection is successful
  global address, socket, startFrame, mainTopLevel
  if network.attemptConnect(socket, address.get(), config['server']['bindPort']): #attempt to connect to the server
    mainTopLevel.withdraw() #hide the tkinter gui
    network.addUsedType('gameStart') #only receive messages of type "gameStart"
    initPygame() #initiate the pygame GUI
    drawStartWait() #draw the display to be used whilst waiting for the game to start
    isServerRunning() #check if the server is ready to start
  else: #if the connection was unsuccessful
    messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"") #display a message to this effect
    
#draw the display to be used whilst waiting for the game to start
def drawStartWait():
  displaySurface.fill(blue) #fill the display surface with the colour blue
  titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (160 / 11))) #create a font where the size of the font is relative to the size of the window
  
  text = titleFont.render("The Weakest Link", True, yellow) #create yellow text (with anti-analyzing) and content "The Weakest Link"
  textRect = text.get_rect() #get the coordinates of the four corners of the text
  textRect.center = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / 2)) #move the coordinates to the centre of the screen
  displaySurface.blit(text, textRect) #copy the text onto the screen at the coordinates setup above
  
#check if the server is ready to start
def isServerRunning():
  global mainTopLevel            
  if network.getMessageofType('gameStart', False): #get any messages of type gameStart with a non-blocking call
    network.removeUsedType('gameStart') #remove the gameStart message from the usedTypes list
    network.addUsedType('startGUI') #add the startGUI message to the usedTypes list
    startGUI() #wait for control to start the GUI
  else: #if no messages exists
    pygame.display.update() #update the pygame display
    fpsClock.tick(FPS) #limit the number of updates per second to the value held in FPS
    if mainTopLevel.config()['class'][4] == 'Tk': #if the mainTopLevel is a root Tk() instance use it to call this function again in 100 ms
      mainTopLevel.after(100, isServerRunning)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a toplevel get its root Tk() instance and use it to call this function again in 100 ms
      mainTopLevel.root.after(100, isServerRunning)
    
#wait for control to start the GUI        
def startGUI():
  global mainTopLevel
  if network.getMessageofType('startGUI', False): #get any messages of type startGUI with a non-blocking call
    network.removeUsedType('startGUI') #remove startGUI from the used types list
    network.addUsedType('rndStart') #add the messages we want to receive to the used types list
    network.addUsedType('rndScoreUpdate')
    network.addUsedType('correctAns')
    network.addUsedType('incorrectAns')
    network.addUsedType('contestantUpdate')
    network.addUsedType('askQuestion')
    network.addUsedType('allCorrect')
    network.addUsedType('timeUp')
    network.addUsedType('contestantEliminated')
    network.addUsedType('finalStart')
    network.addUsedType('finalCorrectAns')
    network.addUsedType('finalIncorrectAns')
    network.addUsedType('askFinalQuestion')
    network.addUsedType('headStart')
    network.addUsedType('winner')
    gameLoop() #enter the main game loop
  else: #if no messages exists
    pygame.display.update() #update the pygame display
    fpsClock.tick(FPS) #limit the number of updates per second to the value held in FPS
    if mainTopLevel.config()['class'][4] == 'Tk': #if the mainTopLevel is a root Tk() instance use it to call this function again in 100 ms
      mainTopLevel.after(100, startGUI)
    elif mainTopLevel.config()['class'][4] == 'Toplevel': #if the mainTopLevel is a toplevel get its root Tk() instance and use it to call this function again in 100 ms
      mainTopLevel.root.after(100, startGUI)
    
#Initialize the Tkinter GUI with the given parent
def initTk(parent):
  global address, startFrame, mainTopLevel
  
  mainTopLevel = parent #save the parent as a global variable mainTopLevel
  
  startFrame = ttk.Frame(parent, padding="3 3 3 3") #Create the startFrame for the content of the GUI to be placed in with 3 pixels of space between it and the parent on all 4 sides
  startFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #grid the startFrame in the parents 0th row and 0th column
  startFrame.columnconfigure(0, weight=1) #configure the 0th column of the startFrame to expand at the same rate as the parents width
  startFrame.rowconfigure(0, weight=1) #configure the 0th row of the startFrame to expand at the same rate as the parents height
  
  startMenu = Menu(parent) #create a Menu
  parent['menu'] = startMenu #set the parents Menu as the Menu just creaated
  startFile = Menu(startMenu, tearoff=0) #create another Menu to use as a sub menu
  startTools = Menu(startMenu, tearoff=0)
  startHelp = Menu(startMenu, tearoff=0)
  startMenu.add_cascade(menu=startFile, label='File') #Add the sub menus just created to the main menu
  startMenu.add_cascade(menu=startTools, label='Tools')
  startMenu.add_cascade(menu=startHelp, label='Help')
  
  startFile.add_command(label='Exit', command=close) #Add an exit command to the main menu
  
  startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress()))) #Add a command to the tools menu which creates an info box showing the machines current ip addresses
  
  startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink")) #Add an information box containing information about the application to the help menu
  
  address = StringVar() #create a string variable to contain the address of the server to connect to
  address.set(config['server']['bindAddress'])  #set the default value of the address to the value in the config file
  
  ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N) #add a button the the startFrame which will attempt to connect to the server at the address specified
  ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N) #add a button to close the startFrame
  ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N) #add a text entry to the startFrame with the value bound to the address string variable
  ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N) #add a label to the startFrame identifying the text entry as the ip address of the server
  
  parent.protocol("WM_DELETE_WINDOW", close) #call the close() function when the X at the top right corner of the application window is pressed
  
#Close the Tkinter window cleanly
def close():
  global mainTopLevel, socket
  network.closeSocket(socket) #Close the clientsocket
  if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify() #if the mainTopLevel is a TopLevel and not a root instance show the TopLevels parent
  mainTopLevel.destroy() #destroy the main top level
  pygame.quit() #end the pygame instance
  
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