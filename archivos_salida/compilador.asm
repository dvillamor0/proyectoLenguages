0
5
10
1
20
2
30
3
40
4
50
10.5
20.75
30.99
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
LOAD R0, [0x2]
STORE R0, [0x1]
LOAD R0, [0x1]
LOAD R1, [0x4]
STORE R1, [0x3]
LOAD R0, [0x0]
STORE R0, [0x4]
LOAD R0, [0x6]
STORE R0, [0x5]
LOAD R0, [0x5]
STORE R0, [0x7]
LOAD R0, [0x9]
STORE R0, [0x8]
LOAD R0, [0xB]
STORE R0, [0xA]
LOAD R0, [0xA]
STORE R0, [0xC]
LOAD R0, [0xE]
STORE R0, [0xD]
LOAD R0, [0x10]
STORE R0, [0xF]
LOAD R0, [0xF]
STORE R0, [0x11]
LOAD R0, [0x13]
STORE R0, [0x12]
LOAD R0, [0x15]
STORE R0, [0x14]
LOAD R0, [0x14]
STORE R0, [0x16]
LOAD R0, [0x18]
STORE R0, [0x17]
LOAD R0, [0x1A]
STORE R0, [0x19]
LOAD R0, [0x19]
STORE R0, [0x1B]
LOAD R0, [0x13]
STORE R0, [0x1C]
LOAD R0, [0x1E]
STORE R0, [0x1D]
LOAD R0, [0x1F]
STORE R0, [0x1E]
LOAD R0, [0x1E]
STORE R0, [0x20]
LOAD R0, [0x22]
STORE R0, [0x21]
LOAD R0, [0x21]
STORE R0, [0x23]
LOAD R0, [0x25]
STORE R0, [0x24]
LOAD R0, [0x24]
STORE R0, [0x26]
LOAD R0, [0x1C]
LOAD R1, [0x28]
STORE R1, [0x27]
LOAD R0, [0x1D]
STORE R0, [0x27]
LOAD R0, [0x0]
STORE R0, [0x28]
LOAD R0, [0x3]
LOAD R1, [0x28]
LOAD R2, [0x9]
ADD R1, R1, R2
ADD R2, R0, R1
LOAD R3, [0x0]
STORE R3, [0x29]
LOAD R0, [0x18]
STORE R0, [0x2A]
LOAD R0, [0x3]
LOAD R1, [0x2A]
LOAD R2, [0x9]
ADD R1, R1, R2
ADD R2, R0, R1
LOAD R3, [0x0]
STORE R3, [0x2B]
LOAD R0, [0x29]
LOAD R1, [0x2B]
ADD R2, R0, R1
STORE R2, [0x2C]
LOAD R0, [0x2C]
STORE R0, [0x2D]
LOAD R0, [0x0]
STORE R0, [0x2E]
LOAD R0, [0x2E]
STORE R0, [0x2F]
LOAD R0, [0x2]
STORE R0, [0x30]
LOAD R0, [0x2F]
LOAD R1, [0x30]
CMP R0, R1
LOAD R2, [0x0]
BLT R0, R1, [0x5C]
JUMP [0x5E]
LOAD R2, [0x9]
STORE R2, [0x31]
LOAD R0, [0x31]
LOAD R1, [0x0]
CMP R0, R1
BEQ R0, R1, [0x7A]
LOAD R0, [0x3]
LOAD R1, [0x2F]
LOAD R2, [0x9]
ADD R1, R1, R2
ADD R2, R0, R1
LOAD R3, [0x0]
STORE R3, [0x32]
LOAD R0, [0xE]
STORE R0, [0x33]
LOAD R0, [0x32]
LOAD R1, [0x33]
MUL R2, R0, R1
STORE R2, [0x34]
LOAD R0, [0x34]
STORE R0, [0x35]
LOAD R0, [0x9]
STORE R0, [0x36]
LOAD R0, [0x2F]
LOAD R1, [0x36]
ADD R2, R0, R1
STORE R2, [0x37]
LOAD R0, [0x37]
STORE R0, [0x2F]
JUMP [0x54]
LOAD R0, [0x0]
STORE R0, [0x38]
LOAD R0, [0x38]
RET
