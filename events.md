#Server Generated Events
| Event Name           | Arg1                    | Arg2                 | Arg3        | Arg4      |
|----------------------|-------------------------|----------------------|-------------|-----------|
| rndStart             | Round Number            |                      |             |           |
| askQuestion          | Round Question Number   | Contestant Name      | Question    | Awnser    |
| nxtQuestion          | Round Question Number   | NxtContestant Name   | NxtQuestion | NxtAwnser |
| contestantUpdate     | List of contestantClass |                      |             |           |
| correctAns           | Awnser                  |                      |             |           |
| incorrectAns         | Awnser                  |                      |             |           |
| rndScoreUpdate       | Rnd Bank Cnt            | List of Money Values | Bank        |           |
| timeUp               |                         |                      |             |           |
| allCorrect           |                         |                      |             |           |
| eliminationWait      |                         |                      |             |           |
| contestantEliminated | ContestantClass         |                      |             |           |
| responseWait         |                         |                      |             |           |
| finalStart           |                         |                      |             |           |
| askFinalQuestion     | Contestant Name         | Question             | Awnser      |           |
| nxtFinalQuestion     | NxtContestant Name      | NxtQuestion          | NxtAwnser   |           |
| finalCorrectAns      | Awnser                  |                      |             |           |
| finalIncorrectAns    | Awnser                  |                      |             |           |
| headStart            |                         |                      |             |           |
| winner               | ContestantClass         |                      |             |           |
| gameStart            |                         |                      |             |           |

#Events the Server Listens For
| Event Name       | Arg1             | Key                                                      |
|------------------|------------------|----------------------------------------------------------|
| quResponse       | response         | response: 1 - Correct; 2 - Incorrect; 3 - Bank; 4 - Time |
| promtMsg         | msg              |                                                          |
| gotoQu           | question         |                                                          |
| removeContestant | contestant index |                                                          |