from tkinter import *
from tkinter import ttk
import pygame, sys, operator, network, misc, threading
from pygame.locals import *

def initPygame():
    global displaySurface, FPS, fpsClock, width, height, white, blue, black
    pygame.init()

    FPS = 10
    fpsClock = pygame.time.Clock()

    width = 800
    height = 600

    displaySurface = pygame.display.set_mode((width, height), 0)
    pygame.display.set_caption("The Weakest Link")

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
        if not font: font = pygame.font.SysFont('microsoftsansserif', 24)
        if self.active: placeholder = pygame.image.load('redPlaceholder.png')
        else: placeholder = pygame.image.load('bluePlaceholder.png')
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
    mainFont = pygame.font.SysFont('microsoftsansserif', 40)
    titleFont = pygame.font.SysFont('microsoftsansserif', 55)
    titleFont.set_underline(True)

    money.remove(0)
    money.reverse()
    moneyPlaceholder = {}

    for value in money:
            moneyPlaceholder[value] = placeholder(displaySurface, (10, 10 + 55 * money.index(value)), '£' + str(value), textColour = white)
    
    money.reverse()

    for i in range(0, correctIndex):
        moneyPlaceholder[money[i]].activate()
            
    bank = placeholder(displaySurface, (10, height - 65), "Bank £" + str(bank), textColour = white, active = True)

    titleText = titleFont.render('Round ' + str(round) + ' Question ' + str(roundQuestion), True, black)
    titleRect = titleText.get_rect()
    titleRect.topleft = (155, 10)
    displaySurface.blit(titleText, titleRect)

    wrapText(displaySurface, (155, titleRect.bottom + 10, width - 165, height - (titleRect.height + 10)), question, mainFont, black)

def drawTime(round, contestants):
    drawEnd(round, contestants, 'Time Up')

def drawCorrect(round, contestants):
    drawEnd(round, contestants, 'You got all the Questions Correct')

def drawEnd(round, contestants, line1):
    displaySurface.fill(blue)
    mainFont = pygame.font.SysFont('microsoftsansserif', 40)
    titleFont = pygame.font.SysFont('microsoftsansserif', 55)
    titleFont.set_underline(True)
    subTitleFont = pygame.font.SysFont('microsoftsansserif', 55)
    
    timeUp = titleFont.render(line1, True, black)
    timeUpRect = timeUp.get_rect()
    timeUpRect.midtop = (displaySurface.get_width() / 2, 10)
    displaySurface.blit(timeUp, timeUpRect)
    
    endofRound = subTitleFont.render('End of Round ' + str(round), True, black)
    endofRoundRect = endofRound.get_rect()
    endofRoundRect.midtop = (displaySurface.get_width() / 2, 70)
    displaySurface.blit(endofRound, endofRoundRect)
    
    weakestLink = mainFont.render('You must now choose the weakest link', True, black)
    weakestLinkRect = weakestLink.get_rect()
    weakestLinkRect.midtop = (displaySurface.get_width() / 2, 180)
    displaySurface.blit(weakestLink, weakestLinkRect)
    
    y = 270
    contestantList = list(contestants.keys())
    contestantScore = list(contestants.values())
    
    for i in range(0, len(contestants)):
        contestant = mainFont.render(contestantList[i] + ': ' + str(contestantScore[i]), True, black)
        contestantRect = contestant.get_rect()
        if i % 2 == 0:
            contestantRect.midtop = (displaySurface.get_width() / 3, y)
        else:
            contestantRect.midtop = (2 * displaySurface.get_width() / 3, y)
            y += 50
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
    if network.attemptConnect(socket, address.get(), 1024):
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
            mainTopLevel.after_idle(isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after_idle(isServerRunning)
        
def initTk(parent):
    global address, startFrame, waitFrame, mainTopLevel
    
    mainTopLevel = parent
    
    startFrame = ttk.Frame(parent, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)
    
    address = StringVar()
    address.set('localhost')
    
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
