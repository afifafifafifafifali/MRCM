# MRCM - A 64-bit RISC-like CPU

MRCM (Mithu Risc Computing Machine) A 64-bit RISC(Reduced Intrusction Set Computing) CPU implementation using MyHDL, based on RISC-V architecture principles. ** Please note that it is currently ROM(READ ONLY MEMORY) only CPU implementation. ** 

## Components

### `alu.py`

@brief: Arithmetic Logic Unit for 64-bit RISC CPU
Implements basic arithmetic and logical operations

Supports ADD, SUB, AND, OR operations on 64-bit operands.

### `reg.py`

@brief: Register File for 64-bit RISC CPU
Implements 32 general-purpose 64-bit registers

Contains 32 x 64-bit registers (x0-x31) with x0 hardwired to 0.
Supports simultaneous dual read and single write operations.

### `cpu_complete.py`

@brief: 64-bit RISC CPU implementation
Implements a RISC-V like processor with 5-stage pipeline

Features RISC-V compatible instruction set with support for:

- R-type: register-register operations
- I-type: register-immediate operations
- Load/Store: memory access operations
- Program counter management
- Built-in sample program execution

## Architecture

- 64-bit data path
- Harvard architecture (separate instruction/data memory)
- 5-stage pipeline (IF, ID, EX, MEM, WB)
- RISC-V inspired instruction encoding with extended x86-like instructions
- Modular design for extensibility

## Extended Instruction Set

The CPU now supports additional x86-like instructions:

- MOV_IMM: Move immediate value to register (like x86 MOV)
- CALLQ: Function call instruction (like x86 CALLQ)
- JMP: Unconditional jump instruction (like x86 JMP)
- RET: Return from function (like x86 RET)
- PUSH/POP: Stack operations

## Assembler Features

The CPU includes a complete assembler that supports:

- Standard RISC-V instructions
- Extended x86-like instructions
- Symbolic labels for branches and function calls
- DB (Define Byte) directive for data definition
- Human-readable assembly syntax (kinda like basic ngl)
- Memory layout: Instructions start at 0x4, data at 0x1000
