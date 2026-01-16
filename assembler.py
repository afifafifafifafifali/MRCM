
"""
CPU Assembler for 64-bit RISC CPU with extended x86-like instructions

This assembler converts human-readable assembly code into machine code
that can be directly used by the CPU simulator.
"""

import sys
import re
from typing import List, Dict, Tuple

class Assembler:
    def __init__(self):
        
        self.opcodes = {
            
            'AFIF': {'type': 'R', 'opcode': 0b0110011, 'funct3': 0, 'funct7': 0},
            'ADD': {'type': 'R', 'opcode': 0b0110011, 'funct3': 0, 'funct7': 0},
            'SUB': {'type': 'R', 'opcode': 0b0110011, 'funct3': 0, 'funct7': 0b0100000},
            'AND': {'type': 'R', 'opcode': 0b0110011, 'funct3': 7, 'funct7': 0},
            'OR': {'type': 'R', 'opcode': 0b0110011, 'funct3': 6, 'funct7': 0},
            'XOR': {'type': 'R', 'opcode': 0b0110011, 'funct3': 4, 'funct7': 0},
            'NAWFEEL': {'type': 'R', 'opcode': 0b0110011, 'funct3': 7, 'funct7': 0b0000001}, # just nand
            'SLL': {'type': 'R', 'opcode': 0b0110011, 'funct3': 1, 'funct7': 0},
            'SRL': {'type': 'R', 'opcode': 0b0110011, 'funct3': 5, 'funct7': 0},
            'SRA': {'type': 'R', 'opcode': 0b0110011, 'funct3': 5, 'funct7': 0b0100000},
            'SLT': {'type': 'R', 'opcode': 0b0110011, 'funct3': 2, 'funct7': 0},
            'SLTU': {'type': 'R', 'opcode': 0b0110011, 'funct3': 3, 'funct7': 0},
            
            
            'ADDI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0},
            'ANDI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 7},
            'ORI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 6},
            'XORI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 4},
            'SLLI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 1},
            'SRLI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 5},
            'SRAI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 5},  # Same as SRLI but with different funct7
            'SLTI': {'type': 'I', 'opcode': 0b0010011, 'funct3': 2},
            'SLTIU': {'type': 'I', 'opcode': 0b0010011, 'funct3': 3},
            
            # Load/Store instructions
            'LW': {'type': 'I', 'opcode': 0b0000011, 'funct3': 2},
            'SW': {'type': 'S', 'opcode': 0b0100011, 'funct3': 2},
            
            # Branch instructions
            'BEQ': {'type': 'B', 'opcode': 0b1100011, 'funct3': 0},
            'BNE': {'type': 'B', 'opcode': 0b1100011, 'funct3': 1},
            
            # Extended x86-like instructions
            'MOVB': {'type': 'I', 'opcode': 0b1000000, 'funct3': 0},  # Move byte immediate
            'MOVL': {'type': 'I', 'opcode': 0b1000000, 'funct3': 0},  # Move long immediate
            'CALLQ': {'type': 'I', 'opcode': 0b1000001, 'funct3': 0}, # Call instruction
            'JMP': {'type': 'I', 'opcode': 0b1000010, 'funct3': 0},   # Jump instruction
            'RET': {'type': 'I', 'opcode': 0b1000011, 'funct3': 0},   # Return instruction
            'NOP': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0},   # NOP is ADDI x0, x0, 0
        }
        
        self.registers = {
            'x0': 0, 'x1': 1, 'x2': 2, 'x3': 3, 'x4': 4, 'x5': 5, 'x6': 6, 'x7': 7,
            'x8': 8, 'x9': 9, 'x10': 10, 'x11': 11, 'x12': 12, 'x13': 13, 'x14': 14, 'x15': 15,
            'x16': 16, 'x17': 17, 'x18': 18, 'x19': 19, 'x20': 20, 'x21': 21, 'x22': 22, 'x23': 23,
            'x24': 24, 'x25': 25, 'x26': 26, 'x27': 27, 'x28': 28, 'x29': 29, 'x30': 30, 'x31': 31,
        }

        
        self.labels = {}
        self.data_segments = {}  # Store data segments defined with DB
        self.data_segment_addresses = {}  # Store addresses of data segments
        self.pending_labels = []

    def parse_register(self, reg_str: str) -> int:
        """Parse register string and return register number."""
        reg_str = reg_str.strip().lower()
        if reg_str.startswith('x') and reg_str[1:].isdigit():
            num = int(reg_str[1:])
            if 0 <= num <= 31:
                return num
        elif reg_str in self.registers:
            return self.registers[reg_str]
        else:
            raise ValueError(f"Invalid register: {reg_str}")

    def parse_immediate(self, imm_str: str) -> int:
        """Parse immediate value string and return integer."""
        imm_str = imm_str.strip()
        if imm_str.lower().startswith('0x'):
            return int(imm_str, 16)
        elif imm_str.isdigit() or (imm_str.startswith('-') and imm_str[1:].isdigit()):
            return int(imm_str)
        else:
            raise ValueError(f"Invalid immediate value: {imm_str}")

    def encode_r_type(self, instr_info: Dict, rd: int, rs1: int, rs2: int) -> int:
        """Encode R-type instruction."""
        funct7 = instr_info.get('funct7', 0)
        funct3 = instr_info['funct3']
        opcode = instr_info['opcode']
        
        # [31:25]funct7 [24:20]rs2 [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
        instruction = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        return instruction

    def encode_i_type(self, instr_info: Dict, rd: int, rs1: int, imm: int) -> int:
        """Encode I-type instruction."""
        funct3 = instr_info['funct3']
        opcode = instr_info['opcode']
        
        #  special cases niggas
        if instr_info.get('name') == 'SRAI':
            funct7 = 0b0100000
            imm &= 0x1F  
            instruction = (funct7 << 25) | (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        elif instr_info.get('name') in ['SLLI', 'SRLI']:
            imm &= 0x3F  # Only lower 6 bits for 64-bit registers
            instruction = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        else:
            # ahh I-type opcodes: [31:20]imm [19:15]rs1 [14:12]funct3 [11:7]rd [6:0]opcode
            imm &= 0xFFF  # sign-extend to 12 bits
            instruction = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        
        return instruction

    def encode_s_type(self, instr_info: Dict, rs1: int, rs2: int, imm: int) -> int:
        """Encode S-type instruction."""
        funct3 = instr_info['funct3']
        opcode = instr_info['opcode']
        
        imm &= 0xFFF  # Sign-extend to 12 bits
        imm_high = (imm >> 5) & 0x7F  # Bits [11:5]
        imm_low = imm & 0x1F           # Bits [4:0]
        
        # [31:25]imm[11:5] [24:20]rs2 [19:15]rs1 [14:12]funct3 [11:7]imm[4:0] [6:0]opcode
        instruction = (imm_high << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_low << 7) | opcode
        return instruction

    def encode_b_type(self, instr_info: Dict, rs1: int, rs2: int, imm: int) -> int:
        """Encode B-type instruction."""
        funct3 = instr_info['funct3']
        opcode = instr_info['opcode']
        
        imm &= 0x1FFE  # 12 bits total, bit 0 is always 0
        
        imm_12 = (imm >> 11) & 1      # Bit 12
        imm_10_5 = (imm >> 1) & 0x3F  # Bits [10:5]
        imm_4_1 = (imm >> 5) & 0xF    # Bits [4:1]
        imm_11 = (imm >> 10) & 1      # Bit 11
        
        # [31]imm[12] [30:25]imm[10:5] [24:20]rs2 [19:15]rs1 [14:12]funct3 [11:8]imm[4:1] [7]imm[11] [6:0]opcode
        instruction = (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | \
                      (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode
        return instruction

    def assemble_line(self, line: str) -> int:
        """Assemble a single line of assembly code."""
        # Remove comments and strip whitespace
        line = re.sub(r'#.*$', '', line).strip()
        if not line:
            return None

        # split instruction and operands
        parts = line.split(None, 1)
        if not parts:
            return None

        instr_name = parts[0].upper()
        operands = parts[1] if len(parts) > 1 else ""

        # handle NOP specially
        if instr_name == 'NOP':
            return self.encode_i_type(
                {'type': 'I', 'opcode': 0b0010011, 'funct3': 0},
                rd=0, rs1=0, imm=0
            )

        # get instruction info
        if instr_name not in self.opcodes:
            raise ValueError(f"Unknown instruction: {instr_name}")

        instr_info = self.opcodes[instr_name]

        # Parse operands based on instruction type
        if instr_info['type'] == 'R':
            # Format: RD, RS1, RS2
            ops = [op.strip() for op in operands.split(',')]
            if len(ops) != 3:
                raise ValueError(f"R-type instruction {instr_name} requires 3 operands")
            rd = self.parse_register(ops[0])
            rs1 = self.parse_register(ops[1])
            rs2 = self.parse_register(ops[2])
            return self.encode_r_type(instr_info, rd, rs1, rs2)

        elif instr_info['type'] in ['I', 'MOVB', 'MOVL', 'CALLQ', 'JMP', 'RET']:
            # Format: RD, RS1, IMM  or  RD, IMM  or  RS1, IMM
            ops = [op.strip() for op in operands.split(',')]
            if instr_name in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLLI', 'SRLI', 'SRAI', 'SLTI', 'SLTIU']:
                if len(ops) != 3:
                    raise ValueError(f"I-type instruction {instr_name} requires 3 operands")
                rd = self.parse_register(ops[0])
                rs1 = self.parse_register(ops[1])
                imm = self.parse_immediate(ops[2])
                return self.encode_i_type(instr_info, rd, rs1, imm)
            elif instr_name == 'LW':
                # LW RD, IMM(RS1) format
                if '(' in operands and ')' in operands:
                    # parse "rd, imm(rs1)" format
                    match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                    if not match:
                        raise ValueError(f"Invalid operand format for {instr_name}")
                    rd_str, imm_str, rs1_str = match.groups()
                    rd = self.parse_register(rd_str.strip())
                    imm = self.parse_immediate(imm_str.strip())
                    rs1 = self.parse_register(rs1_str.strip())
                    return self.encode_i_type(instr_info, rd, rs1, imm)
                else:
                    raise ValueError(f"Invalid operand format for {instr_name}")
            elif instr_name in ['MOVB', 'MOVL']:
                # MOVB/MOVL RD, IMM
                if len(ops) != 2:
                    raise ValueError(f"{instr_name} requires 2 operands: RD, IMM")
                rd = self.parse_register(ops[0])
                imm = self.parse_immediate(ops[1])
                return self.encode_i_type(instr_info, rd, 0, imm)  # rs1 = 0 for move immediate
            elif instr_name in ['CALLQ', 'JMP']:
                # CALLQ/JMP IMM
                if len(ops) != 1:
                    raise ValueError(f"{instr_name} requires 1 operand: IMM")
                imm = self.parse_immediate(ops[0])
                # for PC-relative jumps, the immediate is the offset from current PC
                # this piece of shit will be calculated at runtime by the CPU: PC + offset
                return self.encode_i_type(instr_info, 0, 0, imm)  # rd=0, rs1=0 for jumps
            elif instr_name == 'RET':
                # RET (no operands)
                return self.encode_i_type(instr_info, 0, 1, 0)  # rd=0, rs1=1 (use x1 as link register), imm=0
            else:
                # LW RD, IMM(RS1)
                if '(' in operands and ')' in operands:
                    # parse "rd, imm(rs1)" format
                    match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                    if not match:
                        raise ValueError(f"Invalid operand format for {instr_name}")
                    rd_str, imm_str, rs1_str = match.groups()
                    rd = self.parse_register(rd_str.strip())
                    imm = self.parse_immediate(imm_str.strip())
                    rs1 = self.parse_register(rs1_str.strip())
                    return self.encode_i_type(instr_info, rd, rs1, imm)
                else:
                    if len(ops) != 3:
                        raise ValueError(f"I-type instruction {instr_name} requires 3 operands")
                    rd = self.parse_register(ops[0])
                    rs1 = self.parse_register(ops[1])
                    imm = self.parse_immediate(ops[2])
                    return self.encode_i_type(instr_info, rd, rs1, imm)

        elif instr_info['type'] == 'S':
            # format: RS2, IMM(RS1)  or  RS2, RS1, IMM
            if '(' in operands and ')' in operands:
                # Parse "rs2, imm(rs1)" format
                match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                if not match:
                    raise ValueError(f"Invalid operand format for {instr_name}")
                rs2_str, imm_str, rs1_str = match.groups()
                rs2 = self.parse_register(rs2_str.strip())
                imm = self.parse_immediate(imm_str.strip())
                rs1 = self.parse_register(rs1_str.strip())
                return self.encode_s_type(instr_info, rs1, rs2, imm)
            else:
                ops = [op.strip() for op in operands.split(',')]
                if len(ops) != 3:
                    raise ValueError(f"S-type instruction {instr_name} requires 3 operands")
                rs2 = self.parse_register(ops[0])
                rs1 = self.parse_register(ops[1])
                imm = self.parse_immediate(ops[2])
                return self.encode_s_type(instr_info, rs1, rs2, imm)

        elif instr_info['type'] == 'B':
            # Format: RS1, RS2, IMM
            ops = [op.strip() for op in operands.split(',')]
            if len(ops) != 3:
                raise ValueError(f"B-type instruction {instr_name} requires 3 operands")
            rs1 = self.parse_register(ops[0])
            rs2 = self.parse_register(ops[1])
            imm = self.parse_immediate(ops[2])
            return self.encode_b_type(instr_info, rs1, rs2, imm)

        else:
            raise ValueError(f"Unsupported instruction type: {instr_info['type']}")

    def assemble(self, asm_code: str) -> List[int]:
        """Assemble assembly code into machine code."""
        lines = asm_code.split('\n')
        instructions = []
        current_instruction_address = 4  # Program starts at address 4
        current_data_address = 0x1000   # Data starts at address 0x1000

        #  identify labels and data segments
        for line_num, line in enumerate(lines, 1):
            clean_line = re.sub(r'#.*$', '', line).strip()
            if not clean_line:
                continue

            if clean_line.endswith(':'):
                label_name = clean_line[:-1].strip()
                next_line_idx = line_num
                if next_line_idx < len(lines):
                    next_line = re.sub(r'#.*$', '', lines[next_line_idx]).strip()
                    if next_line and re.search(r'\bDB\b', next_line.upper()):
                        self.data_segment_addresses[label_name] = current_data_address
                    else:
                        self.labels[label_name] = current_instruction_address
                continue

            db_match = re.search(r'\bDB\b', clean_line.upper())
            if db_match:
                continue

            if clean_line and not clean_line.startswith('#'):
                current_instruction_address += 4  # each instruction is 4 bytes

        current_instruction_address = 4
        current_data_address = 0x1000

        for line_num, line in enumerate(lines, 1):
            clean_line = re.sub(r'#.*$', '', line).strip()
            if not clean_line:
                continue

            if clean_line.endswith(':'):
                continue

            db_match = re.search(r'\bDB\b', clean_line.upper())
            if db_match:
                byte_values = self.process_db_directive(clean_line)
                continue

            try:
                instruction = self.assemble_line_with_labels(line, current_instruction_address)
                if instruction != None:
                    instructions.append(instruction)
                    current_instruction_address += 4
            except Exception as e:
                raise RuntimeError(f"Line {line_num}: {str(e)}")

        return instructions

    def process_db_directive(self, line: str):
        """Process DB (define byte) directive."""
        parts = re.split(r'\bDB\b', line, flags=re.IGNORECASE)
        if len(parts) < 2:
            return []

        label_part = parts[0].strip()
        current_label = None
        if label_part.endswith(':'):
            current_label = label_part[:-1].strip()

        values_part = parts[1].strip()
        values_part = re.split(r'\s+#', values_part)[0].strip()

        values = [val.strip() for val in values_part.split(',')]

        byte_values = []
        for val in values:
            val = val.strip()
            if val.lower().startswith('0x'):
                byte_values.append(int(val, 16))
            elif val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                byte_values.append(int(val))
            elif val.startswith('"') and val.endswith('"'):
                string_val = val[1:-1]  # remove quotes
                for char in string_val:
                    byte_values.append(ord(char))
            else:
                byte_values.append(val)

        if current_label:
            self.data_segments[current_label] = byte_values

        return byte_values

    def resolve_label(self, label: str, current_address: int) -> int:
        """Resolve a label to its address, calculating PC-relative offset if needed."""
        if label in self.labels:
            target_address = self.labels[label]
            # for PC-relative addressing: offset = target - current
            offset = target_address - current_address
            return offset
        else:
            raise ValueError(f"Undefined label: {label}")

    def assemble_line_with_labels(self, line: str, current_address: int) -> int:
        """Assemble a single line of assembly code with label resolution."""
        # remove comments and strip whitespace
        line = re.sub(r'#.*$', '', line).strip()
        if not line:
            return None

        # split instruction and operands
        parts = line.split(None, 1)
        if not parts:
            return None

        instr_name = parts[0].upper()
        operands = parts[1] if len(parts) > 1 else ""

        # handle NOP specially
        if instr_name == 'NOP':
            return self.encode_i_type(
                {'type': 'I', 'opcode': 0b0010011, 'funct3': 0},
                rd=0, rs1=0, imm=0
            )

        # get instruction info
        if instr_name not in self.opcodes:
            raise ValueError(f"Unknown instruction: {instr_name}")

        instr_info = self.opcodes[instr_name]

        # parse operands based on instruction type
        if instr_info['type'] == 'R':
            # format: RD, RS1, RS2
            ops = [op.strip() for op in operands.split(',')]
            if len(ops) != 3:
                raise ValueError(f"R-type instruction {instr_name} requires 3 operands")
            rd = self.parse_register(ops[0])
            rs1 = self.parse_register(ops[1])
            rs2 = self.parse_register(ops[2])
            return self.encode_r_type(instr_info, rd, rs1, rs2)

        elif instr_info['type'] in ['I', 'MOVB', 'MOVL', 'CALLQ', 'JMP', 'RET']:
            # handle instructions that might use labels
            ops = [op.strip() for op in operands.split(',')]

            if instr_name in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLLI', 'SRLI', 'SRAI', 'SLTI', 'SLTIU']:
                if len(ops) != 3:
                    raise ValueError(f"I-type instruction {instr_name} requires 3 operands")
                rd = self.parse_register(ops[0])
                rs1 = self.parse_register(ops[1])
                imm = self.parse_immediate(ops[2])
                return self.encode_i_type(instr_info, rd, rs1, imm)
            elif instr_name == 'LW':
                # LW RD, IMM(RS1) format
                if '(' in operands and ')' in operands:
                    # Parse "rd, imm(rs1)" format
                    match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                    if not match:
                        raise ValueError(f"Invalid operand format for {instr_name}")
                    rd_str, imm_str, rs1_str = match.groups()
                    rd = self.parse_register(rd_str.strip())
                    imm = self.parse_immediate(imm_str.strip())
                    rs1 = self.parse_register(rs1_str.strip())
                    return self.encode_i_type(instr_info, rd, rs1, imm)
                else:
                    raise ValueError(f"Invalid operand format for {instr_name}")
            elif instr_name in ['MOVB', 'MOVL']:
                # MOVB/MOVL RD, IMM
                if len(ops) != 2:
                    raise ValueError(f"{instr_name} requires 2 operands: RD, IMM")
                rd = self.parse_register(ops[0])
                imm = self.parse_immediate(ops[1])
                return self.encode_i_type(instr_info, rd, 0, imm)  # rs1 = 0 for move immediate
            elif instr_name in ['CALLQ', 'JMP']:
                # CALLQ/JMP LABEL or CALLQ/JMP IMMEDIATE
                if len(ops) != 1:
                    raise ValueError(f"{instr_name} requires 1 operand: LABEL or IMMEDIATE")

                operand = ops[0].strip()
                # see if it's a label (contains letters and underscores)
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', operand):
                    #  a label, resolve it to PC-relative offset
                    imm = self.resolve_label(operand, current_address)
                else:
                    # a numeric immediate
                    imm = self.parse_immediate(operand)

                # for PC-relative jumps/calls, the immediate is the offset from current PC
                return self.encode_i_type(instr_info, 0, 0, imm)  # rd=0, rs1=0 for jumps/calls
            elif instr_name == 'RET':
                # RET (no operands)
                return self.encode_i_type(instr_info, 0, 1, 0)  # rd=0, rs1=1 (use x1 as link register), imm=0
            else:
                # handle other I-type instructions with memory format
                if '(' in operands and ')' in operands:
                    # parse "rd, imm(rs1)" format
                    match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                    if not match:
                        raise ValueError(f"Invalid operand format for {instr_name}")
                    rd_str, imm_str, rs1_str = match.groups()
                    rd = self.parse_register(rd_str.strip())
                    imm = self.parse_immediate(imm_str.strip())
                    rs1 = self.parse_register(rs1_str.strip())
                    return self.encode_i_type(instr_info, rd, rs1, imm)
                else:
                    if len(ops) != 3:
                        raise ValueError(f"I-type instruction {instr_name} requires 3 operands")
                    rd = self.parse_register(ops[0])
                    rs1 = self.parse_register(ops[1])
                    imm = self.parse_immediate(ops[2])
                    return self.encode_i_type(instr_info, rd, rs1, imm)

        elif instr_info['type'] == 'S':
            # format: RS2, IMM(RS1)  or  RS2, RS1, IMM
            if '(' in operands and ')' in operands:
                # parse "rs2, imm(rs1)" format
                match = re.match(r'([^,]+),\s*([^(]+)\(([^)]+)\)', operands)
                if not match:
                    raise ValueError(f"Invalid operand format for {instr_name}")
                rs2_str, imm_str, rs1_str = match.groups()
                rs2 = self.parse_register(rs2_str.strip())
                imm = self.parse_immediate(imm_str.strip())
                rs1 = self.parse_register(rs1_str.strip())
                return self.encode_s_type(instr_info, rs1, rs2, imm)
            else:
                ops = [op.strip() for op in operands.split(',')]
                if len(ops) != 3:
                    raise ValueError(f"S-type instruction {instr_name} requires 3 operands")
                rs2 = self.parse_register(ops[0])
                rs1 = self.parse_register(ops[1])
                imm = self.parse_immediate(ops[2])
                return self.encode_s_type(instr_info, rs1, rs2, imm)

        elif instr_info['type'] == 'B':
            # format: RS1, RS2, LABEL or RS1, RS2, IMMEDIATE
            ops = [op.strip() for op in operands.split(',')]
            if len(ops) != 3:
                raise ValueError(f"B-type instruction {instr_name} requires 3 operands")
            rs1 = self.parse_register(ops[0])
            rs2 = self.parse_register(ops[1])

            # check if the third operand is a label
            target_operand = ops[2]
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', target_operand):
                #  a label, resolve it to PC-relative offset
                imm = self.resolve_label(target_operand, current_address)
            else:
                #  a numeric immediate
                imm = self.parse_immediate(target_operand)

            return self.encode_b_type(instr_info, rs1, rs2, imm)

        else:
            raise ValueError(f"Unsupported instruction type: {instr_info['type']}")

    def generate_c_array(self, instructions: List[int]) -> str:
        """Generate C-style array from instructions."""
        c_array = "uint32_t program[] = {\n"
        for i, instr in enumerate(instructions):
            c_array += f"    0x{instr:08x},  // Instruction {i}\n"
        c_array += "};\n"
        return c_array

    def generate_python_list(self, instructions: List[int]) -> str:
        """Generate Python list from instructions."""
        python_list = "(\n"
        for i, instr in enumerate(instructions):
            python_list += f"    0x{instr:08x},  \n"
        python_list += f")+(0x00000013,) * {32-len(instructions)}"
        return python_list


def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <assembly_file.asm>")
        print("\nExample assembly file format:")
        print("# Add comments with #")
        print("ADDI x1, x0, 5    # Load 5 into x1")
        print("ADDI x2, x0, 13   # Load 13 into x2")
        print("ADD x3, x1, x2    # Add x1 and x2, store in x3")
        print("SLLI x4, x3, 1    # Shift left by 1 (multiply by 2)")
        print("SRLI x5, x4, 1    # Shift right by 1 (divide by 2)")
        print("NOP               # No operation")
        return

    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            asm_code = f.read()
        
        assembler = Assembler()
        instructions = assembler.assemble(asm_code)
        
        print("#----- MRCM 64-bit RISC-like CPU assembled program-----")
        print(assembler.generate_python_list(instructions))
        print()
        print("#-----END OF ASSEMBLED INSTRUCTIONS-----")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
    # ADOLF AEAE
