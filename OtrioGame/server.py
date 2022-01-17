
import socket
import sys
import threading
import queue
import threading
import time
import pickle

def listenerThread(gQueue,  lSocket):
  
  while True:
    #try:
    lSocket.listen(6)
    connection, address = lSocket.accept()
    message = connection.recv(1024)
    message = message.decode('ASCII')
    connection.sendall(b'expecting Data')
    print("mesage =", message, "from", address)
    message = message.split(' ')
    length = 0
    rMessage = b''
    if(message[0] == 'sending'):
      length = int(message[1])
    else:
      print('invalid message: ' + str(message))
    while (len(rMessage) < length):
      rMessage += connection.recv(1024)
    rMessage = rMessage.decode('ASCII')
    gQueue.put(rMessage)
    connection.close()
      
      
    #except Exception as e:
      #print('failed to recive message in listenerThread : ' + str(e))

def send(message,address):
  csocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  csocket.bind(('localhost',0))
  csocket.settimeout(5)
  print("sending", message, "to", address)
  try:
  
    csocket.connect(address)
    length = str(len(message.encode()))
    csocket.sendall(('sending '+length).encode())
    confrimation = csocket.recv(1024)
    
    csocket.sendall(message.encode())
  except Exception as e:
    print('Failure to send message: ' + message + '\n Error code: ' + str(e))
  csocket.close()


def makeGameBoard():
  x = []
  y = []
  z = []
  for a in range (0,3):        
    for b in range(0,3):
      for c in range(0,3):
        z.append('n')
      y.append(z)
      z = []
    x.append(y)
    y = []
  return x


def checkForWin(board,players):
  for p in players:
    if(seeIfPlayerHasWon(board,p[0])):
      print(str(p[0]) + ' has Won') 
      return p[0]
  return 'null' 
def seeIfPlayerHasWon(board, player):
      

    #the next 3 loop sets are for the straight across wins left to right, top to bottem and the other top to bottem...
    #this takes care of 27 possible wins

    #takes care of 9 possible wins
    for x in range(0,3):
      for y in range(0,3):
        if(board[x][y][0] == player and board[x][y][1] == player and board[x][y][2] == player):
          return True
    #takes care of 9 possible wins 
    for z in range(0,3):
      for y in range(0,3):
        if(board[0][y][z] == player and board[1][y][z] == player and board[2][y][z] == player):
          return True 
    #takes care of 9 possible wins
    for x in range(0,3):
      for z in range(0,3):
        if(board[x][0][z] == player and board[x][1][z] == player and board[x][2][z] == player):
          return True 

    #all of the across wins should be here and the up and down ones now we need the diagonal ones 

    #the next four loops are for the diaganols and each take up 3 possible wins apice totaling to 12 of the wins
    for x in range(0,3):
      if(board[x][0][0]== player  and board[x][1][1]== player  and board[x][2][2]== player ):
        return True
    for x in range(0,3):
      if(board[x][0][2]== player  and board[x][1][1]== player  and board[x][2][0]== player ):
        return True
    
    for z in range(0,3):
      if(board[0][0][z]== player  and board[1][1][z]== player  and board[2][2][z]== player ):
        return True
    for z in range(0,3):
      if(board[2][0][z]== player  and board[1][1][z]== player  and board[0][2][z]== player ):
        return True

    #six possible wins accounted for here
    for y in range(0,3):
      if(board[0][y][0]== player  and board[1][y][1]== player  and board[2][y][2]== player ):
        return True
      if(board[2][y][0]== player  and board[1][y][1]== player  and board[0][y][2]== player ):
        return True
   #the last four wins are the corner to oppisite corner wins which i'm not sure if you can make a loop for or not.
   #these need to be tested all of them just to be sure.
    if(board[0][0][0] == player and board[1][1][1] == player and board[2][2][2]== player):
      return True
    
    if(board[0][2][0]== player and board[1][1][1]== player and board[2][0][2]== player):
      return True

    if(board[0][0][2]== player and board[1][1][1]== player and board[2][2][0]== player):
      return True
   
    if(board[0][2][2]== player and board[1][1][1]== player and board[2][0][0]== player):
      return True
    

    
