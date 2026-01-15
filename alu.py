from myhdl import *

@block
def alu(a, b, op, result):

    @always_comb
    def logic():

        shamt = b[6:0]  # 6-bit shift amount (0–63)

        if op == 0:        # ADD
            result.next = a + b

        elif op == 1:      # SUB
            result.next = a - b

        elif op == 2:      # AND
            result.next = a & b

        elif op == 3:      # OR
            result.next = a | b

        elif op == 4:      # XOR
            result.next = a ^ b

        elif op == 5:      # SLL
            result.next = a << shamt

        elif op == 6:      # SRL
            result.next = a >> shamt

        elif op == 7:      # SRA (arithmetic shift right)
            result.next = a.signed() >> shamt

        elif op == 8:      # SLT (signed)
            result.next = 1 if a.signed() < b.signed() else 0

        elif op == 9:      # SLTU (unsigned)
            result.next = 1 if a < b else 0

        elif op == 10:     # MOV
            result.next = b

        elif op == 11:     # CALL
            result.next = a + 4

        elif op == 12:     # JMP
            result.next = a + b

        elif op == 13:     # RET
            result.next = a

        elif op == 14:     # NAND
            result.next = (a & b) ^ 0xFFFFFFFFFFFFFFFF  # Perform NAND by AND followed by NOT

        else:
            result.next = 0

    return logic
