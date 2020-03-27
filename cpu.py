"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #create 8 registrars
        self.reg = [0b0] * 8
        #set the program counter to 0
        self.pc = 0
        #create 256 bytes of RAM
        self.ram = [0b0] * 0xFF
        self.reg[7] = 0xF4
        self.sp = self.reg[7]

    def load(self,script):

        address = 0

        # For now, we've just hardcoded a program:
        # Removing the hardcoded comments to create read in function
        #to add machine code to RAM
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000, #registrar 0
        #     0b00001000, # value 8
        #     0b01000111, # PRN R0
        #     0b00000000, #print value in first registrar
        #     0b00000001, # HLT
        # ]
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        with open(script) as f:
            for line in f:
                #print(line)
                #blank comments should be skipped
                #in the event there is a comment
                #we want the data to the left of the # symbol
                #.strip is used to remove whitespace
                comment_split = line.split("#")
                command = comment_split[0].strip()
                #The command needs to be casted and set to base 2
                #print('command is: ' + command)
                #print(f"COMMAND:{command}")
                if command == '':
                    continue
                value = int(command,2)
                #print('value is: ' + str(value))
                #assign the converted value into the next entry in ram
                self.ram[address] = value
                #after entered into ram, increment the address value by 1
                #to write to the next space of ram in the next command.
                address += 1
                

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
             self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
             self.reg[reg_a] *= self.reg[reg_b]
        #if the comparison register is called
        elif op == 'CMP':
            #The flag parameter according to the spec:
            #FL bits: 00000LGE
            if self.reg[reg_a] == self.reg[reg_b]:
                #according to spec if values are equal...
                #If they are equal, set the Equal E flag to 1, otherwise set it to 0.
                self.flag = 0b00000001
            #if a is less than b
            elif self.reg[reg_a] < self.reg[reg_b]:
                #set the less than flag to 1
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                #set the greater than flag to 1
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")
    
    def ram_read(self, address):
        """
        Reads the value at the designated address of RAM
        """
        return self.ram[address]
    def ram_write(self,address,value):
        """
        Writes a value to RAM at the designated address
        """
        self.ram[address] = value


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """
        The core running of our built CPU
        """
        #kept in a while loop to continue working through passed in commands.
        running = True
        while running == True:
            #print(f"PC:{self.pc}")
            #the Load function writes pre-written commands in the program variable to RAM
            #As a result, the instructions as loaded should cycle through RAM.
            instruction = self.ram[self.pc]

            #first checking to see if the command passed in is HALT
            #If HALT is passed, stop the program
            if instruction == 0b00000001:
                running = False
                self.pc += 1
            #checking if instruction is to set registrar to integer:
            #From Spec:
            # `LDI register immediate`
            # Set the value of a register to an integer.  
            #The first value sets which registrar will be assigned the integer
            #The Second value determines what that value is
            #The PC (program counter) goes one forward to see the value
            elif instruction == 0b10000010:
                #LDI FUNCTION
                #one RAM entries out determines which registrar is loaded
                reg_slot = self.ram_read(self.pc + 1)
                #two ram entries out determines what value is loaded
                int_value = self.ram_read(self.pc + 2)
                
                #The registrar at slot reg_slot is being assigned the int_value both
                #determined from RAM above
                self.reg[reg_slot] = int_value
                #the program counter is set 3 entries ahead
                #one for the current instruction
                #one for the integer value
                #one for the registrar slot
                self.pc += 3    
            #Writing logic for if the Print function is called
            elif instruction == 0b01000111:
                #PRT FUNCTION
                #import pdb; pdb.set_trace()
                #loading which registrar slot should be preinted
                reg_slot = self.ram_read(self.pc + 1)
                #prints the value at that registrar slot
                print(self.reg[reg_slot])

                #inriments by two
                #one for the current instruction
                #one for the reg_slot
                self.pc += 2
            elif instruction == 0b10100010:
                #if MULT is called

                #grab the next two values in the program counter
                #to find out what values in the registrar are going to be multiplied
                reg_slot_1 = self.ram[self.pc+1]
                reg_slot_2 = self.ram[self.pc+2]
                self.alu('MUL',reg_slot_1,reg_slot_2)
                self.pc +=3
            elif instruction == 0b10100000:
                #if ADD is called

                #grab the next to values in the program counter
                #to findo ut what values in the registrar are going to be added
                reg_slot_1 = self.ram[self.pc+1]
                reg_slot_2 = self.ram[self.pc+2]
                self.alu('ADD',reg_slot_1,reg_slot_2)
                self.pc +=3
            elif instruction == 0b01000101:
                #PUSH
                #determine which registrar is pushing their value to the stack
                reg_slot = self.ram[self.pc+1]
                val = self.reg[reg_slot]
                #decriment the stack pointer
                self.sp -= 1
                #push the value pulled from the registar to the stack
                self.ram[self.sp] = val
                self.pc += 2
            elif instruction == 0b01000110:
                #POP
                #determine which registrar will get the value popped from the stack
                reg_slot = self.ram[self.pc+1]      
                #val = self.reg[reg_slot]
                #update the value of the registrar
                #at the reg_slot with the assigned value
                value = self.ram[self.sp]
                self.reg[reg_slot] = value
                #incriment the stack pointer      
                self.sp += 1
                self.pc +=2
            elif instruction == 0b01010000:
                #CALL FUNCTION
                #since the CALL spec has the address after the CALL instruction
                #designate the registrar slot and the second address is the return address...
                return_address = self.pc + 2
                #decriment the stack pointer by 1
                self.sp -= 1
                #assign the new top of the stack the value of the return address
                #this relates to the RET function, as this will be the return address
                #once the call stack completes
                self.ram[self.sp] = return_address

                #with the return addres stored
                #determine what registar slot is used for the called function
                reg_slot = self.ram[self.pc+1]
                #the subroutine location is the value at that designated reg slot
                subroutine_location = self.reg[reg_slot]
                #the program counter is set to the location of that sub routine
                self.pc = subroutine_location

            elif instruction == 0b00010001:
                #RET FUNCTION
                #The Return Address is the location in ram where the stack pointer is at
                #(this is because the call function should fully execute what it is on the stack)
                return_address = self.ram[self.sp]
                #the stack than incriments
                #this returns to the function code prior to the call
                self.sp += 1
                #the program counter is then set to where the return address points to
                self.pc = return_address
            elif instruction == 0b10100111:
                #CMP FUNCTION
                #the compare function takes the next to values in the program counter
                #as the pointers to the registers to be compared to
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                #calls the ALU function's CMP command
                self.alu("CMP", reg_a, reg_b)
                #PC incriments 3 times, since there are two arguments for CMP
                self.pc += 3
            elif instruction == 0b01010100:
                ##JUMP FUNCTION
                #the next value in the program counter is the address to jump to
                address = self.ram_read(self.pc + 1)
                #the program counter because the address we poitned to from the JUMP function
                self.pc = self.reg[address]
            elif instruction == 0b01010101:
                #JEQ FUNCTION
                #the next value in the PC is the address to go to
                #IF CMP function returned an equal flag
                address = self.ram_read(self.pc + 1)
                #Checks if flag is Equal
                if self.flag == 0b00000001:
                    #if values are equal, jump to that designated address
                    self.pc = self.reg[address]
                else:
                    #if the value is NOT equal, skip over the JEQ logic to next command
                    self.pc +=2
            elif instruction == 0b01010110:
                #JNE FUNCTION
                #the next value in the PC is the address to go to
                #IF CMP function did NOT return an equal flag
                address = self.ram_read(self.pc +1)
                if self.flag != 0b00000001:
                    #opposite JEQ, if not equal, then jump to the address.
                    self.pc = self.reg[address]
                else:
                    #if the value IS equal, skip over the JNE logic to next command
                    self.pc += 2
                pass
            else:
                print("I do not recognize that command")
                print(f"You are currently at Program Counter value: {self.pc}")
                print(f"The command issued was: {self.ram_read(self.pc)}")
                sys.exit(1)
