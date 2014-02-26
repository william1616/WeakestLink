from tkinter import *
from tkinter import ttk
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

class placeholder():
    def __init__(self, surface, coordinates, text, font=None, textColour=None, active=False):
        self.surface = surface
        self.coordinates = coordinates
        self.active = active
        self.change(text, font, textColour)
    def change(self, text=None, font=None, textColour=None):
        if not textColour: textColour = pygame.Color(0, 0, 0)
        if not font: font = pygame.font.SysFont(config['pygame']['font'], int(self.surface.get_height() / 25))
        if self.active: placeholder = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\redPlaceholder.png'))
        else: placeholder = pygame.image.load(os.path.join(os.path.dirname(__file__), '..\\resources\\bluePlaceholder.png'))
        placeholder = pygame.transform.scale(placeholder, (int(self.surface.get_width() / (160 / 27)), int(self.surface.get_height() / (40 / 3))))
        self.surface.blit(placeholder, self.coordinates)
        if text:
            self.text = font.render(text, True, textColour)
            self.textRect = self.text.get_rect()
            self.textRect.center = tuple(map(operator.add, placeholder.get_rect().center, self.coordinates))
        self.surface.blit(self.text, self.textRect)
    def activate(self):
        self.active = True
        self.change()
    def deactivate(self):
        self.active = False
        self.change()

def wrapText(surface, coordinates, text, font, textColour):
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
        surface.blit(textSurface, (rect.left, y))
        y += fontHeight + lineSpacing
        text = text[i:]

    return text
    
def drawQuestion(round, roundQuestion, question, correctIndex, money, bank):
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / 15))
    titleFont = pygame.font.SysFont(config['pygame']['font'], int(displaySurface.get_height()  / (120 / 11)))
    titleFont.set_underline(True)

    money.remove(0)
    money.reverse()
    moneyPlaceholder = {}

    for value in money:
            moneyPlaceholder[value] = placeholder(displaySurface, ((int(displaySurface.get_width() / 80)), int((displaySurface.get_height()  / 60) + (displaySurface.get_height()  / (120 / 11)) * money.index(value))), '£' + str(value), textColour = white)
    
    money.reverse()

    for i in range(0, correctIndex):
        moneyPlaceholder[money[i]].activate()
            
    bank = placeholder(displaySurface, (int(displaySurface.get_width() / 80), int(displaySurface.get_height()  - (displaySurface.get_height()  / (120 / 13)))), "Bank £" + str(bank), textColour = white, active = True)

    titleText = titleFont.render('Round ' + str(round) + ' Question ' + str(roundQuestion), True, black)
    titleRect = titleText.get_rect()
    titleRect.topleft = (int(displaySurface.get_width() / (120 / 31)), int(displaySurface.get_height()  / 80))
    displaySurface.blit(titleText, titleRect)

    wrapText(displaySurface, (int(displaySurface.get_width() / (120 / 31)), int(titleRect.bottom + (displaySurface.get_height()  / 80)), int(displaySurface.get_width() - (displaySurface.get_width() / (40 /11))), int(displaySurface.get_height()  - (titleRect.height + (displaySurface.get_height()  / 80)))), question, mainFont, black)

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
    contestantList = list(contestants.keys())
    contestantScore = list(contestants.values())
    
    for i in range(0, len(contestants)):
        contestant = mainFont.render(contestantList[i] + ': ' + str(contestantScore[i]), True, black)
        contestantRect = contestant.get_rect()
        if i % 2 == 0:
            contestantRect.midtop = (int(displaySurface.get_width() / 3), y)
        else:
            contestantRect.midtop = (int(2 * displaySurface.get_width() / 3), y)
            y += int(displaySurface.get_height() / 16)
        displaySurface.blit(contestant, contestantRect)
    
def gameLoop():
    global socket
    end = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.dict['key'] == 27:
                close()
                end = True
                break
        if end: break
        variables = network.getMessageofType('variables', [socket], False)
        if variables:
            if variables['correct'] == len(variables['money']) - 1:
                drawCorrect(variables['cntRounds'], variables['contestants'])
            elif variables['time']:
                drawTime(variables['cntRounds'], variables['contestants'])
            else:
                drawQuestion(variables['cntRounds'], variables['cntRquestions'], variables['question'], variables['correct'], variables['money'], variables['bank'])
        pygame.display.update()
        fpsClock.tick(FPS)

def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        isServerRunning()

            
def isServerRunning():
    global mainTopLevel, socket
    
    variables = network.getMessageofType('variables', [socket], False)
    if variables and variables['gamemode'] != -1: #if no longer listing for conections
        mainTopLevel.withdraw()
        initPygame()
        gameLoop()
    else:
        #run the function every time the system is idle
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

def setup():
    global socket, config
    socket = network.initClientSocket()
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')

if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    root.mainloop()
