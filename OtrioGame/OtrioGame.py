import pygame, sys, queue, threading, socket, time
from random import randint
from drawGame import gameBoard

# Prints the given text in the middle of a given rectangle
def text_in_mid(screen, font, text, color, rect):
    temp = font.render(text, True, color)
    screen.blit(temp, (rect.x + (rect.w - temp.get_width())/2, rect.y + (rect.h - temp.get_height())/2))

# Returns the screen for a given size
def set_up_screen(size):
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("3D Tic-Tac-Toe")

    #icon = pygame.image.load("icon.png")
    #pygame.display.set_icon(icon)
    return screen

# Draw a white button with a border and the text in the middle
def draw_btn(screen, font, text, rect):
    pygame.draw.rect(screen, color["box"], rect)
    pygame.draw.rect(screen, color["outline"], rect, 4)
    text_in_mid(screen, font, text, color["outline"], rect)

# Draws the first screen
def draw_first(screen, font, message_rect, namelabel_rect, nameinput_rect, create_rect, join_rect, text, write):
    if write == True:
        text += "_"
    text_in_mid(screen, font, "Welcome to 3D Tic-Tac-Toe", color["outline"], message_rect)
    text_in_mid(screen, font, "Player Name:", color["outline"], namelabel_rect)
    draw_btn(screen, font, text, nameinput_rect)
    draw_btn(screen, font, "Create Lobby", create_rect)
    draw_btn(screen, font, "Join Lobby", join_rect)
    
# Makes the first screen where the user chooses to create or join a game
def first_screen(player_name, cs, command_queue):
    screen = set_up_screen([500, 250])
    message_rect = pygame.Rect((0, 0),(500,75))
    namelabel_rect = pygame.Rect((80, 75),(75,25))
    nameinput_rect = pygame.Rect((200, 70),(250,30))
    create_rect = pygame.Rect((75, 125),(150,100))
    join_rect = pygame.Rect((275, 125),(150,100))
    font = pygame.font.Font(None, 30)
    write = False
    text = ""
    run = 1
    while run == 1:
        screen.fill(color["form"])
        draw_first(screen, font, message_rect, namelabel_rect, nameinput_rect, create_rect, join_rect, text, write)
        for event in pygame.event.get():
        # Exit button trigger
            if event.type == pygame.QUIT:
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                # Click create
                if create_rect.collidepoint(pygame.mouse.get_pos()) and text != "" and text.isspace() == False:
                    run = create_screen(text, cs, command_queue)
                # Click join
                elif join_rect.collidepoint(pygame.mouse.get_pos()) and text != "" and text.isspace() == False:
                    run = join_screen(text, cs, command_queue)
                # If the name input box is selected
                if nameinput_rect.collidepoint(pygame.mouse.get_pos()):
                    write = True
                else:
                    write = False
            elif event.type == pygame.KEYDOWN and write == True:
                if event.key == pygame.K_BACKSPACE:
                    text = str(text[: -1])
                else:
                    current_text = font.render(text, True, color['outline'])
                    if current_text.get_width() < nameinput_rect.w - 20 and event.key != pygame.K_SPACE and event.key != pygame.K_MINUS:
                        text += event.unicode
        pygame.display.update()
    # The run system chanes together function calls till one returns done, in which case the done makes its way back to where where the game starts by going back to the main execution    
    if run == "done":
        return text
    elif run == 0:
        pygame.quit()
        sys.exit(0)

# Draws the create screen
def draw_create(screen, font, namelabel_rect, nameinput_rect, public_rect, private_rect,wordlabel_rect, wordinput_rect, create_rect, back_rect, public, name, name_selected, word, word_selected):
    if name_selected:
        name += '_'
    elif word_selected:
        word += '_'
    text_in_mid(screen, font, "Lobby Name:", color["outline"], namelabel_rect)
    draw_btn(screen, font, name, nameinput_rect)
    # Shows if public or private is selected
    if public:
        pygame.draw.rect(screen, color["selected"], public_rect)
        pygame.draw.rect(screen, color["box"], private_rect)
    else:
        pygame.draw.rect(screen, color["box"], public_rect)
        pygame.draw.rect(screen, color["selected"], private_rect)
    pygame.draw.rect(screen, color["outline"], public_rect, 4)
    text_in_mid(screen, font, "Public", color["outline"], public_rect)
    pygame.draw.rect(screen, color["outline"], private_rect, 4)
    text_in_mid(screen, font, "Private", color["outline"], private_rect)
    text_in_mid(screen, font, "Password:", color["outline"], wordlabel_rect)
    draw_btn(screen, font, word, wordinput_rect)
    draw_btn(screen, font, "Create", create_rect)
    draw_btn(screen, font, "Back", back_rect)

# Makes the create screen, where the user gives the game a name, chooses if it is public or private, and if private, give it a passward
# Both the name and the password can not be blank or only made up of spaces

