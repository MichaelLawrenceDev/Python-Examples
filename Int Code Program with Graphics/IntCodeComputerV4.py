# CSS-4342-001
# 11/16/2021
# Michael Lawrence

import sys
import os.path
import random
import msvcrt
import threading
import time
from graphics import *

program = []
base = 0
avaliable_memory = 4000
output_list = []
win = None
input = 0
startDrawWhiteSpace = False

# BREAKOUT ATTRIBUTES
spacing = 2
size = 15
screenSpacing = size + spacing
topSpace = 50
screen_size = (
    42*(spacing+size*2)+screenSpacing*2, 
    22*(spacing+size*2)+screenSpacing*2 + topSpace*2
)
scoreText = None
howToPlayText = None

# AI Variables
ball_pos = 0
paddle_pos = 0
moveIn = 0 
modeAI = False

def main():
    global win, scoreText, howToPlayText

    win = GraphWin("BREAKOUT", 
        screen_size[0], 
        screen_size[1]
    )
    # Text
    t = Text(Point(screen_size[0]/2,topSpace/2), "---=  BREAKOUT!  =---")
    t.setSize(36)
    t.setStyle("bold italic")
    t.draw(win)

    t = Text(Point(150,topSpace/2+10), "INTCODE  =---")
    t.setSize(24)
    t.setStyle("bold italic")
    t.draw(win)

    howToPlayText = Text(Point(screen_size[0]/2,screen_size[1]-topSpace/2), 
        "Use [A/S/D] or equivalent [arrow keys] (console must be selected)  -  OR  -  [Enter] for AI control, once enabled, stays enabled.")
    howToPlayText.setSize(17)
    howToPlayText.draw(win)

    scoreText = Text(Point(screen_size[0]-150,topSpace/2+10), "---=  SCORE: 0 ")
    scoreText.setSize(24)
    scoreText.setStyle("bold italic")
    scoreText.draw(win)

    # Verify arguments, and grab intcode from passed in file...
    if (len(sys.argv) != 2):
        sys.exit("Usage: IntCodeComputer.py <filename>")
    elif (not os.path.exists(sys.argv[1])):
        sys.exit("Could not find filepath \"" + sys.argv[1] + "\".")
    
    global program    
    program = loadProgram(sys.argv[1])
    executeProgram()

# Verify Arguments: Check if 1 argument has been entered containing a valid filepath. 
# Returns the intcode read (list of integers).
def loadProgram(filename):
    global avaliable_memory
    
    try:
        intcode = []
        file = open(filename, "r")
        raw = file.readlines()
        file.close()
        
        for line in raw:
            tmp = line.strip().split(",")
            for integer in tmp:
                intcode.append(int(integer))
        
    except:
        sys.exit("Could not read file. File not formated as intcode.")
        
    # fill remaining memory slots with 0.
    for i in range(avaliable_memory - len(intcode)):
        intcode.append(0)
    
    return intcode
      

def executeProgram():
    
    global program, base
    
    pc = 0   # program counter
    base = 0 # relative base
    success = False

    while (not success):
        opcode = program[pc] % 100
        try:
            # opcode (1) = Add
            if (opcode == 1):
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = args[0] + args[1]
                pc+=4
                
            # opcode (2) = Multiply
            elif (opcode == 2):
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = args[0] * args[1]
                pc+=4
            
            # opcode (3) = Store User Input at position
            elif (opcode == 3):
                inp = setInput()
                program[program[pc+1]] = inp
                pc+=2
            
            # opcode (4) = Output next value
            elif (opcode == 4):
                args = getArgValues(pc, 1)
                setOutput(args[0])
                pc+=2
                
            # opcode (5) = Jump-If-True: if first argument is not 0, then update
            #                            instruction pointer to argument 2
            elif (opcode == 5):
                args = getArgValues(pc, 2)
                pc = args[1] if (args[0] != 0) else pc + 3
            
            # opcode (6) = Jump-If-False: like Jump-If-True, but on 0.
            elif (opcode == 6):
                args = getArgValues(pc, 2)
                pc = args[1] if (args[0] == 0) else pc + 3
            
            # opcode (7) = less than: compare two args and store 0 (false) or 1 (true)
            elif (opcode == 7):
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = 1 if (args[0] < args[1]) else 0
                pc+=4
                
            # opcode (8) = Equals: compare two args and store 0 (false) or 1 (true)
            elif (opcode == 8):
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = 1 if (args[0] == args[1]) else 0
                pc+=4
                
            # opcode (9) = Adjust the relative base of the program
            elif (opcode == 9):
                args = getArgValues(pc, 1)
                base+=args[0]
                pc+=2
            
            # opcode (99) = Halt Execution
            elif (opcode == 99):
                success = True
                
            # Other opcodes will lead to program failure
            else:
                print("Error: Opcode [" + str(opcode) + "] at position " + str(pc) + " is not a valid opcode")
                break
                
        except IndexError:
            print("Error: Opcode [" + str(opcode) + "] at position " + str(pc) + 
                " has arguments that reference values outside of the program's index range.")
            success = True
        except ValueError as e:
            print(e)
            success = True
        
    
