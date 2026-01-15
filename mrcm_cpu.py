"""
@brief: 64-bit risc cpu implementation
this is a single-issue, single-cycle risc-like core with extended ops
"""

from myhdl import *
from alu import alu
from reg import regfile

# risc-v instruction opcodes
R_TYPE = 0b0110011
I_TYPE = 0b0010011
LOAD = 0b0000011
STORE = 0b0100011
BRANCH = 0b1100011

# x86-like instruction opcodes
MOV_IMM = 0b1000000  # move immediate to register (like x86 mov)
CALL = 0b1000001     # call instruction (like x86 callq)
JMP = 0b1000010      # jump instruction (like x86 jmp)
RET = 0b1000011      # return instruction (like x86 ret)
PUSH = 0b1000100     # push to stack
POP = 0b1000101      # pop from stack

# alu operations
ALU_ADD = 0
ALU_SUB = 1
ALU_AND = 2
ALU_OR = 3
ALU_XOR = 4
ALU_SLL = 5
ALU_SRL = 6
ALU_SRA = 7
ALU_SLT = 8
ALU_SLTU = 9
ALU_MOV = 10         # move operation
ALU_CALL = 11        # call operation
ALU_JMP = 12         # jump operation
ALU_RET = 13         # return operation
ALU_NAND = 14        # nand operation

@block
def memory(clk, mem_read_enable, mem_write_enable, mem_address, mem_write_data, mem_read_data, size=1024):
    """
    @brief: data memory for the cpu
    @param clk: clock signal
    @param mem_read_enable: memory read enable
    @param mem_write_enable: memory write enable
    @param mem_address: memory address
    @param mem_write_data: data to write to memory
    @param mem_read_data: data read from memory
    @param size: memory size
    """
    mem_array = [Signal(intbv(0)[64:]) for _ in range(size)]

    @always_comb
    def read_logic():
        if mem_read_enable and 0 <= mem_address and mem_address < size:
            mem_read_data.next = mem_array[mem_address[10:0]]
        else:
            mem_read_data.next = 0

    @always_seq(clk.posedge, reset=None)
    def write_logic():
        if mem_write_enable and 0 <= mem_address and mem_address < size:
            mem_array[mem_address[10:0]].next = mem_write_data

    return read_logic, write_logic

@block
def instruction_memory(pc, instruction, program=None, rom_size=32):
    """
    @brief: instruction memory (rom)
    @param pc: program counter
    @param instruction: current instruction
    @param program: program to execute (optional, defaults to nops)
    @param rom_size: size of the ROM (default 32 instructions)
    """
    # For synthesis compatibility, the ROM must be defined at elaboration time
    # We'll use the program parameter directly, assuming it's already processed
    # by the calling code to be a tuple of the correct size

    # If no program is provided, default to all NOPs
    if program is None:
        rom = tuple([0x00000013] * rom_size)
    else:
        rom = program  # Caller must ensure it's a tuple of correct size

    @always_comb
    def read_instr():
        addr = (pc - 4) // 4
        if addr < rom_size and addr >= 0:
            instruction.next = rom[addr]
        else:
            instruction.next = 0x00000013

    return read_instr

