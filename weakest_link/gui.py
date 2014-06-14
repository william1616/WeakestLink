from tkinter import *
from tkinter import ttk, messagebox
import pygame, sys, operator, os.path
from pygame.locals import *

path = os.path.dirname(__file__)
try:
    import network, misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("network", os.path.join(path, "network.py"))
    network = loader.load_module("network")
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

def initPygame():
    global displaySurface, FPS, fpsClock, white, blue, black
    pygame.init()

    FPS = config['pygame']['fps']
    fpsClock = pygame.time.Clock()

    width = config['pygame']['width']
    height = config['pygame']['height']

    displaySurface = pygame.display.set_mode((width, height), 0)
    pygame.display.set_caption(config['pygame']['window_title'])

    white = pygame.Color(255, 255, 255)
    blue = pygame.Color(0, 100, 255)
    black = pygame.Color(0, 0, 0)

class moneyPlaceholder():
    def __init__(self, surface, coordinates, text, font=None, textColour=None, active=False):
        self.surface = surface
        self.coordinates = coordinates
        self.active = active
        self.change(text, font, textColour)
    def change(self, text=None, font=None, textColour=None):
        if not textColour: textColour = pygame.Color(0, 0, 0)
        if not font: font = pygame.font.SysFont(config['pygame']['font'], int(self.surface.get_height() / 25))
        if self.active: moneyImage = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\redPlaceholder.png'))
        else: moneyImage = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\bluePlaceholder.png'))
        moneyImage = pygame.transform.scale(moneyImage, (int(self.surface.get_width() / (160 / 27)), int(self.surface.get_height() / (40 / 3))))
        self.surface.blit(moneyImage, self.coordinates)
        if text:
            self.text = font.render(text, True, textColour)
            self.textRect = self.text.get_rect()
            self.textRect.center = tuple(map(operator.add, moneyImage.get_rect().center, self.coordinates))
        self.surface.blit(self.text, self.textRect)
    def activate(self):
        self.active = True
        self.change()
    def deactivate(self):
        self.active = False
        self.change()
        
class awnserPlaceholder():
    def __init__(self, surface, coordinates, font=None, textColour=None):
        self.surface = surface
        self.coordinates = coordinates
        self.change(None, font, textColour)
    def change(self, state=None, font=None, textColour=None):
        #state none=blue no symbol true=blue and tick false=red and cross
        if not textColour: textColour = pygame.Color(0, 0, 0)
        if not font: font = pygame.font.SysFont(config['pygame']['font'], int(self.surface.get_height() / 25))
        if state == False: awnserImage = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\incorrectRed.png'))
        elif state == True: awnserImage = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\correctBlue.png'))
        else: awnserImage = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\neutralBlue.png'))
        awnserImage = pygame.transform.scale(awnserImage, (int(self.surface.get_width() / 10), int(self.surface.get_height() / (40 / 3))))
        self.surface.blit(awnserImage, self.coordinates)
    def correct(self):
        self.change(True)
    def incorrect(self):
        self.change(False)

def wrapText(surface, coordinates, text, font, textColour, center=False):
    rect = pygame.Rect(coordinates)
    y = rect.top
    lineSpacing = 0
    fontHeight = font.get_height()

    while text:
        i = 1

        if y + fontHeight > rect.bottom:
            break
        
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
        
        if i < len(text):
            i = text.rfind(' ', 0, i) + 1
        
        textSurface = font.render(text[:i], True, textColour)
        if center:
            surface.blit(textSurface, (rect.centerx - (textSurface.get_width() / 2), y))
        else:
            surface.blit(textSurface, (rect.left, y))
        y += fontHeight + lineSpacing
        text = text[i:]
    
