"""
@brief: arithmetic logic unit for 64-bit risc cpu
implements basic arithmetic and logical operations
"""

from myhdl import *

@block
def alu(a, b, op, result):
    """
    @brief: arithmetic logic unit
    @param a: first operand (64-bit)
    @param b: second operand (64-bit)
    @param op: operation selector
    @param result: result of operation (64-bit)
    """
    @always_comb
    def logic():
        if op == 0:
            result.next = a + b
        elif op == 1:
            result.next = a - b
        elif op == 2:
            result.next = a & b
        elif op == 3:
            result.next = a | b
        elif op == 4:
            result.next = a ^ b  # xor(EXclusive OR) operation
        elif op == 5:  # alu_sll
            shift_amount = int(b) & 0x3F
            shift_amount = min(shift_amount, 63)
            result.next = int(a) << shift_amount
        elif op == 6:  # alu_srl
            shift_amount = int(b) & 0x3F
            shift_amount = min(shift_amount, 63)
            result.next = int(a) >> shift_amount
        elif op == 7:  # alu_sra
            shift_amount = int(b) & 0x3F
            shift_amount = min(shift_amount, 63)  # max shift

            a_val = int(a)

            if a_val & (1 << 63):  # if msb is 1 (negative number in 2's complement)

                if shift_amount == 0:
                    result.next = a_val
                else:
                    shifted = (a_val >> shift_amount)
                    # apply sign extension mask
                    sign_extension = ((1 << shift_amount) - 1) << (64 - shift_amount)
                    result.next = shifted | sign_extension
            else:
                result.next = a_val >> shift_amount
        elif op == 8:  # slt
            a_signed = a if a < 2**63 else a - 2**64
            b_signed = b if b < 2**63 else b - 2**64
            result.next = 1 if a_signed < b_signed else 0
        elif op == 9:  # sltu
            # set less than unsigned: result = 1 if a < b (unsigned comparison), else 0
            result.next = 1 if a < b else 0
        elif op == 10:  # alu_mov
            result.next = b
        elif op == 11:  # alu_call
            result.next = a + 4  # calculate return address (next instruction)
        elif op == 12:  # alu_jmp
            # for pc-relative jump: target = pc + immediate
            result.next = a + b
        elif op == 13:  # alu_ret
            result.next = a
        elif op == 14:  # alu_nand
            # nand is not(and) - need to mask to 64-bit to avoid bounds issues
            result.next = ~(a & b) & ((1 << 64) - 1)  # nand with 64-bit mask
        else:
            result.next = 0
    return logic


