"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        self.sp = len(self.ram)
        self.branchtable = {
            HLT: self.HLT,
            LDI: self.LDI,
            PRN: self.PRN,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        if len(sys.argv) != 2:
            print("usage: ls8.py progname")
            sys.exit(1)
        try:
            filename = sys.argv[1]
            with open(filename) as f:
                for l in f:
                    words = l.split()
                    if len(words) == 0:
                        continue
                    if words[0] == '#':
                        continue
                    try:
                        self.ram[address] = int(words[0], 2)
                        address += 1
                    except ValueError:
                        print(f"Invalid number: {words[0]}")
                        sys.exit(2)
                    except IndexError:
                        print(f"Invalid index")
                        sys.exit(3)
        except FileNotFoundError:
            print(f"Couldn't find {sys.argv[1]}")
            sys.exit(4)

        if address == 0:
            print("Program was empty")
            sys.exit(5)

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
    
    def HLT(self, operand_a, operand_b):
        self.running = False

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        # self.pc += 3

    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        # self.pc += 2

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        # self.pc += 3
    
    def PUSH(self, operand_a, operand_b):
        self.sp -= 1
        self.ram_write(self.sp, self.reg[operand_a])
        # self.pc += 2

    def POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram_read(self.sp)
        self.ram_write(self.sp, 0)
        self.sp += 1
        # self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

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
        """Run the CPU."""
        
        while self.running:
            ir = self.ram[self.pc]
            # self.trace()
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # if ir == 0b10000010: # LDI R0,8
            #     self.LDI(operand_a, operand_b)
            #     
            # elif ir ==  0b01000111: # PRN R0
            #     self.PRN(operand_a)
            #     self.pc += 2
            # elif ir == 0b00000001: # HLT
            #     self.HLT()
            # elif ir == 0b10100010: # MULT
            #     self.MUL(operand_a, operand_b)
            #     self.pc += 3
            if ir in self.branchtable:
                self.branchtable[ir](operand_a,operand_b)

            n_of_arg = ir >> 6
            size_instr = n_of_arg + 1
            self.pc += size_instr