def playTurn(board,x,y,z,player):
    if(board[x][y][z] == 'n'):
      board[x][y][z] = player
      return True
    return False


#I have not tested this yet i'm not sure if pickle give a binary string or not
def update_player(address,game,turnNum):
  #I need to make this more efficent... 
  moves = ''
  for x in range(0,3):
    for y in range(0,3):
      for z in range(0,3): 
        moves += game[x][y][z] + '-'
      
  
  
  send('updatePlayer ' + moves[:-1]+' ' +str(turnNum),address)


def sendMove(address,name,move):
  send('sendMove '+ name+ ' ' + move,address) 

def sendChat(to_address,chat,theLog):
  firstSpace = chat.find(' ')
  chat = chat[firstSpace:]
  firstSpace = chat.find(' ')
  chat = chat[firstSpace:]
  theLog += " " +chat
  send('sendChat ' + chat,to_address) 


def updateAllPlayers(players,message):

  for p in players:
    send(message,p[1])

#start of gameThread
def gameThread(gameName,gQueue):
  
  
  chatLog = 'Start of Chat:'
  numPlayers = 0
  players = []
  #players Tuple = (name , address, isAlive,connection)
  playerAddresses = []
  gameStarted = False
  turn = 0
  timer = 0
  gQ = gQueue
  gSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  gSocket.bind(('',0))
  game = makeGameBoard()
  listener = threading.Thread(target =listenerThread, args =(gQ,gSocket))
  listener.setDaemon(True)
  listener.start()
  turnNumber = 0
  


  #five should be the max but just to be safe i'm giving an extra for a little leeway
  
  ###########################################################################
  #inside here is where the we should be dealing with all of the various comands from the
  #clients in a game
  while True :
    while True:
      if not gQ.empty():
        break
      else:
        
        timer = timer
        time.sleep(1)
        if(turnNumber >=27):
          message = ' n n n n n n'
          break
        if(gameStarted):
          if(len(players) > turn):
            if(not players[turn][2]):
              timer = 61
              break
        if(timer >= 60 and gameStarted):
          timer = 0
          players[turn] = (players[0],players[1],False,players[3])
          break
    message = gQ.get()
    address = ''
    if(type(message) == tuple):
      #print(message)
      address = message[0]
      uMessage= message[1]
      message = message[1]
      message = message.split(' ')
      print(address)
      print(address[1])
      
      addresss = (address[0],int(message[len(message)-1]))
      print('the new address' +str(address)) 
      
      exists = False
      
      for p in players:
        if p[0] == message[0]:
          
          p = (p[0],address,True,p[3])
          exisits = True
          send('gameSocket '+str(gSocket.getsockname()[1]),address)
      if not exists and numPlayers < 4:
        numPlayers += 1
        players.append((message[0],address,True,connection))
        send('gameSocket '+str(gSocket.getsockname()[1]) ,address)
    else:  
      uMessage = message
      message = message.split(' ')
    print('the message: ' + str(uMessage))
    print('the Command recive: ' + message[1])
    
    #start game 
    
    #Format: name requestType
    if ((message[1] == 'startGame' or len(players) == 4) and  (not gameStarted)):
      gameStarted = True
      timer = 0
      for i in range(0, len(players)):
        if(players[i][2]):
          send('startGame',players[i][1])
    #Format: name requestType
    elif(message[1] == 'joinGame'):
       print("has joined the game: " + message[0])
       playersToPrint = ''
       for p in players:
         playersToPrint += " " + p[0]
       print(playersToPrint) 
      
    #formated as
    #message = [name,command,x-y-z,colour] <i'm not sure on the spelling of colour here...
    #Format: name requestType x-y-z
    elif(message[1] == 'submitMove' and gameStarted):
      timer = 0
      for p in players:
        if(p[0] == message[0]):
          if(players.index(p) == turn):
            
            theMove = message[2].split('-')
            validMove = playTurn(game,int(theMove[0]),int(theMove[1]),int(theMove[2]),message[0])
            turnNumber+= 1
            winner = checkForWin(game,players)
            turn =  (turn + 1) % 4
            for i in range(0, len(players)):
              if(players[i][2]):
                sendMove(players[i][1],message[0],message[2]+' ' +str(turn))
              if(winner != 'null' and players[i][3]):
                send('winner ' + winner,players[i][1])
             
            if(winner != 'null'):
              sys.exit()
          else:
            print('Invalid move attempt: ' + uMessage)
            #invalid move attempted
          #where I'm levaing of for the moment
          #game.play
    #Format: name requestType
    elif(message[1] == 'leaveGame'):
      for p in players:
        if(p[0] == message[0]):
          
          p = (p[0],p[1],False,p[3])
       
       
    #Format: name requestType   
    elif(message[1] == 'getBoard'):
      for p in players:
        if p[0] == message[0]:
          update_player(p[1],game,turn)   
    #Format: name reqestType
    elif(message[1] == 'SubmitText'):
      for p in players:
        sendChat(p[1],uMessage,chatLog) ###############################################
    #Format: name requestType
    elif(message[1] == 'getPlayers'):
      playersNames = ''
      for p in players:
        playersNames += p[0] + "-"
      for p in players:
        if p[0] == message[0]:
          send('playerNames '+ playersNames[:-1],p[1])
    #random turn being played due to timeout
    elif(timer > 59):
      timer = 0
      turnPlayed = False
      turnNumber+= 1
      for a in range (0,3):        
        for b in range(0,3):
          for c in range(0,3):
            if(not turnPlayed and game[a][b][c] == 'n'):
              game[a][b][c] = player[turn][0]
              turnPlayed = True
              a = 3
              b = 3
              c = 3
      activePlayer = 0
      for p in players:
        if(p[3] == True):
          activePlayers += 1
        if(activePlayers == 0):
          sys.exit()
      turn =  (turn + 1) % 4
      winner = checkForWin(board,players)
      for i in range(0, len(players)):
              if(players[i][2] and players[3]):
                
                sendMove(player[i][1],message[0]+' ' +str(turn),message[2])
                if(winner != 'null'):
                  send('winner ' + winner,players[i][1])
    elif( turnNumber >= 27):
      winner = checkForWin(board,players)
      if(winner != 'null'):
        for i in range(0, len(players)):
          if(players[i][2] and players[3]):
           
             if(winner != 'null'):
               send('winner ' + winner,players[i][1])
      else:
        if(winner == 'null'):
          for i in range(0, len(players)):
            if(players[i][2] and players[3]):
              send('winner ' + 'Draw',players[i][1])
    
    else:
      print('Invalid Message recive by game thread: ' + uMessage)
      print('the list is: ' + str(message))
    
    
         
  