@block
def cpu(clk, reset, pc_out, program=None, reg_read_port1=None, reg_read_port2=None,
        reg_addr1=None, reg_addr2=None, reg_out1=None, reg_out2=None):
    """
    @brief: main cpu core
    @param clk: clock signal
    @param reset: reset signal
    @param pc_out: program counter output
    @param program: program to execute (optional, defaults to nops)
    @param reg_read_port1: optional register read port 1 control
    @param reg_read_port2: optional register read port 2 control
    @param reg_addr1: optional register address 1 for monitoring
    @param reg_addr2: optional register address 2 for monitoring
    @param reg_out1: optional register output 1 for monitoring
    @param reg_out2: optional register output 2 for monitoring
    """
    pc_reg = Signal(intbv(4)[64:])

    instr_reg = Signal(intbv(0)[32:])

    rs1_addr = Signal(intbv(0)[5:])
    rs2_addr = Signal(intbv(0)[5:])
    rd_addr = Signal(intbv(0)[5:])
    rs1_data = Signal(intbv(0)[64:])
    rs2_data = Signal(intbv(0)[64:])
    reg_write_data = Signal(intbv(0)[64:])
    reg_write_enable = Signal(bool(0))

    immediate = Signal(intbv(0)[64:])

    alu_op = Signal(intbv(0)[4:])
    alu_result = Signal(intbv(0)[64:])
    alu_src_a = Signal(intbv(0)[64:])
    alu_src_b = Signal(intbv(0)[64:])

    mem_read_data = Signal(intbv(0)[64:])
    mem_write_data = Signal(intbv(0)[64:])
    mem_address = Signal(intbv(0)[64:])
    mem_write_enable = Signal(bool(0))
    mem_read_enable = Signal(bool(0))
    mem_read = Signal(bool(0))
    mem_write = Signal(bool(0))

    alu_src = Signal(bool(0))
    mem_to_reg = Signal(intbv(0)[2:])
    reg_write = Signal(bool(0))
    branch = Signal(bool(0))
    jump = Signal(bool(0))

    # Use the program passed to the CPU constructor, default to empty if none provided
    instr_mem = instruction_memory(pc_reg, instr_reg, program)

    # Instantiate the register file with only the required connections
    # Skip the optional monitoring parameters to avoid synthesis issues
    rf = regfile(clk, reg_write, rs1_addr, rs2_addr, rd_addr, reg_write_data, rs1_data, rs2_data)
    alu_inst = alu(alu_src_a, alu_src_b, alu_op, alu_result)
    mem = memory(clk, mem_read_enable, mem_write_enable, mem_address, mem_write_data, mem_read_data)

    @always_comb
    def decode():
        opcode = instr_reg[7:0]

        funct7 = instr_reg[32:25]
        funct3 = instr_reg[15:12]
        rs1_addr.next = instr_reg[20:15]
        rs2_addr.next = instr_reg[25:20]
        rd_addr.next = instr_reg[12:7]

        alu_op.next = 0
        alu_src.next = 0
        mem_to_reg.next = 0
        reg_write.next = 0
        mem_read.next = 0
        mem_write.next = 0
        branch.next = 0
        jump.next = 0  # Enable jump control signal

        if opcode == R_TYPE:
            reg_write.next = 1
            alu_src.next = 0

            if funct3 == 0:
                if funct7 == 0:
                    alu_op.next = ALU_ADD
                elif funct7 == 0b0100000:
                    alu_op.next = ALU_SUB
            elif funct3 == 1:
                alu_op.next = ALU_SLL
            elif funct3 == 2:
                alu_op.next = ALU_SLT
            elif funct3 == 3:
                alu_op.next = ALU_SLTU
            elif funct3 == 4:
                alu_op.next = ALU_XOR
            elif funct3 == 5:
                if funct7 == 0:
                    alu_op.next = ALU_SRL
                elif funct7 == 0b0100000:
                    alu_op.next = ALU_SRA
            elif funct3 == 6:
                alu_op.next = ALU_OR
            elif funct3 == 7:
                if funct7 == 0b0000001:
                    alu_op.next = ALU_NAND  # nawfeel (nand) operation
                else:
                    alu_op.next = ALU_AND   # regular and operation

        elif opcode == I_TYPE:
            reg_write.next = 1
            alu_src.next = 1

            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:20]
            immediate.next = imm_val.signed()

            if funct3 == 0:
                alu_op.next = ALU_ADD
            elif funct3 == 2:
                alu_op.next = ALU_SLT
            elif funct3 == 3:
                alu_op.next = ALU_SLTU
            elif funct3 == 4:
                alu_op.next = ALU_XOR
            elif funct3 == 6:
                alu_op.next = ALU_OR
            elif funct3 == 7:
                alu_op.next = ALU_AND
            elif funct3 == 1:
                alu_op.next = ALU_SLL
            elif funct3 == 5:
                if instr_reg[31:25] == 0:
                    alu_op.next = ALU_SRL
                elif instr_reg[31:25] == 0b0100000:
                    alu_op.next = ALU_SRA

        elif opcode == LOAD:
            reg_write.next = 1
            alu_src.next = 1
            mem_read.next = 1
            mem_to_reg.next = 1

            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:20]
            immediate.next = imm_val.signed()

        elif opcode == STORE:
            mem_write.next = 1
            alu_src.next = 1

            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:7]
            immediate.next = imm_val.signed()

        elif opcode == BRANCH:
            branch.next = 1

        # handle extended x86-like instructions
        elif opcode == MOV_IMM:  # move immediate to register (like x86 mov)
            reg_write.next = 1
            alu_src.next = 1
            alu_op.next = ALU_MOV

            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:20]
            immediate.next = imm_val.signed()

        elif opcode == CALL:  # call instruction (like x86 callq)
            reg_write.next = 1  # write return address to link register
            alu_op.next = ALU_CALL
            jump.next = 1  # enable jump to target address
            rd_addr.next = 1  # write return address to x1 (link register)
            alu_src.next = 1  # use immediate for jump target calculation

            # calculate target address from immediate (pc-relative)
            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:20]
            immediate.next = imm_val.signed()

        elif opcode == JMP:  # jump instruction (like x86 jmp)
            jump.next = 1  # enable jump to target address
            alu_op.next = ALU_JMP
            alu_src.next = 1  # use immediate as second operand

            # calculate target address from immediate (pc-relative)
            imm_val = intbv(0)[64:]
            imm_val[:] = instr_reg[32:20]
            immediate.next = imm_val.signed()

        elif opcode == RET:  # return instruction (like x86 ret)
            jump.next = 1  # enable jump to return address
            alu_op.next = ALU_RET
            rs1_addr.next = 1  # use x1 as link register for return address

    @always_comb
    def alu_source_mux():
        alu_src_a.next = rs1_data
        if alu_src:
            alu_src_b.next = immediate
        else:
            alu_src_b.next = rs2_data

        # for jumps and calls, we need pc + immediate for pc-relative addressing
        if jump and (alu_op == ALU_JMP or alu_op == ALU_CALL):
            alu_src_a.next = pc_reg  # use current pc as first operand for jumps/calls
            alu_src_b.next = immediate  # use immediate as second operand

    @always_comb
    def writeback_mux():
        if mem_to_reg == 1:
            reg_write_data.next = mem_read_data
        else:
            reg_write_data.next = alu_result

    @always_comb
    def memory_control():
        mem_read_enable.next = mem_read
        mem_write_enable.next = mem_write
        mem_address.next = alu_result
        mem_write_data.next = rs2_data

    @always_seq(clk.posedge, reset=None)
    def pc_update():
        #reset is always a valid signal
        if reset and reset.val:
            pc_reg.next = 4
        elif jump: 
            if alu_op == ALU_CALL:
                # for call, target is pc + immediate (stored in immediate signal)
                pc_reg.next = pc_reg + immediate
            elif alu_op == ALU_JMP:
                # for jmp, target is pc + immediate (stored in immediate signal)
                pc_reg.next = pc_reg + immediate
            elif alu_op == ALU_RET:
                # for ret, target is in rs1_data (return address from link register)
                pc_reg.next = rs1_data
            else:
                # for other jumps, use alu result
                pc_reg.next = alu_result
        else:
            pc_reg.next = pc_reg + 4

    @always_comb
    def output_assignments():
        pc_out.next = pc_reg

    @always_comb
    def reg_write_logic():
        reg_write_enable.next = reg_write and (rd_addr != 0)

    return decode, alu_source_mux, writeback_mux, memory_control, pc_update, output_assignments, reg_write_logic, instr_mem, rf, alu_inst, mem

