import os.path

path = os.path.dirname(__file__)

try:
    import misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

config = misc.initConfig()

class contestantClass():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.totalScore = 0
        self.finalScore = [None] * int(config['questions']['finalRndQCnt'] / 2)
        
    def incScore(self, ammount=1):
        self.score += ammount
        self.totalScore += ammount
        
    def correctFinalQu(self, questionNo):
        self.incScore()
        if questionNo <= config['questions']['finalRndQCnt']:
            self.finalScore[floor((questionNo - 1) / 2)] = True
        
    def incorrectFinalQu(self, questionNo):
        if questionNo <= config['questions']['finalRndQCnt']:
            self.finalScore[floor((questionNo - 1) / 2)] = False
        
    def clrScore(self):
        self.score = 0
        
    def finalQuestionsCorrect(self):
        return self.finalScore.count(True)