#end of gameThread #############################################################3



#start of getGames
def getGames(games):
  gamesList = ''
  isOpen = 0
  for g in games:
    if(g[4] == 'null'):
      isOpen = 0
    else:
      isOpen = 1
    gamesList = gamesList + g[0] + '-' +  str(g[1])+"-" + str(isOpen)+ ' '
  
  return gamesList
#end of getGames

#address of the main server
    
    

def serverConnectionThread(connection,client_address,games):
    leaveLoop = False
    while True:
      
      
      
      #we need to look into the exact size we need to have here I doubt its more than 64 mb so it might be a good idea to shorten alot
      message = connection.recv(1024)
      message = message.decode('ASCII')
      #connection.close()
      print('\ncommand recived: ' + message)
      #the sleep was used for testing and should only be uncomented to test things...
      #time.sleep(5)

      #If one of the users disconnects from the lobby before the game starts
      if(message == ''):
        print("Connection to player " + str(client_address) + " lost")
        for g in games :
          if g[0] == message[2]:
            g[3].put(message[0]+' leaveGame')
            index = games.index(g)
            games[index] = (g[0],g[1]-1,g[2],g[3],g[4])
            if games[index][1] <= 0:
              games.pop(index)
        connection.close()  
        sys.exit()
    
      #the format i'm gonna go with is name requestType extra extra
      #note that the extra part might vary from request to request some its simply other
      #stuff that might be needed for each comand check below if you are'nt sure
      #ex for a new game request: tim newGame theGameName 
      unsplitMessage = message
      message = message.split(' ')
    
      #this next part determines what to do with a recived connection

      #this should make a new game and then put the person requsting the new game in a
      
      if(len(message) < 2):
        connection.sendall(b'Invalid Message')
      #format: name requestType gameName password address
      if message[1] == 'newGame':
        #game name in use
        gameFound = False
        for g in games:
          if(g[0] == message[2]):
            gameFound = True
            connection.sendall(b'bad')
          
        #game name not in use it should be able to be made.
        if not gameFound:
          connection.sendall(b'good')
          client_address = (client_address[0],int(message[len(message) - 1] ))
          gameQueue = queue.Queue()
          newGameThread = threading.Thread(target =gameThread, args =(message[2],gameQueue))
          newGameThread.setDaemon(True)
          newGameThread.start()
          games.append((message[2],1,newGameThread,gameQueue,message[3]))
          gameQueue.put((client_address,message[0] + ' joinGame ' + message[len(message)-1]))
          
          leaveLoop = True
          #i'm thinking of using a queue for general comunication since they are supossedly thread safe
          #they should help keep an order to our conamnds sent to a game and prevent any lose
          #of data due to threading.                                
          #gameQueue.push(client_address)
          
      elif message[1] == 'leaveGame' :
        for g in games :
          if g[0] == message[2]:
            g[3].put(message[0]+' leaveGame')
            index = games.index(g)
            games[index] = (g[0],g[1]-1,g[2],g[3],g[4])
            if games[index][1] <= 0:
              games.pop(index)
        
      #join a game
      #format: name requestType gameName password address                                 
      elif message[1] == 'joinGame' :
        gameJoined = False
      #format: name requestType 
      
        for g in games :
          if(message[2] == g[0]):
            if((message[3] == g[4] or g[4] == 'null') and g[1] < 4):
              index = games.index(g)
              games[index] = (g[0],g[1]+1,g[2],g[3],g[4])
              client_address = (client_address[0],int(message[len(message) - 1] ))
              g[3].put((client_address,unsplitMessage))
              gameJoined = True 
              connection.sendall(b'good')
              leaveLoop = True
              
              break
            else:
              connection.sendall(b'bad')
        if message[2] == 'random':
          print('joining Random: '+ message[0])
          #for loop to find the avalible game to join
          for g in games :
            if(g[1] < 4 and g[4] == 'null'):
               g[3].put((client_address,unsplitMessage))
               gameJoined = True
               break
              
        
        
        if not gameJoined:
          print('join failue with: ' + unsplitMessage)
          connection.sendall(b'error')
          leaveLoop = False
        
      #A way to rejoin a game should go here
      #Note that i've done nothing to account for this anywhere yet so it all needs to be done
      #format: name requestType gameName
      #elif message[1] == 'rejoin':
        
        
      #this should send to the client a list of all of the games and the number of players in those games
      #each one seperated by a comma ex game1 3, game2 2,
      ##format: name requestType
      elif message[1] == 'gameList':
        print('printing games')
        gl = getGames(games)
        print(gl)
        connection.sendall(('gameList '+gl).encode())
        
      else:
        print('Invalid Message recive by main thread: ' + unsplitMessage)
        connection.sendall(b'unknown comand')
      
      if(leaveLoop):
        connection.close()
        break

#start of main server stuff
sAddress = ('localhost', 33222)
    
Ssocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
Ssocket.bind(sAddress)
serverThreads = []
games = []
#games.append(('gameName',1,gameThread,gameQueue,password))
 

Ssocket.listen(10)
print('Main server listening on listening on: ' ,sAddress)
#getGames(games)

#I think we need to get rid of the while true here
#not a big deal either way but i don't have the time to adjust the tabs atm so its gonna stay.
try:
  while True:
    print('i am here')
    connection , client_address = Ssocket.accept()
    leaveLoop = False
    for g in games:
      if g[1] ==4:
        games.pop(games.index(g))
    print('\nconnected to: ' + str(client_address))
    #i'm just gonna hope games does'nt get messed up...
    serverConnectionHandler = threading.Thread(target =serverConnectionThread, args =(connection,client_address,games))
    serverConnectionHandler.setDaemon(True)
    serverConnectionHandler.start() 
    serverThreads.append(serverConnectionHandler)      
except KeyboardInterrupt as e:
  print('closeing due to keyboard interupt' + str(e))
  
  Ssocket.close()
  
  sys.exit()