def drawQuestion(round, roundQuestion, question):
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15))
    titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (120 / 11)))
    titleFont.set_underline(True)
    

    titleText = titleFont.render('Round ' + str(round) + ' Question ' + str(roundQuestion), True, black)
    titleRect = titleText.get_rect()
    titleRect.topleft = (int(displaySurface.get_width() / (120 / 31)), int(displaySurface.get_height()  / 80))
    displaySurface.blit(titleText, titleRect)

    wrapText(displaySurface, (int(displaySurface.get_width() / (120 / 31)), int(titleRect.bottom + (displaySurface.get_height()  / 80)), int(displaySurface.get_width() - (displaySurface.get_width() / (40 /11))), int(displaySurface.get_height()  - (titleRect.height + (displaySurface.get_height()  / 80)))), question, mainFont, black)
    
def updateRndScores(correctIndex, money, bank):
    if 0 in money: money.remove(0)
    money.reverse()
    moneyPlaceholderList = {}

    for value in money:
        moneyPlaceholderList[value] = moneyPlaceholder(displaySurface, ((int(displaySurface.get_width() / 80)), int((displaySurface.get_height()  / 60) + (displaySurface.get_height()  / (120 / 11)) * money.index(value))), '£' + str(value), textColour = white)
    
    money.reverse()

    for i in range(0, correctIndex):
        moneyPlaceholderList[money[i]].activate()
            
    bank = moneyPlaceholder(displaySurface, (int(displaySurface.get_width() / 80), int(displaySurface.get_height()  - (displaySurface.get_height()  / (120 / 13)))), "Bank £" + str(bank), textColour = white, active = True)

def drawFinalQuestion(questionCnt, question, contestants):
    #lastResult true=correct false=incorrect
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15))
    titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (120 / 11)))
    titleFont.set_underline(True)
    
    titleText = titleFont.render('Final Round Question ' + str(questionCnt), True, black)
    titleRect = titleText.get_rect()
    titleRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height()  / 80))
    displaySurface.blit(titleText, titleRect)
    
    wrapText(displaySurface, (int(displaySurface.get_width() / 80), int(titleRect.bottom + (displaySurface.get_height()  / 80)), int(displaySurface.get_width() - (displaySurface.get_width() / 80)), int(displaySurface.get_height()  - (titleRect.height + (displaySurface.get_height()) * 3 / 7))), question, mainFont, black)
    
    mainText = mainFont.render(contestants[0].name + ':', True, black)
    mainRect = mainText.get_rect()
    mainRect.topright = (int(displaySurface.get_width() * 2 / 9), int((displaySurface.get_height() - titleRect.height) * 5 / 7))
    displaySurface.blit(mainText, mainRect)
    
    mainText = mainFont.render(contestants[1].name + ':', True, black)
    mainRect = mainText.get_rect()
    mainRect.topright = (int(displaySurface.get_width() * 2 / 9), int((displaySurface.get_height() - titleRect.height) * 6 / 7))
    displaySurface.blit(mainText, mainRect)
    
    awnserPlaceholder1 = {}
    awnserPlaceholder2 = {}
    
    for i in range(2, 7):
        awnserPlaceholder1[i] = awnserPlaceholder(displaySurface, (int(displaySurface.get_width() * ((i) / 7)), int((displaySurface.get_height() - titleRect.height) * 5 / 7)))
        if contestants[0].finalScore[i - 2] == True:
            awnserPlaceholder1[i].correct()
        elif contestants[0].finalScore[i - 2] == False:
            awnserPlaceholder1[i].incorrect()
        awnserPlaceholder2[i] = awnserPlaceholder(displaySurface, (int(displaySurface.get_width() * ((i) / 7)), int((displaySurface.get_height() - titleRect.height) * 6 / 7)))
        if contestants[1].finalScore[i - 2] == True:
            awnserPlaceholder2[i].correct()
        elif contestants[1].finalScore[i - 2] == False:
            awnserPlaceholder2[i].incorrect()
            
