# CSS-4342-001
# 11/16/2021
# Michael Lawrence

import sys
import os.path 

program = []
base = 0
avaliable_memory = 4000

def main():
    
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
        print("===============================================")
        try:
            # opcode (1) = Add
            if (opcode == 1):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]} {program[pc+3]}] at {pc}")
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = args[0] + args[1]
                print(f"ADD {args[0]} + {args[1]} = {program[program[pc+3]]} => stored at {pos}\n")
                pc+=4
                
            # opcode (2) = Multiply
            elif (opcode == 2):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]} {program[pc+3]}] at {pc}")
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = args[0] * args[1]
                print(f"MULTIPLY {args[0]} * {args[1]} = {program[program[pc+3]]} => stored at {pos}\n")
                pc+=4
            
            # opcode (3) = Store User Input at position
            elif (opcode == 3):
                print(f"[{program[pc]} {program[pc+1]}] at {pc}")
                program[getResultPos(pc, 2)] = setInput()
                print(f"INPUT = {program[program[pc+1]]} => stored at {getResultPos(pc, 2)}\n")
                pc+=2
            
            # opcode (4) = Output next value
            elif (opcode == 4):
                print(f"[{program[pc]} {program[pc+1]}] at {pc}")
                args = getArgValues(pc, 1)
                setOutput(args[0])
                pc+=2
                
            # opcode (5) = Jump-If-True: if first argument is not 0, then update
            #                            instruction pointer to argument 2
            elif (opcode == 5):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]}] at {pc}")
                args = getArgValues(pc, 2)
                print(f"JUMP-IF-TRUE = {args[0] != 0} changing pc to {args[1] if (args[0] != 0) else pc + 3}\n")
                pc = args[1] if (args[0] != 0) else pc + 3
            
            # opcode (6) = Jump-If-False: like Jump-If-True, but on 0.
            elif (opcode == 6):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]}] at {pc}")
                args = getArgValues(pc, 2)
                print(f"JUMP-IF-FALSE = {args[0] == 0} changing pc to {args[1] if (args[0] == 0) else pc + 3}\n")
                pc = args[1] if (args[0] == 0) else pc + 3
            
            # opcode (7) = less than: compare two args and store 0 (false) or 1 (true)
            elif (opcode == 7):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]} {program[pc+2]}] at {pc}")
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = 1 if (args[0] < args[1]) else 0
                print(f"LESS-THAN {args[0]} < {args[1]} ? {1 if (args[0] < args[1]) else 0} => stored at {pos}\n")
                pc+=4
                
            # opcode (8) = Equals: compare two args and store 0 (false) or 1 (true)
            elif (opcode == 8):
                print(f"[{program[pc]} {program[pc+1]} {program[pc+2]} {program[pc+2]}] at {pc}")
                args = getArgValues(pc, 2)
                pos = getResultPos(pc, 4)
                program[pos] = 1 if (args[0] == args[1]) else 0
                print(f"EQUALS {args[0]} == {args[1]} ? {1 if (args[0] == args[1]) else 0} => stored at {pos}\n")
                pc+=4
                
            # opcode (9) = Adjust the relative base of the program
            elif (opcode == 9):
                print(f"[{program[pc]} {program[pc+1]}] at {pc}")
                args = getArgValues(pc, 1)
                print(f"BASE-ADJUST {base} + {args[0]} = {base + args[0]}\n")
                base+=args[0]
                pc+=2
            
            # opcode (99) = Halt Execution
            elif (opcode == 99):
                print(f"Intcode: HALT at pos[{pc}]")
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
            print(f"\tARG[{i}] mode 0: value = {program[program[pc+1+i]]}")
        elif (mode == 1): # immediate mode
            values_list.append(program[pc+1+i])
            print(f"\tARG[{i}] mode 1: value = {program[pc+1+i]}")
        elif (mode == 2): # relative mode
            values_list.append(program[program[pc+1+i]+base])
            print(f"\tARG[{i}] mode 2: value = {program[program[pc+1+i]+base]} with base ({base})")
        else:
            raise ValueError("Argument mode provided ("+str(mode)+") in opcode ("+str(program[pc])+") is invalid. " + 
                             "Modes must be either:\n\t0: Positional mode\n\t1: Immediate mode\n\t2: Relative Mode")
    
    return values_list
  
def getResultPos(pc, sizeOfCommand):

    global program, base

    modes = str(program[pc] // 100)
    mode = program[pc+sizeOfCommand-1]

    if len(modes) == (sizeOfCommand-1):
        print(f"\tRST[{sizeOfCommand-2}] mode 2: store at {program[pc+sizeOfCommand-1]+base} (base {base})")
        mode = program[pc+sizeOfCommand-1]+base
    else:
        print(f"\tRST[{sizeOfCommand-2}] mode 0: store at {program[pc+sizeOfCommand-1]}")
    
    return mode

  
# Simple retrieval of user input

def setInput():
    try:
        return int(input("Enter Input --> "))
    except:
        print("Error, user entered invalid integer, try again.")
        return setInput()


# Even more simple output

def setOutput(output):
    print("Output = " + str(output))

if __name__ == "__main__":
    main()