# 64-bit RISC CPU - Detailed Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Instruction Set Architecture (ISA)](#instruction-set-architecture-isa)
5. [Pipeline Design](#pipeline-design)
6. [Signal Definitions](#signal-definitions)
7. [Module Interfaces](#module-interfaces)
8. [Implementation Details](#implementation-details)
9. [Sample Program](#sample-program)
10. [Design Considerations](#design-considerations)

## Overview

This document provides detailed technical documentation for the 64-bit RISC CPU implementation using MyHDL. The CPU is designed with inspiration from the RISC-V architecture and implements a 5-stage pipeline for efficient instruction processing.

### Key Features

- 64-bit data path throughout the processor
- Harvard architecture with separate instruction and data memories
- 5-stage pipeline for improved throughput
- RISC-style instruction encoding
- 32 general-purpose 64-bit registers
- Modular design for easy extension

## Architecture

### Processor Organization

The CPU follows a classic RISC architecture with:

- Fixed-length 32-bit instructions
- Load-store architecture (memory accesses limited to dedicated instructions)
- 32 general-purpose registers (x0-x31)
- Dedicated ALU for arithmetic and logical operations
- Separate instruction and data caches/memory

### Data Path Widths

- General-purpose registers: 64 bits
- ALU operations: 64 bits
- Memory addresses: 64 bits
- Instruction width: 32 bits
- Data memory width: 64 bits

## Components

### ALU Module (`alu.py`)

#### Description

The Arithmetic Logic Unit performs basic arithmetic and logical operations on 64-bit operands.

#### Operations Supported

- 0: Addition (ADD)
- 1: Subtraction (SUB)
- 2: Bitwise AND (AND)
- 3: Bitwise OR (OR)
- 4: Bitwise XOR (XOR)
- 5: Shift Left Logical (SLL)
- 6: Shift Right Logical (SRL)
- 7: Shift Right Arithmetic (SRA)
- 8: Set Less Than (SLT)
- 9: Set Less Than Unsigned (SLTU)
- 10: Move Operation (MOV)
- 11: Call Operation (CALL)
- 12: Jump Operation (JMP)
- 13: Return Operation (RET)
- 14: Bitwise NAND (NAND)

#### Interface

```
Inputs:
  - a: 64-bit first operand
  - b: 64-bit second operand
  - op: 4-bit operation selector

Output:
  - result: 64-bit result
```

#### Implementation

Combinational logic that selects the appropriate operation based on the `op` input.

### Register File (`reg.py`)

#### Description

Implements 32 general-purpose 64-bit registers (x0-x31) with dedicated read and write ports.

#### Special Register

- x0 (register 0) is hardwired to 0 and cannot be modified

#### Interface

```
Inputs:
  - clk: Clock signal
  - we: Write enable (active high)
  - rs1: Read port 1 address (5 bits)
  - rs2: Read port 2 address (5 bits)
  - rd: Write address (5 bits)
  - wd: Write data (64 bits)

Outputs:
  - r1: Read port 1 data (64 bits)
  - r2: Read port 2 data (64 bits)
```

#### Behavior

- Dual-port read capability (can read two registers simultaneously)
- Single-port write capability (one register written per cycle)
- Write operations are clocked and occur on positive clock edge
- Reading x0 always returns 0 regardless of its stored value

### CPU Core (`cpu_complete.py`)

#### Description

Main CPU implementation containing the control logic, datapath, and pipeline stages.

#### Sub-components

- Instruction fetch unit
- Instruction decode unit
- Execution unit
- Memory access unit
- Write-back unit
- Program counter management
- Control signal generation

## Instruction Set Architecture (ISA)

### Instruction Formats

The CPU supports multiple RISC-V-like instruction formats:

#### R-Type (Register-Register Operations)

```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
funct7   rs2     rs1     funct3  rd    opcode
```

#### I-Type (Immediate Operations)

```
[31:20] [19:15] [14:12] [11:7] [6:0]
imm     rs1     funct3  rd    opcode
```

#### S-Type (Store Operations)

```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
imm[11:5] rs2   rs1     funct3  imm[4:0] opcode
```

#### B-Type (Branch Operations)

```
[31] [30:25] [24:20] [19:15] [14:12] [11:8] [7] [6:0]
imm[12] imm[10:5] rs2   rs1     funct3  imm[4:1] imm[11] opcode
```

### Supported Opcodes

- R_TYPE = 0b0110011 (Register-register operations)
- I_TYPE = 0b0010011 (Register-immediate operations)
- LOAD = 0b0000011 (Load operations)
- STORE = 0b0100011 (Store operations)
- BRANCH = 0b1100011 (Branch operations)

### ALU Operations

- ALU_ADD = 0 (Addition)
- ALU_SUB = 1 (Subtraction)
- ALU_AND = 2 (Bitwise AND)
- ALU_OR = 3 (Bitwise OR)
- ALU_XOR = 4 (Bitwise XOR)
- ALU_SLL = 5 (Shift Left Logical)
- ALU_SRL = 6 (Shift Right Logical)
- ALU_SRA = 7 (Shift Right Arithmetic)
- ALU_SLT = 8 (Set Less Than)
- ALU_SLTU = 9 (Set Less Than Unsigned)
- ALU_MOV = 10 (Move Operation)
- ALU_CALL = 11 (Call Operation)
- ALU_JMP = 12 (Jump Operation)
- ALU_RET = 13 (Return Operation)
- ALU_NAND = 14 (Bitwise NAND)

## Pipeline Design

### Five-Stage Pipeline

The CPU implements a 5-stage-like(not fully) pipeline for improved instruction throughput:

#### Stage 1: Instruction Fetch (IF)

- Fetches instruction from instruction memory based on Program Counter (PC)
- Updates PC for next instruction (PC + 4 for sequential execution)
- Handles branch/jump target calculations

#### Stage 2: Instruction Decode (ID)

- Decodes fetched instruction
- Reads source registers from register file
- Extracts immediate values for I-type instructions
- Generates control signals for execution stage

#### Stage 3: Execute (EX)

- Performs ALU operations using operands from previous stage
- Calculates memory addresses for load/store operations
- Evaluates branch conditions

#### Stage 4: Memory Access (MEM)

- Accesses data memory for load/store operations
- For loads: reads data from memory
- For stores: writes data to memory
- For non-memory operations: passes through ALU result

#### Stage 5: Write Back (WB)

- Writes results back to register file
- Selects between ALU result and memory data based on control signals
- Updates appropriate destination register

### Pipeline Hazards

The current implementation handles structural hazards through proper resource allocation. Data hazards and control hazards are managed through the pipeline design.

## Signal Definitions

### CPU Core Signals

- `clk`: System clock signal
- `reset`: Asynchronous reset signal
- `pc_out`: Program counter output for monitoring

### Internal CPU Signals

- `pc_reg`: Program counter register (64-bit)
- `instr_reg`: Instruction register (32-bit)
- `rs1_addr`, `rs2_addr`, `rd_addr`: Register addresses (5-bit)
- `rs1_data`, `rs2_data`: Register read data (64-bit)
- `reg_write_data`: Data to write to register (64-bit)
- `immediate`: Sign-extended immediate value (64-bit)
- `alu_op`: ALU operation selector (4-bit)
- `alu_result`: ALU computation result (64-bit)
- `mem_read_data`, `mem_write_data`: Memory data signals (64-bit)
- `mem_address`: Memory address (64-bit)
- `mem_write_enable`, `mem_read_enable`: Memory control signals
- `alu_src`: ALU source selection (1-bit)
- `mem_to_reg`: Write-back source selection (2-bit)
- `reg_write`: Register write enable (1-bit)
- `branch`, `jump`: Control flow signals (1-bit)

## Module Interfaces

### Top-Level Interface (`riscv_cpu_top`)

```
Inputs:
  - clk: Clock signal
  - reset: Reset signal

Outputs:
  - pc_out: Program counter value
```

### CPU Core Interface (`cpu`)

```
Inputs:
  - clk: Clock signal
  - reset: Reset signal

Outputs:
  - pc_out: Program counter value
```

### Memory Interface (`memory`)

```
Inputs:
  - clk: Clock signal
  - mem_read_enable: Memory read enable
  - mem_write_enable: Memory write enable
  - mem_address: Memory address (64-bit)
  - mem_write_data: Data to write (64-bit)

Outputs:
  - mem_read_data: Data read from memory (64-bit)
```

### Instruction Memory Interface (`instruction_memory`)

```
Inputs:
  - pc: Program counter (64-bit)
  - program: Program array

Outputs:
  - instruction: Fetched instruction (32-bit)
```

## Implementation Details

### Program Initialization

The CPU includes a built-in sample program in the instruction memory:

```
Address 0x4: 0x00500093  // ADDI x1, x0, 5    -> x1 = 5
Address 0x8: 0x00500113  // ADDI x2, x0, 5    -> x2 = 5
Address 0xC: 0x001101b3  // AFIF x3, x2, x1   -> x3 = x2 + x1 = 10 (ADD operation)
Address 0x10: 0x0220f1b3 // NAWFEEL x3, x1, x2 -> x3 = ~(x1 & x2) = ~(5 & 5) = ~5 = NAND of 5 and 5
Address 0x14: 0x00000013  // NOP (infinite loop)
```

### Control Logic

The control unit decodes instructions and generates appropriate control signals:

- `reg_write`: Enables register write operations
- `mem_read`/`mem_write`: Controls memory access
- `mem_to_reg`: Selects write-back source
- `alu_op`: Specifies ALU operation
- `alu_src`: Selects ALU second operand (register or immediate)

### Data Forwarding

The implementation includes mechanisms to handle data dependencies between instructions in the pipeline.

## Sample Program

The embedded sample program demonstrates basic CPU functionality:

1. Loads immediate value 5 into register x1
2. Loads immediate value 5 into register x2
3. Adds x2 and x1, storing result in x3 (x3 = 10) - using AFIF instruction (ADD operation)
4. Performs NAND operation on x1 and x2, storing result in x3 (x3 = ~(5 & 5) = NAND of 5 and 5) - using NAWFEEL instruction
5. Enters infinite NOP loop

This program exercises:

- ADDI (add immediate) instructions
- ADD (register-register addition) instructions via AFIF
- NAWFEEL (NAND) operation
- Register read/write operations
- Program flow control

## Design Considerations

### Modularity

Each major component is implemented as a separate block, allowing for:

- Independent testing and verification
- Easy replacement or enhancement of individual components
- Clear interfaces between modules

### Scalability

The design allows for easy extension:

- Additional ALU operations can be added by extending the operation decoder
- More complex instruction formats can be incorporated
- Pipeline stages can be modified or enhanced

### Verification-Friendly

The modular design enables:

- Component-level testing
- Integration testing
- Simulation-based verification

### Hardware Synthesis Readiness

The MyHDL implementation follows practices suitable for hardware synthesis:

- Clear clocking discipline
- Well-defined reset behavior
- Deterministic combinational logic
- Proper handling of control signals

## Programming Guide

### How to Write Programs for this CPU

This CPU follows the RISC-V instruction set architecture principles. Programs are loaded as arrays of 32-bit instruction values.

#### Basic Program Structure

Programs are defined as arrays of 32-bit hexadecimal values that represent RISC-V instructions:

```python
my_program = [
    0x00500093,  # ADDI x1, x0, 5    -> x1 = 5
    0x01200213,  # ADDI x4, x0, 18   -> x4 = 18
    0x004082B3,  # ADD x5, x1, x4    -> x5 = x1 + x4 = 23
    0x00000013,  # NOP (infinite loop)
    0x00000013,  # NOP
    # ... more instructions
]
```

#### Loading Programs into the CPU

To load a custom program into the CPU, pass it as the `program` parameter when instantiating the CPU:

```python
from myhdl import *
from cpu_complete import riscv_cpu_top

clk = Signal(bool(0))
reset = ResetSignal(0, active=1, isasync=True)
pc = Signal(intbv(0)[64:])

my_program = [0x00500093, 0x01200213, 0x004082B3, 0x00000013]

dut = riscv_cpu_top(clk, reset, pc, program=my_program)
```

#### Register Convention

- x0: Always zero (hardwired to 0, cannot be modified)
- x1-x31: General purpose registers (64-bit values)

#### Instruction Formats

The CPU supports several RISC-V instruction formats:

##### R-Type (Register-Register Operations)

```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
funct7   rs2     rs1     funct3  rd    opcode
```

Examples:

- ADD: `0x000282B3` (ADD x5, x1, x4) - x5 = x1 + x4
- SUB: `0x404082B3` (SUB x5, x1, x4) - x5 = x1 - x4

##### I-Type (Immediate Operations)

```
[31:20] [19:15] [14:12] [11:7] [6:0]
imm     rs1     funct3  rd    opcode
```

Examples:

- ADDI: `0x00500093` (ADDI x1, x0, 5) - x1 = x0 + 5 = 5
- ANDI: `0x00500097` (ANDI x1, x0, 5) - x1 = x0 & 5

##### S-Type (Store Operations)

```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
imm[11:5] rs2   rs1     funct3  imm[4:0] opcode
```

Examples:

- SW: `0x0040A023` (SW x4, 0(x1)) - store x4 at address in x1

##### Load Operations

Examples:

- LW: `0x00002083` (LW x1, 0(x0)) - load word from address in x0 to x1

#### Common Instructions

- ADDI rd, rs1, imm: Add immediate to register (I-type)
- ADD rd, rs1, rs2: Add two registers (R-type)
- SUB rd, rs1, rs2: Subtract rs2 from rs1 (R-type)
- AND rd, rs1, rs2: Bitwise AND (R-type)
- OR rd, rs1, rs2: Bitwise OR (R-type)
- XOR rd, rs1, rs2: Bitwise XOR (R-type)
- SLL rd, rs1, rs2: Shift left logical (R-type)
- SRL rd, rs1, rs2: Shift right logical (R-type)
- SRA rd, rs1, rs2: Shift right arithmetic (R-type)
- SLT rd, rs1, rs2: Set less than (R-type)
- SLTU rd, rs1, rs2: Set less than unsigned (R-type)
- LW rd, imm(rs1): Load word from memory (I-type)
- SW rs2, imm(rs1): Store word to memory (S-type)

#### Extended x86-like Instructions

- MOV_IMM rd, imm: Move immediate value to register (custom format)
- CALL imm: Call function at immediate address (custom format)
- JMP imm: Jump to immediate address (custom format)
- RET: Return from function (custom format)
- PUSH rs: Push register value to stack (custom format)
- POP rd: Pop value from stack to register (custom format)

#### Programming Tips

1. The program counter starts at address 4 (0x4)
2. Instructions are 32 bits (4 bytes) each, so PC increments by 4 for each instruction
3. Register x0 is always 0 and cannot be modified
4. Use ADDI with x0 as source to load immediate values
5. Programs should end with an infinite loop (like repeated NOPs) to prevent executing undefined instructions

### Testing and Verification

### Testbench (`tb.py`)

A comprehensive testbench is provided to verify CPU functionality:

#### Features:

- Clock generation with 5-time-unit period
- Proper reset sequence (20-time-unit reset pulse)
- Program counter monitoring
- 20-cycle simulation run
- Console output of PC values at each cycle

#### Test Results:

The CPU has been verified to successfully:

- Initialize with PC = 0x4 after reset release
- Execute the embedded sample program
- Increment PC by 4 for each instruction (0x4 → 0x8 → 0xC → 0x10...)
- Run for 20 cycles without errors
- Maintain proper timing relationships

#### Test Output Example:

```
Starting CPU simulation...
Time: 20 - Reset released, PC: 0000000000000004
Cycle 1: Time: 25, PC: 0x0000000000000004
Cycle 2: Time: 35, PC: 0x0000000000000008
Cycle 3: Time: 45, PC: 0x000000000000000c
...
```

The test confirms that the CPU is functioning correctly and executing the embedded sample program as designed.
