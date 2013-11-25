import pygame, sys, operator, select, socket, json
from pygame.locals import *

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
        if not font: font = pygame.font.Font('freesansbold.ttf', 24)
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

def draw(round, roundQuestion, question, correctIndex, money, bank):
    displaySurface.fill(blue)
    mainFont = pygame.font.Font('freesansbold.ttf', 40)
    titleFont = pygame.font.Font('freesansbold.ttf', 55)
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

def gameLoop():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.dict['key'] == 27:
                pygame.quit()
                sys.exit()
        readable, writable, err = select.select([clientsocket.fileno()], [], [], 0.1)
        if readable:
            msg = clientsocket.recv(4096)
            #check = self.clientsocket.recv(40).decode('UTF-8')
            #assert(hashlib.sha1(msg).hexdigest() == check)
            variables = json.loads(msg.decode('UTF-8'))
            draw(variables['cntRounds'], variables['cntRquestions'], variables['question'], variables['correct'], variables['money'], variables['bank'])
        pygame.display.update()
        fpsClock.tick(FPS)

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print('Attempting to connect to lcoalhost')
    clientsocket.connect(('localhost',1024))
except:
    print('Failed to connect to localhost')
    pygame.quit()
    sys.exit()

gameLoop()