# helper functions to encode x86-like instructions
def movb(rd, imm):
    """encode movb instruction: move byte immediate to register"""
    # i-type format: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
    # for mov_imm: rs1=0, funct3=0, opcode=0x40
    return ((imm & 0xFF) << 20) | (0 << 15) | (0 << 12) | ((rd & 0x1F) << 7) | 0x40

def movl(rd, imm):
    """encode movl instruction: move long immediate to register"""
    # i-type format: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
    # for mov_imm: rs1=0, funct3=0, opcode=0x40
    return ((imm & 0xFFF) << 20) | (0 << 15) | (0 << 12) | ((rd & 0x1F) << 7) | 0x40

def callq(target):
    """encode callq instruction: call function at target address"""
    # i-type format: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
    # for call: rs1=0, funct3=0, opcode=0x41
    return ((target & 0xFFF) << 20) | (0 << 15) | (0 << 12) | (0 << 7) | 0x41

def jmp(imm):
    """encode jmp instruction: unconditional jump"""
    # i-type format: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
    # for jmp: rs1=0, funct3=0, opcode=0x42
    return ((imm & 0xFFF) << 20) | (0 << 15) | (0 << 12) | (0 << 7) | 0x42

def ret():
    """encode ret instruction: return from function"""
    # i-type format: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
    # for ret: rs1=1 (use x1 as link register), funct3=0, opcode=0x43
    return (0 << 20) | (1 << 15) | (0 << 12) | (0 << 7) | 0x43

@block
def riscv_cpu_top(clk, reset, pc_out, program=None, reg_addr1=None, reg_addr2=None, reg_out1=None, reg_out2=None):
    """
    @brief: top-level cpu module
    @param clk: clock signal
    @param reset: reset signal
    @param pc_out: program counter output
    @param program: program to execute (optional, defaults to nops)
    @param reg_addr1: optional register address 1 for monitoring
    @param reg_addr2: optional register address 2 for monitoring
    @param reg_out1: optional register output 1 for monitoring
    @param reg_out2: optional register output 2 for monitoring
    """
    cpu_inst = cpu(clk, reset, pc_out, program, reg_addr1=reg_addr1, reg_addr2=reg_addr2,
                   reg_out1=reg_out1, reg_out2=reg_out2)
    return cpu_inst