# Return: a list of values with length of equal to the number of args required
# modes[0] = mode of arg1, modes[1] = mode of arg2, ext...  
# mode can be either 0 (positional mode), 1 (immediate mode), or 2 (relative mode)
#   0: use argument as address to value
#   1: use argument as value
#   2: use argument as a relative address to value

def getArgValues(pc, numOfArgs):

    global program, base
    
    modes = str(program[pc] // 100)[::-1] # isolate arguments and reverse order
    values_list = []
    
    for i in range(numOfArgs):
        mode = 0
        try:
            mode = int(modes[i])
        except IndexError:
            pass # index error means a leading zero was removed.
            
        if (mode == 0): # positional mode
            values_list.append(program[program[pc+1+i]])
        elif (mode == 1): # immediate mode
            values_list.append(program[pc+1+i])
        elif (mode == 2): # relative mode
            values_list.append(program[program[pc+1+i]+base])
        else:
            raise ValueError("Argument mode provided ("+str(mode)+") in opcode ("+str(program[pc])+") is invalid. " + 
                             "Modes must be either:\n\t0: Positional mode\n\t1: Immediate mode\n\t2: Relative Mode")
    
    return values_list
  
def getResultPos(pc, sizeOfCommand):

    global program, base

    modes = str(program[pc] // 100)
    mode = program[pc+sizeOfCommand-1]

    if len(modes) == (sizeOfCommand-1):
        mode = program[pc+sizeOfCommand-1]+base
    
    return mode

  
# Simple retrieval of user input
def setInput():
    global input, moveIn

    # Wait get input ...
    if (not modeAI):
        thread = threading.Thread(target=keypressed) # from keys
        thread.start()
        thread.join()
    else:
        time.sleep(moveIn)
        updateGame(move())

    return input
    
def keypressed():
    global modeAI
    input_char = msvcrt.getch()

    if input_char == 'a'.encode() or input_char == 'K'.encode():
        updateGame(-1) # a or left arrow
    elif input_char == 's'.encode() or input_char == 'P'.encode():
        updateGame(0)  # s or down arrow
    elif input_char == 'd'.encode() or input_char == 'M'.encode():
        updateGame(1)  # d or right arrow
    elif input_char == 'a'.encode() or input_char == b'\r':
        print("AI-MODE ENABLED")
        modeAI = True
        updateGame(move())
    else:
        keypressed()

def move():
    global ball_pos, paddle_pos

    if ball_pos > paddle_pos:
        return 1
    elif ball_pos < paddle_pos:
        return -1
    else:
        return 0

def updateGame(value):
    global input
    input = value

def createRect(x, y):
    # Rectangle Pos
    upperLeftCorner = Point(
        x*(size*2+spacing)-size+screenSpacing, 
        y*(size*2+spacing)-size+screenSpacing+topSpace)
    lowerRightCorner = Point(
        x*(size*2+spacing)+size+screenSpacing, 
        y*(size*2+spacing)+size+screenSpacing+topSpace)
    
    return Rectangle(upperLeftCorner, lowerRightCorner)

# Even more simple output
def setOutput(output):

    #   Draws output
    global scoreText, ball_pos, paddle_pos
    output_list.append(output)

    # output list (x, y, type)
    if (len(output_list) == 3):

        if output_list[0] == -1: # not tile, rather score
            scoreText.setText(f"---=  SCORE: {output_list[2]}")

        # ADD SQUARES TO GAME
        elif output_list[2] == 0: # empty tile
            obj = createRect(output_list[0], output_list[1])
            obj.setFill(color_rgb(255,255,255))
            obj.setOutline(color_rgb(255,255,255))
            obj.draw(win)

        elif output_list[2] == 1: # wall tile
            # random shades of gray
            obj = createRect(output_list[0], output_list[1])
            num = random.randrange(60,100)
            obj.setFill(color_rgb(num, num, num))
            obj.draw(win)
            
        elif output_list[2] == 2: # block tile
            # tiered blue
            obj = createRect(output_list[0], output_list[1])
            num = random.randrange(0,40)
            y = output_list[1]*5
            obj.setFill(color_rgb(74+num+y,104+num+y,255))
            obj.draw(win)

        elif output_list[2] == 3: # horizontal paddle tile
            paddle_pos = output_list[0]
            obj = createRect(output_list[0], output_list[1])
            obj.setFill(color_rgb(160,82,45))
            obj.draw(win)

        elif output_list[2] == 4: # ball tile (moves diagonally and bounces off objects)
            ball_pos = output_list[0]
            obj = Circle(Point(
                output_list[0]*(size*2+spacing)+screenSpacing, 
                output_list[1]*(size*2+spacing)+screenSpacing+topSpace), 
                size)
            obj.setFill(color_rgb(255,69,0))
            obj.draw(win)

        output_list.clear()


if __name__ == "__main__":
    main()