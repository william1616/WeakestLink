WeakestLink
===========

A interactive version of the popular BBC gameshow.

General Preconceptions
-----
To run this software you require:

-a server program running which imports questions from a csv file and distributes those questions to client

-a client program running which controls the gameflow - correct, incorrect, time up, bank etc

Optionally:

-a GUI program running which displays the game information in a graphical form

You can have multiple clients of the same type connected to a single server. Clients connect to a server using sockets to transfer data you therefore have to specifiy the IP address of the computer the server is running on (all programs can run on the same computer using localhost as the server address). There is a json config file which can be edited with a text editor to customise how the program runs.

File Structure
------
File|Ussage
----|------
main.py|Main menu which allows running of all other programs through a gui
server.py|Server file which runs the gamecode and controls client programs
control.py|Connects to server as a client and controls gameflow
gui.py|Connects to the server as a client and displays the game stats

Releases
---
https://github.com/william1616/WeakestLink/releases