def drawHead2Head(questionCnt, contestants):
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15))
    titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (160 / 11)))
    titleFont.set_underline(True)
    subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11)))
    
    titleText = titleFont.render('Head To Head Round', True, black)
    titleRect = titleText.get_rect()
    titleRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height()  / 80))
    displaySurface.blit(titleText, titleRect)
    
    subText = subTitleFont.render('Question ' + str(questionCnt), True, black)
    subTextRect = subText.get_rect()
    subTextRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (80 / 7)))
    displaySurface.blit(subText, subTextRect)
    
    mainText = mainFont.render(contestants[0].name + ' : ' + str(contestants[0].score), True, black)
    mainRect = mainText.get_rect()
    mainRect.midtop = (int(displaySurface.get_width() / 2), int((displaySurface.get_height() - titleRect.height) * 4 / 7))
    displaySurface.blit(mainText, mainRect)
    
    mainText = mainFont.render(contestants[1].name + ' : ' + str(contestants[1].score), True, black)
    mainRect = mainText.get_rect()
    mainRect.midtop = (int(displaySurface.get_width() / 2), int((displaySurface.get_height() - titleRect.height) * 5 / 7))
    displaySurface.blit(mainText, mainRect)
    
def drawTime(round, contestants):
    drawEnd(round, contestants, 'Time Up')

def drawCorrect(round, contestants):
    drawEnd(round, contestants, 'You got all the Questions Correct')

def drawEnd(round, contestants, line1):
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 20))
    titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (160 / 11)))
    titleFont.set_underline(True)
    subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11)))
    
    timeUp = titleFont.render(line1, True, black)
    timeUpRect = timeUp.get_rect()
    timeUpRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / 80))
    displaySurface.blit(timeUp, timeUpRect)
    
    endofRound = subTitleFont.render('End of Round ' + str(round), True, black)
    endofRoundRect = endofRound.get_rect()
    endofRoundRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (80 / 7)))
    displaySurface.blit(endofRound, endofRoundRect)
    
    weakestLink = mainFont.render('You must now choose the weakest link', True, black)
    weakestLinkRect = weakestLink.get_rect()
    weakestLinkRect.midtop = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() / (40 / 9)))
    displaySurface.blit(weakestLink, weakestLinkRect)
    
    y = int(displaySurface.get_height() / (80 / 27))
    
    for i in range(0, len(contestants)):
        contestant = mainFont.render(contestants[i].name + ': ' + str(contestants[i].score), True, black)
        contestantRect = contestant.get_rect()
        if i % 2 == 0:
            contestantRect.midtop = (int(displaySurface.get_width() / 3), y)
        else:
            contestantRect.midtop = (int(2 * displaySurface.get_width() / 3), y)
            y += int(displaySurface.get_height() / 16)
        displaySurface.blit(contestant, contestantRect)
    
def drawRoundStart(round):
    drawStart("Round " + str(round) + " Starting")
    
def drawFinalStart(contestants):
    drawStart("Final Round Starting", contestants[0].name + " vs " + contestants[1].name)
    
def drawHead2HeadStart():
    drawStart("Going to Head to Head Round")
    
def drawStart(text1, text2=None):
    displaySurface.fill(blue)
    subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11)))
    
    text1 = subTitleFont.render(text1, True, black)
    textRect1 = text1.get_rect()
    textRect1.center = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() * 1 / 3))
    displaySurface.blit(text1, textRect1)
    
    if text2:
        text2 = subTitleFont.render(text2, True, black)
        textRect2 = text2.get_rect()
        textRect2.center = (int(displaySurface.get_width() / 2), int(displaySurface.get_height() * 2 / 3))
        displaySurface.blit(text2, textRect2)
        
def displayWinner(winner):
    drawCentreText(winner + ' is the Winner!')
    
def displayEliminated(contestantName):
    drawCentreText(contestantName + ' you are the Weakest Link Goodbye!')
    
def drawCentreText(text):
    displaySurface.fill(blue)
    subTitleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height() / (160 / 11)))    
    wrapText(displaySurface, (int(displaySurface.get_width() / 80), int(displaySurface.get_height() / 3), int(displaySurface.get_width() - (displaySurface.get_width() / 80)), int(displaySurface.get_height() - (displaySurface.get_height() / 80))), text, subTitleFont, black, True)

