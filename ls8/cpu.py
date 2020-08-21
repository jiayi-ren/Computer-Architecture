"""CPU functionality."""

import sys
import datetime

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        # self.sp = 0xF4
        self.reg[7] = 0xF4
        self.branchtable = {
            HLT: self.HLT,
            LDI: self.LDI,
            PRN: self.PRN,
            ADD: self.ADD,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE,
            AND: self.AND,
            OR: self.OR,
            XOR: self.XOR,
            NOT: self.NOT,
            SHL: self.SHL,
            SHR: self.SHR,
            MOD: self.MOD
        }
        self.fl = [0] * 8

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

    def PRN(self, operand_a, operand_b = None):
        print(self.reg[operand_a])
        # self.pc += 2

    def ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        # self.pc += 3
    
    def PUSH(self, operand_a, operand_b = None):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[operand_a])
        # self.pc += 2

    def POP(self, operand_a, operand_b = None):
        self.reg[operand_a] = self.ram_read(self.reg[7])
        # self.ram_write(self.reg[7], 0)
        self.reg[7] += 1
        # self.pc += 2
    
    def CALL(self, operand_a, operand_b):
        self.reg[4] = self.pc + 2
        self.PUSH(4, operand_b)
        self.pc = self.reg[operand_a]

    def RET(self, operand_a = None, operand_b = None):
        # print(self.ram_read(self.reg[7]))
        self.pc = self.ram_read(self.reg[7])
        # self.POP(4, operand_b)

    def CMP(self, operand_a, operand_b):
        # self.alu("SUB", operand_a, operand_b)
        self.alu("CMP", operand_a, operand_b)
    
    def JMP(self, operand_a, operand_b = None):
        self.pc = self.reg[operand_a]
    
    def JEQ(self, operand_a, operand_b = None):
        ir = self.ram[self.pc]
        self.pc = self.reg[operand_a] if self.fl[7] else self.pc+(ir >> 6) + 1

    def JNE(self, operand_a, operand_b = None):
        ir = self.ram[self.pc]
        self.pc = self.reg[operand_a] if not self.fl[7] else self.pc+(ir >> 6) + 1

    def AND(self, operand_a, operand_b):
        self.alu("AND", operand_a, operand_b)

    def OR(self, operand_a, operand_b):
        self.alu("OR", operand_a, operand_b)

    def XOR(self, operand_a, operand_b):
        self.alu("XOR", operand_a, operand_b)

    def NOT(self, operand_a, operand_b):
        self.alu("NOT", operand_a, operand_b)

    def SHL(self, operand_a, operand_b):
        self.alu("SHL", operand_a, operand_b)
        
    def SHR(self, operand_a, operand_b):
        self.alu("SHR", operand_a, operand_b)

    def MOD(self, operand_a, operand_b):
        self.alu("MOD", operand_a, operand_b)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] - self.reg[reg_b] == 0:
                self.fl[7] = 1
            elif self.reg[reg_a] - self.reg[reg_b] < 0:
                self.fl[5] = 1
            else:
                self.fl[6] = 1
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] %= self.reg[reg_b]
            else:
                print("Invalid divisor")
                self.HLT(reg_a, reg_b)
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
            
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # print("opa ", operand_a, "  ", "opb ", operand_b)
            # if self.pc == 17:
            #     sys.exit(1)
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
                # print(ir, "bit", ir & 0b00010000)
                if ir != CALL and ir != RET and ir != JMP and ir != JEQ and ir != JNE:
                    n_of_arg = ir >> 6
                    size_instr = n_of_arg + 1
                    self.pc += size_instr