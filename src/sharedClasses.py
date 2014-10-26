import os.path, misc
from math import floor

#Import the config values from the json file
config = misc.initConfig()

#Containter for all the stats relating to an individual contestant
class contestantClass():
    #contestant name, contestant universally unique identification number
    def __init__(self, name, uuid):
        #setup the initial values for a contestant
        self.name = name
        self.uuid = uuid
        self.score = 0 #Score is 0 as the contestant has not yet awnsered any questions (This is the score for the current round)
        self.totalScore = 0 #Total score is 0 as the contestant has not yet awnsered any questions (This is the total score for the entire game)
        #Final score is list of null values where the number of null values is equal to the number of questions in the final round
        #Get the number of questions from the config file
        #The number of questions in the final round is double the number of questions each contestant will be asked
        self.finalScore = [None] * int(config['questions']['finalRndQCnt'] / 2)
        
    #Increase both the score fot the current round and the score for the entier game by an ammount that defaults to 1
    def incScore(self, ammount=1):
        self.score += ammount
        self.totalScore += ammount
        
    #Incrase the total score and mark the current final question as correct
    def correctFinalQu(self, questionNo):
        self.incScore()
        if questionNo <= config['questions']['finalRndQCnt']: #Check the final round is not currently at the head2head stage
            self.finalScore[floor((questionNo - 1) / 2)] = True #The current question for the contestant is half the current question count for the final round
        
    #Mark the current final question as incorrect
    def incorrectFinalQu(self, questionNo):
        if questionNo <= config['questions']['finalRndQCnt']: #Check the final round is not currently at the head2head stage
            self.finalScore[floor((questionNo - 1) / 2)] = False #The current question for the contestant is half the current question count for the final round
       
    #Reset the mark for the current round
    def clrScore(self):
        self.score = 0
        
    #Count the awnsers in the final round the constant correctly awnsered
    def finalQuestionsCorrect(self):
        return self.finalScore.count(True)