def gameLoop():
    global socket
    end = head2head = responseWait = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.dict['key'] == 27:
                close()
                end = True
                break
        if end: break
        
        if network.messageInBuffer('rndStart'):
            [round] = network.getMessageofType('rndStart', False)
            drawRoundStart(round)
            
        if network.messageInBuffer('rndScoreUpdate'):
            moneyCount, money, bankVal = network.getMessageofType('rndScoreUpdate', False)
            if responseWait: updateRndScores(moneyCount, money, bankVal)
            
        if network.messageInBuffer('correctAns'):
            responseWait = False
        
        if network.messageInBuffer('incorrectAns'):
            responseWait = False
            
        if network.messageInBuffer('contestantUpdate'):
            contestantList = network.getMessageofType('contestantUpdate', False)
            
        if network.messageInBuffer('askQuestion'):
            rQuestion, contestant, question, awnser = network.getMessageofType('askQuestion', False)
            drawQuestion(round, rQuestion, question)
            updateRndScores(moneyCount, money, bankVal)
            responseWait = True
            
        if network.getMessageofType('allCorrect', False):
            drawCorrect(round, contestantList)
            responseWait = False
            
        if network.getMessageofType('timeUp', False):
            drawTime(round, contestantList)
            responseWait = False
            
        if network.messageInBuffer('contestantEliminated'):
            [contestantClass] = network.getMessageofType('contestantEliminated', False)
            displayEliminated(contestantClass.name)
        
        if network.getMessageofType('finalStart', False):
            drawFinalStart(contestantList)
            
        if network.messageInBuffer('finalCorrectAns'):
            responseWait = False
        
        if network.messageInBuffer('finalIncorrectAns'):
            responseWait = False
            
        if network.messageInBuffer('askFinalQuestion'):
            rQuestion, contestant, question, awnser = network.getMessageofType('askFinalQuestion', False)
            if head2head:
                drawHead2Head(rQuestion - config['questions']['finalRndQCnt'], contestantList)
            else:
                drawFinalQuestion(rQuestion, question, contestantList)
            responseWait = True
            
        if network.getMessageofType('headStart', False):
            head2head = True
            drawHead2HeadStart()
        
        if network.messageInBuffer('winner'):
            winner = network.getMessageofType('winner', False)
            displayWinner(winner.name)
        
        pygame.display.update()
        fpsClock.tick(FPS)

def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        network.addUsedType('gameStart')
        isServerRunning()
    else:
        messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"")
            
def isServerRunning():
    global mainTopLevel            
    if network.getMessageofType('gameStart', False): #if no longer listning for conections
        network.addUsedType('rndStart')
        network.addUsedType('rndScoreUpdate')
        network.addUsedType('contestantUpdate')
        network.addUsedType('askQuestion')
        network.addUsedType('allCorrect')
        network.addUsedType('timeUp')
        network.addUsedType('contestantEliminated')
        network.addUsedType('finalStart')
        network.addUsedType('askFinalQuestion')
        network.addUsedType('headStart')
        network.addUsedType('winner')
        network.removeUsedType('gameStart')
        mainTopLevel.withdraw()
        initPygame()
        gameLoop()
    else:
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, isServerRunning)
        
def initTk(parent):
    global address, startFrame, waitFrame, mainTopLevel
    
    mainTopLevel = parent
    
    startFrame = ttk.Frame(parent, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)
    
    startMenu = Menu(parent)
    parent['menu'] = startMenu
    startFile = Menu(startMenu, tearoff=0)
    startTools = Menu(startMenu, tearoff=0)
    startHelp = Menu(startMenu, tearoff=0)
    startMenu.add_cascade(menu=startFile, label='File')
    startMenu.add_cascade(menu=startTools, label='Tools')
    startMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=close)
    
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    address = StringVar()
    address.set(config['server']['bindAddress'])
    
    ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N)
    ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N)
    
    waitFrame = ttk.Frame(parent, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    parent.protocol("WM_DELETE_WINDOW", close)
    
def close():
    global mainTopLevel, socket
    network.closeSocket(socket)
    if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify()
    mainTopLevel.destroy()
    pygame.quit()

def netTypesDeclaration():
    network.addUsedType('variables')
    
def setup():
    global socket, config
    socket = network.initClientSocket()
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')
    netTypesDeclaration()

if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    root.mainloop()
