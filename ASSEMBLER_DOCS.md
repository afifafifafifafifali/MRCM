# CPU Assembler Documentation

## Overview
The CPU Assembler is a tool that converts human-readable assembly code into machine code that can be executed by the 64-bit RISC CPU simulator. It supports both standard RISC-V instructions and extended x86-like instructions.

## Usage
```bash
python assembler.py <assembly_file.asm>
```

The assembler will output a Python list of 32-bit instruction values that can be directly used in the testbench.

## Assembly File Format
- Assembly files should contain one instruction per line
- Comments can be added using `#` symbol
- Instructions follow the format: `INSTRUCTION operands`
- Operands are separated by commas
- Register names can be specified as `x0`, `x1`, ..., `x31`
- Labels can be defined using `label_name:` syntax
- Data can be defined using `DB` directive

## Supported Instructions

### R-Type Instructions (Register-Register Operations)
- `ADD rd, rs1, rs2` - Add two registers
- `SUB rd, rs1, rs2` - Subtract rs2 from rs1
- `AND rd, rs1, rs2` - Bitwise AND
- `OR rd, rs1, rs2` - Bitwise OR
- `XOR rd, rs1, rs2` - Bitwise XOR
- `SLL rd, rs1, rs2` - Shift left logical
- `SRL rd, rs1, rs2` - Shift right logical
- `SRA rd, rs1, rs2` - Shift right arithmetic
- `SLT rd, rs1, rs2` - Set less than (signed)
- `SLTU rd, rs1, rs2` - Set less than unsigned
- `NAWFEEL rd, rs1, rs2` - Bitwise NAND (Not AND) operation
- `AFIF rd, rs1, rs2` - Alias for ADD operation

### I-Type Instructions (Register-Immediate Operations)
- `ADDI rd, rs1, imm` - Add immediate to register
- `ANDI rd, rs1, imm` - AND immediate with register
- `ORI rd, rs1, imm` - OR immediate with register
- `XORI rd, rs1, imm` - XOR immediate with register
- `SLLI rd, rs1, imm` - Shift left logical immediate
- `SRLI rd, rs1, imm` - Shift right logical immediate
- `SRAI rd, rs1, imm` - Shift right arithmetic immediate
- `SLTI rd, rs1, imm` - Set less than immediate (signed)
- `SLTIU rd, rs1, imm` - Set less than immediate (unsigned)
- `LW rd, imm(rs1)` - Load word from memory address rs1+imm

### S-Type Instructions (Store Operations)
- `SW rs2, imm(rs1)` - Store word to memory address rs1+imm

### B-Type Instructions (Branch Operations)
- `BEQ rs1, rs2, imm` - Branch if equal
- `BNE rs1, rs2, imm` - Branch if not equal

### Extended x86-like Instructions
- `MOVB rd, imm` - Move byte immediate to register
- `MOVL rd, imm` - Move long immediate to register
- `CALLQ label` - Call function at label address
- `JMP label` - Jump to label address
- `RET` - Return from function

### Special Instructions
- `NOP` - No operation (equivalent to ADDI x0, x0, 0)

### Data Definition Directive
- `DB value1, value2, ...` - Define byte values in memory
- `DB "string"` - Define string as ASCII bytes
- `label_name: DB ...` - Label pointing to data location

## Example Assembly Program
```
# Data section
message:
DB "Hello", 0          # Define a string followed by null terminator

numbers:
DB 1, 2, 3, 4, 5      # Define an array of numbers

# Code section
# Calculate ((5+13)*2)/2
ADDI x1, x0, 5     # Load 5 into x1
ADDI x2, x0, 13    # Load 13 into x2
ADD x3, x1, x2     # x3 = x1 + x2 = 18
SLLI x4, x3, 1     # x4 = x3 << 1 = 36 (multiply by 2)
SRLI x5, x4, 1     # x5 = x4 >> 1 = 18 (divide by 2)
NAWFEEL x6, x1, x2 # x6 = ~(x1 & x2) = NAND of x1 and x2
AFIF x7, x1, x2     # x7 = x1 + x2 (alias for ADD)
NOP                # Infinite loop
```

## Output Format
The assembler outputs a Python list of hexadecimal instruction values that can be directly assigned to the `test_program` variable in the testbench:

```python
test_program = [
    0x00500093,  # ADDI x1, x0, 5
    0x00D00113,  # ADDI x2, x0, 13
    0x002081B3,  # ADD x3, x1, x2
    0x00119213,  # SLLI x4, x3, 1
    0x00125293,  # SRLI x5, x4, 1
    0x0220f333,  # NAWFEEL x6, x1, x2 (NAND operation)
    0x002083B3,  # AFIF x7, x1, x2 (ADD operation alias)
    0x00000013,  # NOP
]
```

## Memory Layout
The assembler organizes memory as follows:
- Instructions start at address `0x4`
- Data segments start at address `0x1000`
- Each instruction is 4 bytes (32 bits)

## Register Convention
- `x0`: Always zero (hardwired to 0, cannot be modified)
- `x1-x31`: General purpose registers (64-bit values)

## Immediate Values and Labels
- Immediate values can be specified in decimal (e.g., 100) or hexadecimal (e.g., 0x64)
- Labels can be referenced in branch, call, and jump instructions
- For shift operations, immediate values represent the shift amount
- For branch operations, immediate values represent the branch offset

## Error Handling
The assembler will report line numbers and error details if there are syntax errors in the assembly code.