def create_screen(player_name, cs, command_queue):
    screen = set_up_screen([500, 250])
    namelabel_rect = pygame.Rect((50, 25),(100, 25))
    nameinput_rect = pygame.Rect((175, 20),(250, 30))
    public_rect = pygame.Rect((145, 75),(100, 50))
    private_rect = pygame.Rect((255, 75),(100, 50))
    wordlabel_rect = pygame.Rect((60, 150),(100, 25))
    wordinput_rect = pygame.Rect((175, 145),(250, 30))
    create_rect = pygame.Rect((400, 200),(100, 50))
    back_rect = pygame.Rect((0, 200),(100, 50))
    font = pygame.font.Font(None,30)
    public = True
    name = ''
    word = ''
    name_selected = False
    word_selected = False
    run = 1
    while run == 1:
        # Define if name is being edited or password
        if name_selected == True:
            text = name
        elif word_selected == True:
            text = word
        screen.fill(color["form"])
        draw_create(screen, font, namelabel_rect, nameinput_rect, public_rect, private_rect, wordlabel_rect, wordinput_rect, create_rect, back_rect, public, name, name_selected, word, word_selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                # If the name input box is selected
                if nameinput_rect.collidepoint(pygame.mouse.get_pos()):
                    name_selected = True
                    text = name
                else:
                    name_selected = False
                # If the password input box is selected, only works if private is selected
                if wordinput_rect.collidepoint(pygame.mouse.get_pos()) and public == False:
                    word_selected = True
                    text = word
                else:
                    word_selected = False
                # If public is selected, erase the password input and select public
                if public_rect.collidepoint(pygame.mouse.get_pos()):
                    public = True
                    word = ''
                # Select private
                elif private_rect.collidepoint(pygame.mouse.get_pos()):
                    public = False
                # Checks if name is not blank
                elif create_rect.collidepoint(pygame.mouse.get_pos()) and name != '' ''' name not in game list ''':
                    #If private make sure the password is valid
                    if public == True or (word !='' and word.isspace() == False):
                        #Here is where all of the data would be sent to the server to add to the server list

                        ### ... requesting to create a new public/private game on server
                        ### Send newGame Message to Server: Expect good/bad ###
                        
                        # if password is nothing, submit null as password.
                        temp = word
                        if temp == '':
                            temp = 'null' 

                        global game_port
                        port = randint(1000, 65535)
                        msg = player_name + " newGame " + name + " " + temp + " " + str(port)
                        print("create_screen: sending = " + msg)
                        cs.send(msg.encode())
                        response = str(cs.recv(1024).decode())
                        #print("create_screen: response = " + response)
                        
                        if response == "good":
                            # created new game, starting process of making game socket
                            gs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                            gs.bind(('', port))
                            gs.listen(1)
                            connection, server_addr = gs.accept()
                            recv = connection.recv(1024).decode()
                            connection.send("confirm".encode())
                            recv = connection.recv(1024).decode().split()
                            port = int(recv[1])
                            print("create_screen recv port = ", port)
                            game_port = port
                            # Creating listener
                            listener = threading.Thread(target=listenerThread, args=(command_queue, gs))
                            listener.setDaemon(True)
                            listener.start()
                            run = wait_screen("create", player_name, port, command_queue, name)
                        else:
                            # error: game name already taken
                            name = 'invalid_name'
                        ### Send newGame Message to Server: Expect good/bad ###

                # Goes back to the first screen if back is pressed
                elif back_rect.collidepoint(pygame.mouse.get_pos()):
                    run = "back"
            # Deals with text input to either box
            elif event.type == pygame.KEYDOWN and (name_selected == True or word_selected == True):
                if event.key == pygame.K_BACKSPACE:
                    text = str(text[: -1])
                else:
                    current_text = font.render(text, True, color['outline'])
                    if current_text.get_width() < nameinput_rect.w - 20 and event.key != pygame.K_SPACE and event.key != pygame.K_MINUS:
                        text += event.unicode
                # Update name or password
                if name_selected == True:
                    name = text
                elif word_selected == True:
                    word = text      
        pygame.display.update()
    # IF back is clicked
    if run == "back":
        run = first_screen(player_name, cs, command_queue)
    # If it made it to the end
    if run == "done":
        return "done"
    # IF closed
    elif run == 0:
        cs.close()
        pygame.quit()
        sys.exit()

# Draw the join screen
def draw_join(screen, font, font2, message_rect, namelabel_rect, playerslabel_rect, publiclabel_rect, namebox_rect, playersbox_rect, publicbox_rect, up_rect, down_rect, back_rect, join_rect, games, select_boxes, lobby_selected):
    text_in_mid(screen, font, "Select a lobby and press join when ready", color["outline"], message_rect)
    text_in_mid(screen, font, "Lobby Name", color["outline"], namelabel_rect)
    text_in_mid(screen, font, "Players in Lobby", color["outline"], playerslabel_rect)
    text_in_mid(screen, font, "Privacy", color["outline"], publiclabel_rect)
    pygame.draw.rect(screen, color["box"], namebox_rect)
    pygame.draw.rect(screen, color["outline"], namebox_rect, 4)
    pygame.draw.rect(screen, color["box"], playersbox_rect)
    pygame.draw.rect(screen, color["outline"], playersbox_rect, 4)
    pygame.draw.rect(screen, color["box"], publicbox_rect)
    pygame.draw.rect(screen, color["outline"], publicbox_rect, 4)
    # Shows all of the available games with their select boxes
    for x in range(0, len(select_boxes)):
        if select_boxes[x].y > namebox_rect.y and select_boxes[x].y < namebox_rect.y + namebox_rect.h - 10:
            if select_boxes[x] == lobby_selected:
                pygame.draw.rect(screen, color["selected"], select_boxes[x])
            else:
                pygame.draw.rect(screen, color["box"], select_boxes[x])
            pygame.draw.rect(screen, color["outline"], select_boxes[x], 2)
            temp = font2.render(games[x][0], True, color["outline"])
            screen.blit(temp, ((namebox_rect.x + (namebox_rect.w - temp.get_width())/2) + 5, select_boxes[x].y))
            temp = font2.render(games[x][1] + "/4", True, color["outline"])
            screen.blit(temp, ((playersbox_rect.x + (playersbox_rect.w - temp.get_width())/2) + 5, select_boxes[x].y))
            if games[x][2] != "1":
                privacy = "Public"
            else:
                privacy = "Private"
            temp = font2.render(privacy, True, color["outline"])
            screen.blit(temp, ((publicbox_rect.x + (publicbox_rect.w - temp.get_width())/2) + 5, select_boxes[x].y))
    draw_btn(screen, font, "Up", up_rect)
    draw_btn(screen, font, "Dwn", down_rect)
    draw_btn(screen, font, "Back", back_rect)
    draw_btn(screen, font, "Join", join_rect)
    
# Make the join screen where the user selects an available game to join        
def join_screen(player_name, cs, command_queue):
    screen = pscreen = set_up_screen([700, 500])
    font = pygame.font.Font(None,30)
    font2 = pygame.font.Font(None,23)
    message_rect = pygame.Rect((0, 0),(700, 50))
    namelabel_rect = pygame.Rect((50, 50),(300, 25))
    namebox_rect = pygame.Rect((50, 75),(300, 350))
    playerslabel_rect = pygame.Rect((350, 50),(150, 25))
    playersbox_rect = pygame.Rect((350, 75),(150, 350))
    publiclabel_rect = pygame.Rect((500, 50),(150, 25))
    publicbox_rect = pygame.Rect((500, 75),(150, 350))
    up_rect = pygame.Rect((650, 175),(50, 50))
    down_rect = pygame.Rect((650, 275),(50, 50))
    back_rect = pygame.Rect((0, 450),(100, 50))
    join_rect = pygame.Rect((600, 450),(100,50))
    select_boxes = []
    lobby_selected = 0
    word_selected = False
    public = False
    height_dif = 0
    # Still need a way to update this whenever a new game is created or a game gets full, this is just for testing
    # If 3rd  != "1" means the game is public
    games = []

    ### ... requesting game list from server
    ### send gameList command to server: Expect gameList response ###
    msg = player_name+" gameList"
    print("join_screen: sending = " + msg)
    cs.sendall(msg.encode())
    recv = cs.recv(1024).decode()
    #print("join_screen: recieved =", recv)
    recv_split = recv.split(" ")
    for i in range(0, len(recv_split)):
        split = recv_split[i].split('-')
        if len(split) == 3:
            games.append(split)
    ### send gameList command to server: Expect gameList response ###
    
    run = 1
    while run == 1:
        screen.fill(color["form"])
        draw_join(screen, font, font2, message_rect, namelabel_rect, playerslabel_rect, publiclabel_rect, namebox_rect, playersbox_rect, publicbox_rect, up_rect, down_rect, back_rect, join_rect, games, select_boxes, lobby_selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                # Click on back
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    run = "back"
                # Click join
                elif join_rect.collidepoint(pygame.mouse.get_pos()) and lobby_selected != 0:
                    # For public lobby
                    if games[select_boxes.index(lobby_selected)][2] == "0":
                        # Add the current user to the list of players for the selected game
                        
                        ### ... connecting to public game with password as null.
                        ### Send joinGame Message to Server: Expect good/bad ###
                        global game_port
                        port = randint(1000, 65535)
                        msg = player_name+" joinGame "+str(games[select_boxes.index(lobby_selected)][0])+" null "+str(port)
                        print("join_screen: sending = ", msg)
                        cs.send(msg.encode())
                        response = str(cs.recv(1024).decode())
                        #print("join_screen: recieving = " + response)

                        if response == "good":
                            # created new game, starting process of making game socket
                            gs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                            gs.bind(('', port))
                            gs.listen(1)
                            connection, server_addr = gs.accept()
                            recv = connection.recv(1024).decode()
                            connection.send("confirm".encode())
                            recv = connection.recv(1024).decode().split()
                            port = int(recv[1])
                            game_port = port
                            print("join_screen: recieved port = ", port)
                            # Creating listener
                            listener = threading.Thread(target=listenerThread, args=(command_queue, gs))
                            listener.setDaemon(True)
                            listener.start()
                            run = wait_screen("create", player_name, port, command_queue, player_name)
                        else:
                            # error: game name already taken
                            pass
                        ### Send joinGame Message to Server: Expect good/bad ###

                    # For private lobby
                    else:
                        run = password_screen(
                            games[select_boxes.index(lobby_selected)][0],
                            games[select_boxes.index(lobby_selected)][2], 
                            player_name, cs, command_queue
                            )
                elif up_rect.collidepoint(pygame.mouse.get_pos()):
                    height_dif -= 26
                    lobby_selected = 0
                elif down_rect.collidepoint(pygame.mouse.get_pos()) and height + height_dif < height:
                    height_dif += 26
                    lobby_selected = 0
                    
                # If select box is clicked
                for x in select_boxes:
                    if x.collidepoint(pygame.mouse.get_pos()):
                        lobby_selected = x
        # Creates all of the select boxes
        height = namebox_rect.y + 5 + height_dif
        select_boxes = []
        for x in games:
            select_boxes.append(pygame.Rect((20, height),(font2.get_height(), font2.get_height())))
            height += font2.get_height() + 10
        pygame.display.update()
    
    if run == "back":
        run = first_screen(player_name, cs, command_queue)
    elif run == "done":
        return "done"
    elif run == 0:
        cs.close()
        pygame.quit()
        sys.exit()
        
# Draw the password screen
def draw_password(screen, font, message_rect, wordlabel_rect, wordinput_rect, back_rect, join_rect, wrong_rect, wrong_text, write, text):
    if(write == True):
        text += "_"
    text_in_mid(screen, font, "Password will not have spaces or dashes", color["outline"], message_rect)
    text_in_mid(screen, font, "Password:", color["outline"], wordlabel_rect)
    draw_btn(screen, font, text, wordinput_rect)
    draw_btn(screen, font, "Back", back_rect)
    draw_btn(screen, font, "Join", join_rect)
    text_in_mid(screen, font, wrong_text, color["outline"], wrong_rect)

# Make the password screen for if the user picks a private lobby
def password_screen(game_name, password, player_name, cs, command_queue):
    screen = set_up_screen([500,250])
    font = font = pygame.font.Font(None,30)
    message_rect = pygame.Rect((0, 50),(500, 25))
    wordlabel_rect = pygame.Rect((75, 100),(75, 25))
    wordinput_rect = pygame.Rect((175, 95),(250, 30))
    wrong_rect = pygame.Rect((0, 175),(500, 50))
    back_rect = pygame.Rect((0, 200),(100, 50))
    join_rect = pygame.Rect((400, 200),(100,50))
    write = False
    text = ""
    wrong_text = ""
    run = 1
    while run == 1:
        screen.fill(color["form"])
        draw_password(screen, font, message_rect, wordlabel_rect, wordinput_rect, back_rect, join_rect, wrong_rect, wrong_text, write, text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                # Click on the input, allow for writing, remove the wrong text
                if wordinput_rect.collidepoint(pygame.mouse.get_pos()):
                    write = True
                    wrong_text = ""
                else:
                    write = False
                # Go back to the join lobby screen
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    run = "back"
                # See if the password is correct, if not, tell them they got the password wrong
                elif join_rect.collidepoint(pygame.mouse.get_pos()):

                    ### ... connecting to private game with password entered. 
                    ### Send Join Game Message to Server: Expect good/bad ###
                    global game_port
                    port = randint(1000, 65535)
                    msg = player_name+" joinGame "+game_name+" "+text+" "+str(port)
                    print("password_screen: sending = ", msg)
                    cs.send(msg.encode())
                    response = str(cs.recv(1024).decode())
                    #print("password_screen: recieving = " + response)
                    
                    if response == "good":
                        # created new game, starting process of making game socket 
                        game_addr = ('', port)
                        gs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        gs.bind(game_addr)
                        gs.listen(1)
                        connection, server_addr = gs.accept()
                        recv = connection.recv(1024).decode()
                        connection.send("confirm".encode())
                        recv = connection.recv(1024).decode().split()
                        port = int(recv[1])
                        game_port = port
                        print("password_screen: recieved port = ", port)
                        # Creating listener
                        listener = threading.Thread(target=listenerThread, args=(command_queue, gs))
                        listener.setDaemon(True)
                        listener.start()
                        run = wait_screen("create", player_name, port, command_queue, game_name)
                    else:
                        # error: invalid password
                        wrong_text = "Wrong Password"
                    ### Send Join Game Message to Server: Expect good/bad ###

            # Deal with text entry
            elif event.type == pygame.KEYDOWN and write == True:
                if event.key == pygame.K_BACKSPACE:
                    text = str(text[: -1])
                else:
                    current_text = font.render(text, True, color['outline'])
                    if current_text.get_width() < wordinput_rect.w - 20 and event.key != pygame.K_SPACE and event.key != pygame.K_MINUS:
                        text += event.unicode
        pygame.display.update()
    if run == "back":
        run = join_screen(player_name, cs, command_queue)
        
    elif run == "done":
        return "done"
    elif run == 0:
        pygame.quit()
        sys.exit()
        
def draw_wait(screen, font, message_rect, message2_rect, back_rect, players):
    text_in_mid(screen, font, "Waiting for additional players...", color["outline"], message_rect)
    text_in_mid(screen, font, "The game will begin momentarily!", color["outline"], message2_rect)
    draw_btn(screen, font, "Back", back_rect)
    
# Still needs to implement this, it will show the user the current player count, and when the player count reaches 4, start the game
def wait_screen(back_to, name, port, command_queue, game_name):
    screen = set_up_screen([500, 200])
    font = font = pygame.font.Font(None,30)
    message_rect = pygame.Rect((0, 25),(500, 25))
    message2_rect = pygame.Rect((0, 75),(500, 25))
    back_rect = pygame.Rect((0, 150),(100, 50))
    # Get the number of players form the server
    # Change this to 4 to go to the game screen
    
    # Preparing client socket
    cs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    global player_name
    player_name = name
    players = 1
    run = 1
    while run == 1:
        
        if not command_queue.empty():
            if command_queue.get() == 'startGame':
                run = "done"
        screen.fill(color["form"])
        draw_wait(screen, font, message_rect, message2_rect, back_rect, players)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                msg = player_name+" leaveGame "+game_name
                print("wait_screen leave game with msg = ", msg)
                cs.bind(cAddress)
                print("reconnecting to main server in wait_screen... " + str(cAddress))
                cs.connect(sAddress)
                print("reconnected, sending leave game msg")
                cs.send(msg.encode())
                cs.close()
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                # Click on the input, allow for writing, remove the wrong text
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    #Remove this game from the list as there are no players
                    if players == 0:
                        print("Lobby Removed")
                    else:
                        ### ... trying to leave game created.
                        ### Send leave Game Message to Server ###
                        msg = player_name+" leaveGame "+game_name
                        print("wait_screen leave game with msg = ", msg)
                        cs.bind(cAddress)
                        print("reconnecting to main server in wait_screen... " + str(cAddress))
                        cs.connect(sAddress)
                        print("reconnected, sending leave game msg")
                        cs.send(msg.encode())
                        ### Send leave Game Message to Server ###
                        
                    run = "back"
        pygame.display.update()
                        
    if run == "back":
        # if ready to head back, restablish connection with main server
        if back_to == "create":
            run = create_screen(player_name, cs, command_queue)
        else:
            run = join_screen(player_name, cs, command_queue)
    if run == "done":
        return "done"
    elif run == 0:
        cs.close()
        pygame.quit()
        sys.exit()

# Draw the text box
def drawTextBox(screen, screen_res, screen_offset, text, write, font, input_entry, text_entries):
    global box_rect, input_rect
    box_sizeX = 250
    box_sizeY = screen_res[1] - 40
    posX = screen_res[0] / 2 - box_sizeX / 2 + screen_offset * 2
    posY = screen_res[1] / 2 - box_sizeY / 2
    box_rect = pygame.Rect(posX, posY, box_sizeX, box_sizeY)
    box_sizeX -= 10
    box_sizeY = 50
    posX += 5
    posY = screen_res[1] - box_sizeY - 25
    input_rect = pygame.Rect(posX, posY, box_sizeX, box_sizeY)

    pygame.draw.rect(screen, color["box"], box_rect)
    pygame.draw.rect(screen, color["outline"], input_rect, 4)
    drawText(font, text, write, input_entry, screen, text_entries)
    
# Draws all of the text for the text and input boxes
def drawText(font, text, write, input_entry, screen, text_entries):
    if write:
        text += '_'
    current_line = font.render(text, True, color["outline"])
    text_height = current_line.get_height()
    check = text_height * (len(input_entry) + 1)
    input_height = input_rect.y + 5
    # Draws the non current input lines
    for i in input_entry:
        if check < input_rect.h:
            temp = font.render(i , True, color["outline"])
            screen.blit(temp ,(input_rect.x + 5, input_height))
            input_height += 15
        check -= text_height
    # Draws the current line
    screen.blit(current_line, (input_rect.x + 5, input_height))
    height = input_rect.y - 20
    # Draws the previously entered text entries
    for i in text_entries:
        if height > box_rect.y:
            temp = font.render(i, True, color["outline"])
            screen.blit(temp, (box_rect.x + 5, height))
            height -= 15

# Draw the rules to the side of the game
def drawRules(screen, screen_res, font, rules):
    box_rect = pygame.Rect((25, 25),(250, screen_res[1] - 50))
    pygame.draw.rect(screen, color["box"], box_rect)
    pygame.draw.rect(screen, color["outline"], box_rect, 5)
    height = 30
    for x in rules:
        temp_rect = pygame.Rect((25, height), (box_rect.w, 20))
        text_in_mid(screen, font, x, color["outline"], temp_rect)
        height += 20

# All of the text for the rules of the game
def writeRules():
    lines = []
    lines.append("Rules")
    lines.append("")
    lines.append("Win by making a line with your pieces")
    lines.append("while trying to block the others")
    lines.append("You only have three of each piece")
    lines.append("")
    lines.append("Lines to Win:")
    lines.append("")
    lines.append("A line of the same sized piece")
    lines.append("vertical, horizontal  or diagnal")
    lines.append("")
    lines.append("Ascending sized pieces")
    lines.append("(sml, med, lrg)")
    lines.append("")
    lines.append("Decending sized pieces")
    lines.append("(lrg, med, sml)")
    lines.append("")
    lines.append("All sized pieces on one spot")
    lines.append("")
    lines.append("Board Controls:")
    lines.append("")
    lines.append("Purple outline shows turn")
    lines.append("Click on piece to pick up")
    lines.append("Right click to drop piece")
    lines.append("Click open spot to place piece")
    lines.append("Escape to undo move before submitting")
    lines.append("Enter to submit move and end turn")
    lines.append("")
    lines.append("Text Box Controls:")
    lines.append("")
    lines.append("Click on text input to selcet it")
    lines.append("Type message to send to players")
    lines.append("Enter to submit text when typing")
    return lines

def draw_labels(screen, font, labels):
    global players, color
    text_in_mid(screen, font, players[0], color["p1"], labels[0])
    text_in_mid(screen, font, players[1], color["p2"], labels[1])
    text_in_mid(screen, font, players[2], color["p3"], labels[2])
    text_in_mid(screen, font, players[3], color["p4"], labels[3])

def create_labels(screen, font):
    labels = []
    labels.append(pygame.Rect((625, 580), (250, 20)))
    labels.append(pygame.Rect((445, 190), (100, 20)))
    labels.append(pygame.Rect((625, 45),(250, 20)))
    labels.append(pygame.Rect((955, 190), (100, 20)))
    return labels

# Draws the win screen
def draw_win(screen, font, message_rect, quit_rect, again_rect, winner):
    text_in_mid(screen, font, winner + " is the winner!", color["outline"], message_rect)
    draw_btn(screen, font, "Quit Game", quit_rect)
    draw_btn(screen, font, "Play Again", again_rect)

# Make the win screen that allows the user to quit or play again
def win_screen(winner):
    screen = set_up_screen([500, 200])
    font = font = pygame.font.Font(None,30)
    message_rect = pygame.Rect((0, 25),(500, 25))
    quit_rect = pygame.Rect((75, 75),(150,100))
    again_rect = pygame.Rect((275, 75),(150,100))
    run = 1
    while run == 1:
        screen.fill(color["form"])
        draw_win(screen, font, message_rect, quit_rect, again_rect, winner)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    run = 0
                elif again_rect.collidepoint(pygame.mouse.get_pos()):
                    return
        pygame.display.update()  
    if run == 0:
        pygame.quit()
        sys.exit()

def send(message,address):
    print("sending", message, "to", address)
    csocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    csocket.bind(('localhost',0))
    csocket.settimeout(5)
    #print(address)
    #try:
    csocket.connect(address)
    length = str(len(message.encode()))
    csocket.sendall(('sending '+length).encode())
    confrimation = csocket.recv(1024)

    csocket.sendall(message.encode())
    #except Exception as e:
    #print('Failure to send message: ' + message + '\n Error code:' + str(e))
    csocket.close()

def listenerThread(gQueue, lSocket):
    print("listener established")
    lSocket.listen(6)
    while True:
        try:
            connection, address = lSocket.accept()
            #print("message --> listener")
            message = connection.recv(1024)
            message = message.decode('ASCII')
            message = message.split(' ')
            length = 0
            rMessage = b''
            if(message[0] == 'sending'):
                length = int(message[1])
                connection.sendall("confirm".encode())
            else:
                print('invalid message in listener: ' + str(message))
            while (len(rMessage) < length):
                rMessage += connection.recv(1024)
            rMessage = rMessage.decode('ASCII')
            print("recv message in listener: " + str(rMessage))
            gQueue.put(rMessage)
            connection.close()

        except Exception as e:
            print('failed to recive message in listenerThread : ' + str(e))
            break
sAddress = ()
cAddress = ('127.0.0.1', 0)

# Argument Management
if len(sys.argv) != 2:
	print("\npython3 OtrioGame.py [server ip]")
	sys.exit(-1)
else:
    sAddress = (sys.argv[1], 33222)

quit_flag = False
while not quit_flag:
    color = {
        # Use color["text"] to access color
        "form": (148, 210, 102),
        "outline": (0, 0, 0),
        "box": (255, 255, 255),
        "selected": (175, 251, 255),
        "player_board": (126, 122, 64), 
        "center_board": (126, 122, 64),
        "board_slot": (194, 199, 170),
        "turn": (128,0,128)
    }

    # Change this to proper ip
    game_port = 0
    player_name = ''

    cs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    cs.bind(cAddress)
    print("attempt to connect to server on " + str(cAddress))
    cs.connect(sAddress)
    print("Connection established.\n")

    # Initialize pygame form
    pygame.init()
    command_queue = queue.Queue()
    # returns player_name, port
    text = first_screen('', cs, command_queue)
    print("player_name: ", player_name)
    print("game port =", game_port)

    screen_res = [1500, 768] # [x, y]
    screen = pygame.display.set_mode(screen_res)
    pygame.display.set_caption("3D Tic-Tac-Toe!")
    player_num = 0
    #icon = pygame.image.load("icon.png")
    #pygame.display.set_icon(icon)-

    # Game Board Stats (You can adjust as necessary)
    screen_offset = 300
    slot_size = 100
    border = 15
    spacing = 10
    text_space = 20

    # Text Box Variables
    write = False
    text = player_name + ": "
    input_entry = []
    text_entries = []
    after_space = False
    before_space = ''
    font = pygame.font.Font(None, 20) 
    rules = writeRules()
    labels = create_labels(screen, font)
    game_addr = (sAddress[0], game_port)

    ###  Initilization of Board  ###
    board = None
    # Get player names and initial board state
    player_names = []
    send(player_name+' getPlayers', game_addr)
    send(player_name+' getBoard', game_addr)
    ###  Initilization of Board  ###


    ###  FORM EVENTS  ###
    run = True
    counter = 0
    draw = False
    canDrawLabels = False
    boardStateReady = False
    boardPlayersReady = False
    while run:
        
        while not command_queue.empty():
            # Read commands here
            origional_cmd = command_queue.get()
            cmd = origional_cmd.split()
            #print("game recieved cmd ", cmd)
            # update getPlayers
            if cmd[0] == "playerNames":
                # Setting player colors from player list recieved
                unordered_players = cmd[1].split('-')
                players = []
                #print("unordered_players: ", unordered_players)
                #print("me: ", player_name)
                # get player number and order player list
                for num in range(len(unordered_players)):
                    if unordered_players[num] == player_name:
                        player_num = num
                        break
                for num in range(len(unordered_players)):
                    players.append(unordered_players[(player_num+num)%4])
                    
                # get player colors
                p_colors = ((97, 153, 252), (255, 40, 0), (	0, 98, 0), (255,215,0))
                for i in range(0,4):
                    color["p"+str(i+1)] = p_colors[(player_num+i)%4]
                #print("players: ", players)
                #print("my player_num= ", player_num, "-->", player_name)
                board = gameBoard(screen, slot_size, border, spacing, text_space, screen_offset, color)
                boardStateReady = True
                canDrawLabels = True
                # update player names on board
            # calls for game winner screen
            elif cmd[0] == "winner":
                time.sleep(2)
                quit_flag = win_screen(cmd[1])
                run = False
            # updates single move
            elif cmd[0] == "sendMove":
                name = cmd[1]
                move = cmd[2].split('-')
                # get player num
                for i in range(len(players)):
                    if players[i] == name:
                        name = 'p'+str(i+1)
                        turn = (i+1)%4 + 1
                        #print("player=", players[i], "-->", name)
                        break
                board.updateMove([int(move[0]), int(move[1]), int(move[2]), name], turn)
                #print("name =", name)
                #print("move =", move)
                
            # updates single chat
            elif cmd[0] == "sendChat":
                origional_cmd = str(origional_cmd[:-1])
                chat = origional_cmd[20:]
                #print(chat)
                split = chat.split('-')
                for i in split:
                    text_entries.insert(0, i)
            # update all moves on board
            elif cmd[0] == "updatePlayer":
                if not boardStateReady:
                    command_queue.put(origional_cmd)
                else:
                    # update board state.
                    pos = cmd[1].split('-')
                    updated_board = []
                    x = []
                    y = [] 
                    z = []
                    for a in range(3):
                        for b in range(3):
                            for c in range(3):
                                z.append(pos[a+b+c])
                            y.append(z)
                            z = []
                        updated_board.append(y)
                        y = []
                    # createPlayers(<bool: Can Control all Players>, <which player starts first>)
                    turn = (player_num+int(cmd[2]))%4+1
                    #print("player(", player_num+1,"):", players[player_num],"--> turn =", turn)
                    board.createPlayers(False, turn)
                    board.loadBoardState(updated_board)
                    boardPlayersReady = True
            else:
                print("command recieved error: ", cmd)
            draw = True
        if draw:
            counter += 1
            screen.fill(color["form"])
            board.drawBoard()
            drawRules(screen, screen_res, font, rules)
            drawTextBox(screen, screen_res, screen_offset, text, write, font, input_entry, text_entries)
            if canDrawLabels:
                draw_labels(screen, font, labels)
            draw = not draw
        if boardStateReady and boardPlayersReady:
            for event in pygame.event.get():
                # Exit button clicked
                if event.type == pygame.QUIT:
                    run = False
                # Covers if a key is pressed while input box is selected
                elif event.type == pygame.KEYDOWN and write == True:
                    # Delete a character from the input
                    if event.key == pygame.K_BACKSPACE:
                        #if you back space on an empty line
                        if text == '' and len(input_entry) > 0:
                            text = input_entry[len(input_entry) - 1]
                            input_entry.pop()
                            #afterSpace = False
                        elif text != player_name + ": ":
                            text = str(text[: -1])
                    # Enter the text to the chat
                    elif event.key == pygame.K_RETURN:
                        input_entry.append(text)
                        chat = ""
                        for i in input_entry:
                            chat += i + '-'
                        send(player_name+" SubmitText " + chat, game_addr)
                        input_entry = []
                        text = player_name + ': '
                        after_space = False
                        write = False
                    else:
                        # Covers if a space is added
                        if event.key == pygame.K_SPACE:
                            after_space = ''
                            before_space = text
                        elif after_space != False:
                            after_space += event.unicode
                        text += event.unicode
                        # Covers if the text is to long for the input box
                        current_text = font.render(text, True, color['outline'])
                        if current_text.get_width() > input_rect.w - 15:
                            # Allows the user to mash keys without spaces with still going to the next line
                            if after_space == False:
                                input_entry.append(text)
                                text = ''
                                before_space = ''
                                after_space = False
                            else:
                                input_entry.append(before_space)
                                text = after_space
                                before_space = ''
                                after_space = False
                    drawText(font, text, write, input_entry, screen, text_entries)
                # If Resizesed
                #if event.type == pygame.VIDEORESIZE:
                    #screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    #board.updateSize(screen)
                    #draw = True

                # Check for keyPressed
                if event.type == pygame.KEYDOWN:
                    key = event.key
                    # If return or enter is pressed
                    if key in (pygame.K_KP_ENTER, pygame.K_RETURN) and write == False:
                        try:
                            # playerMove = (pos1, pos2, size, ('p1' to 'p4'))
                            # sizes (0 = small, 1 = medium, 2 = large)
                            # | (0,0) | (1,0) | (2,0) | 
                            # | (1,0) | (1,1) | (1,1) | <-- positions on board
                            # | (2,0) | (2,1) | (2,2) |
                            pm = board.submitMove()
                            msg = player_name+' submitMove '+str(pm[0])+'-'+str(pm[1])+'-'+str(pm[2])
                            send(msg, game_addr)
                        except ValueError:
                            # board.submitMove() did not have a move to submit
                            print("Could not make move")
                    # If escape is pressed
                    if key == pygame.K_ESCAPE:
                        board.undoMove()
                    draw = True

                # Checks if the mouse button is pressed
                if event.type == pygame.MOUSEBUTTONUP:
                    # Checks if the text input box is clicked
                    if input_rect.collidepoint(pygame.mouse.get_pos()):
                        write = True
                    else:
                        write = False
                    # Left Click
                    if event.button == 1:
                        board.selectPiece(pygame.mouse.get_pos())
                    # Right Click
                    elif event.button == 3:
                        board.deselectPiece(pygame.mouse.get_pos())
                    draw = True
                
                # If mouse is moving
                if event.type == pygame.MOUSEMOTION:
                    # Update Held Piece Position, returns true
                    if board.updateSelectedPos():
                        draw = True
                    
        pygame.display.update()
pygame.quit()
cs.close()
sys.exit()
    ###  FORM EVENTS  ###