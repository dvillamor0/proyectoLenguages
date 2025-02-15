#unidad de control
ir = 0
cp = 0

#alu

#registros
reg = [0,0,0,0]

#control
carry = 0
zero = 0
negativo = 0
desvordamiento = 0

# Definir el rango de 21 bits con signo
MAX_VALOR = 2**20 - 1  # 1048575
MIN_VALOR = -2**20     # -1048576

def actualizar_banderas(resultado):
    global carry, zero, negativo, desbordamiento
    # Actualizamos la bandera "Zero"
    if resultado == 0:
        zero = 1
    else:
        zero = 0
    
    # Actualizamos la bandera "Negativo"
    if resultado < 0:
        negativo = 1
    else:
        negativo = 0
    
    # Bandera de "Overflow" para operaciones de suma o resta
    if resultado > MAX_VALOR or resultado < MIN_VALOR:  # Desbordamiento de 21 bits
        desbordamiento = 1
    else:
        desbordamiento = 0
    
    # La bandera "Carry" se ajusta para operaciones de suma y resta
    # El carry se activa si hay un valor fuera del rango de 21 bits
    if resultado > MAX_VALOR or resultado < MIN_VALOR:
        carry = 1
    else:
        carry = 0

def assembler_to_binary(instruction):
    parts = instruction.split()
    zero = 0

    # Transferencia de Datos
    if parts[0] == "LOAD":
        # LOAD Rx, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        mem = 0
        try:
            mem = int(parts[2][1:-1], 16)  # Dirección de memoria (hexadecimal entre corchetes)
            # La dirección de memoria debe ser un valor binario de 23 bits
        except ValueError:
            ry = 0
            if parts[2][1:3] == "R0":
                ry = 0
            elif parts[2][1:3] == "R1":
                ry = 1
            elif parts[2][1:3] == "R2":
                ry = 2
            elif parts[2][1:3] == "R3":
                ry = 3
            return f"{'11101'}{rx:02b}{ry:02b}{mem:023b}"
        # La dirección de memoria debe ser un valor binario de 23 bits
        return f"{'00001'}{rx:02b}{zero:02b}{mem:023b}"

    elif parts[0] == "STORE":
        # STORE Rx, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        mem = 0
        try:
            mem = int(parts[2][1:-1], 16)  # Dirección de memoria (hexadecimal entre corchetes)
        except ValueError:
            ry = 0
            if parts[2][1:3] == "R0":
                ry = 0
            elif parts[2][1:3] == "R1":
                ry = 1
            elif parts[2][1:3] == "R2":
                ry = 2
            elif parts[2][1:3] == "R3":
                ry = 3
            return f"{'11110'}{rx:02b}{ry:02b}{mem:023b}"
        return f"{'00010'}{rx:02b}{zero:02b}{mem:023b}"

    elif parts[0] == "MOVE":
        # MOVE Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'00011'}{rx:02b}{ry:02b}{zero:023b}"

    # Aritméticas
    elif parts[0] == "ADD":
        # ADD Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'00100'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    elif parts[0] == "SUB":
        # SUB Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'00101'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    elif parts[0] == "MUL":
        # MUL Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'00110'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    elif parts[0] == "DIV":
        # DIV Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'00111'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    # Lógicas
    elif parts[0] == "AND":
        # AND Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'01000'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    elif parts[0] == "OR":
        # OR Rx, Ry, Rz
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        rz = int(parts[3][1])  # Número del registro Rz
        return f"{'01001'}{rx:02b}{ry:02b}{rz:02b}{zero:021b}"

    elif parts[0] == "NOR":
        # NOR Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'01010'}{rx:02b}{ry:02b}{zero:023b}"

    elif parts[0] == "NOT":
        # NOT Rx
        rx = int(parts[1][1])  # Número del registro Rx
        return f"{'01011'}{rx:02b}{zero:025b}"

    # Desplazamientos y Rotaciones
    elif parts[0] == "SHL":
        # SHL Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'01100'}{rx:02b}{ry:02b}{zero:023b}"

    elif parts[0] == "SHR":
        # SHR Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'01101'}{rx:02b}{ry:02b}{zero:023b}"

    elif parts[0] == "ROL":
        # ROL Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'01110'}{rx:02b}{ry:02b}{zero:023b}"

    elif parts[0] == "ROR":
        # ROR Rx, Ry
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        return f"{'01111'}{rx:02b}{ry:02b}{zero:023b}"

    # Control de Flujo
    elif parts[0] == "JUMP":
        # JUMP [mem]
        mem = int(parts[1][1:-1], 16)  # Dirección de memoria (hexadecimal entre corchetes)
        return f"{'10000'}{zero:04b}{mem:023b}"

    elif parts[0] == "BEQ":
        # BEQ Rx, Ry, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        mem = int(parts[3][1:-1], 16)  # Dirección de memoria
        return f"{'10001'}{rx:02b}{ry:02b}{mem:023b}"

    elif parts[0] == "BNE":
        # BNE Rx, Ry, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        mem = int(parts[3][1:-1], 16)  # Dirección de memoria
        return f"{'10010'}{rx:02b}{ry:02b}{mem:023b}"

    elif parts[0] == "BLT":
        # BLT Rx, Ry, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        mem = int(parts[3][1:-1], 16)  # Dirección de memoria
        return f"{'10011'}{rx:02b}{ry:02b}{mem:023b}"

    elif parts[0] == "JLE":
        # BGT Rx, Ry, [mem]
        rx = int(parts[1][1])  # Número del registro Rx
        ry = int(parts[2][1])  # Número del registro Ry
        mem = int(parts[3][1:-1], 16)  # Dirección de memoria
        return f"{'10100'}{rx:02b}{ry:02b}{mem:023b}"

    # Instrucciones Especiales
    elif parts[0] == "NOP":
        # NOP
        return "00000000000000000000000000000000"

    elif parts[0] == "HALT":
        # HALT
        return "11111000000000000000000000000000"

    elif parts[0] == "PUSH":
        # PUSH Rx
        rx = int(parts[1][1])  # Número del registro Rx
        return f"{'10101'}{rx:02b}{zero:025b}"

    elif parts[0] == "POP":
        # POP Rx
        rx = int(parts[1][1])  # Número del registro Rx
        return f"{'10110'}{rx:02b}{zero:025b}"

    elif parts[0] == "CALL":
        # CALL [mem]
        mem = int(parts[1][1:-1], 16)  # Dirección de memoria
        return f"{'10111'}{zero:04b}{mem:023b}"

    elif parts[0] == "RET":
        # RET
        return f"{'11000'}{zero:027b}"

    # Entrada y salida
    elif parts[0] == "IN":
        # IN Rx
        rx = int(parts[1][1])  # Número del registro Rx
        return f"{'11001'}{rx:02b}{zero:025b}"

    elif parts[0] == "OUT":
        # OUT Rx
        rx = int(parts[1][1])  # Número del registro Rx
        return f"{'11010'}{rx:02b}{zero:025b}"

    elif parts[0] == "CMP":
      # CMP Rx, Ry
      rx = int(parts[1][1])  # Número del registro Rx
      ry = int(parts[2][1])  # Número del registro Ry
      return f"{'11011'}{rx:02b}{ry:02b}{zero:023b}"

    elif parts[0] == "CLR":
      # CLR Rx
      rx = int(parts[1][1])  # Número del registro Rx
      return f"{'11100'}{rx:02b}{zero:025b}"

    return parts[0]

instructions = [
    "LOAD R1, [0x3F]",
    "LOAD R1, [R1]",
    "STORE R2, [0x1A]",
    "STORE R2, [R1]",
    "MOVE R3, R0",
    "ADD R1, R2, R3",
    "SUB R1, R2, R3",
    "MUL R1, R2, R3",
    "DIV R1, R2, R3",
    "AND R1, R2, R3",
    "OR R1, R2, R3",
    "NOR R1, R2",
    "NOT R1",
    "SHL R1, R2",
    "SHR R1, R2",
    "ROL R1, R2",
    "ROR R1, R2",
    "JUMP [0x1A]",
    "BEQ R1, R2, [0x3F]",
    "BNE R1, R2, [0x1A]",
    "BLT R1, R2, [0x3F]",
    "JLE R1, R2, [0x1A]",
    "NOP",
    "HALT",
    "PUSH R1",
    "POP R1",
    "CALL [0x2A]",
    "RET",
    "IN R1",
    "OUT R1",
    "CMP R1, R2",
    "CLR R1"
]

#memoria
memoria = []
stack = []

def cargar_memoria_archivo(nombre):
    with open(nombre + '.txt', 'r') as archivo:
        for linea in archivo:
            linea = assembler_to_binary(linea)
            memoria.append(linea)

def cargar_memoria_input():
    while True:
        linea = input()
        if linea == "":
            break
        memoria.append(assembler_to_binary(linea))

#memoria
memoria = []
stack = []

def cargar_memoria_archivo(nombre):
    with open(nombre + '.txt', 'r') as archivo:
        for linea in archivo:
            linea = assembler_to_binary(linea)
            memoria.append(linea)

def cargar_memoria_input():
    while True:
        linea = input()
        if linea == "":
            break
        memoria.append(assembler_to_binary(linea))

def ejecutar_instruccion():
    global cp, reg, memoria, carry, zero, negativo, desvordamiento,ir

    # Obtener la instrucción a ejecutar
    ir = memoria[cp]
    cp += 1

    opcode = ir[:5]
    rx_bin = ir[5:7]
    ry_bin = ir[7:9]
    rz_bin = ir[9:11]
    mem_bin = ir[11:]

    # Convertir los índices binarios a enteros
    rx = int(rx_bin, 2)
    ry = int(ry_bin, 2)
    rz = int(rz_bin, 2)
    mem = int(mem_bin, 2)

    # Transferencia de Datos
    if opcode == "00001":  # LOAD 1
        reg[rx] = int(memoria[mem])
        print(f"LOAD R{rx} <- [0x{mem:02X}] = {memoria[mem]}")

    elif opcode == "11101":  # LOAD 1 de registro
        direccion = reg[ry]
        reg[rx] = int(memoria[direccion])
        print(f"LOAD R{rx} <- [R{ry}] = {memoria[direccion]}")

    elif opcode == "11110":  # STORE 2
        while len(memoria) <= mem:
            memoria.append(0)
        direccion = reg[ry]
        memoria[direccion] = int(reg[rx])
        print(f"STORE R{rx} -> [R{ry}] = {reg[rx]}")

    elif opcode == "00010":  # STORE 2 de registro
        while len(memoria) <= mem:
            memoria.append(0)
        memoria[mem] = int(reg[rx])
        print(f"STORE R{rx} -> [0x{mem:02X}] = {reg[rx]}")

    elif opcode == "00011":  # MOVE 3
        reg[rx] = int(reg[ry])
        print(f"MOVE R{rx} <- R{ry} = {reg[rx]}")

    # Aritméticas
    elif opcode == "00100":  # ADD 4
        reg[rx] = int(reg[ry]) + int(reg[rz])
        actualizar_banderas(reg[rx])
        print(f"ADD R{rx} <- R{ry} + R{rz} = {reg[rx]}")

    elif opcode == "00101":  # SUB 5
        reg[rx] = int(reg[ry]) - int(reg[rz])
        actualizar_banderas(reg[rx])
        print(f"SUB R{rx} <- R{ry} - R{rz} = {reg[rx]}")

    elif opcode == "00110":  # MUL 6
        reg[rx] = int(reg[ry]) * int(reg[rz])
        actualizar_banderas(reg[rx])
        print(f"MUL R{rx} <- R{ry} * R{rz} = {reg[rx]}")

    elif opcode == "00111":  # DIV 7
        if reg[rz] != 0:
            reg[rx] = int(reg[ry]) // int(reg[rz])
            actualizar_banderas(reg[rx])
            print(f"DIV R{rx} <- R{ry} // R{rz} = {reg[rx]}")
        else:
            print("Error: División por cero")

    # Lógicas
    elif opcode == "01000":  # AND 8
        reg[rx] = reg[ry] & reg[rz]
        print(f"AND R{rx} <- R{ry} & R{rz} = {reg[rx]}")

    elif opcode == "01001":  # OR 9
        reg[rx] = reg[ry] | reg[rz]
        print(f"OR R{rx} <- R{ry} | R{rz} = {reg[rx]}")

    elif opcode == "01010":  # NOR 10
        reg[rx] = ~(reg[ry] | reg[rz])
        print(f"NOR R{rx} <- ~(R{ry} | R{rz}) = {reg[rx]}")

    elif opcode == "01011":  # NOT 11
        reg[rx] = ~reg[rx]
        print(f"NOT R{rx} <- ~R{rx} = {reg[rx]}")

    # Desplazamientos y Rotaciones
    elif opcode == "01100":  # SHL 12
        reg[rx] = reg[ry] << 1
        print(f"SHL R{rx} <- R{ry} << 1 = {reg[rx]}")

    elif opcode == "01101":  # SHR 13
        reg[rx] = reg[ry] >> 1
        print(f"SHR R{rx} <- R{ry} >> 1 = {reg[rx]}")

    elif opcode == "01110":  # ROL 14
        reg[rx] = (reg[ry] << 1) | (reg[ry] >> 31)
        print(f"ROL R{rx} <- R{ry} rotate left = {reg[rx]}")

    elif opcode == "01111":  # ROR 15
        reg[rx] = (reg[ry] >> 1) | (reg[ry] << 31)
        print(f"ROR R{rx} <- R{ry} rotate right = {reg[rx]}")

    # Control de Flujo
    elif opcode == "10000":  # JUMP 16
        cp = mem
        print(f"JUMP to 0x{mem:02X}")

    elif opcode == "10001":  # BEQ 17
        if int(reg[rx]) == int(reg[ry]):
            cp = mem
            print(f"Jumping to 0x{mem:02X}")
        print(f"BEQ: R{rx} = {reg[rx]} and R{ry} = {reg[ry]}")

    elif opcode == "10010":  # BNE 18
        if int(reg[rx]) != int(reg[ry]):
            cp = mem
            print(f"BNE: Jumping to 0x{mem:02X}")
        print(f"BNE: R{rx} = {reg[rx]} and R{ry} = {reg[ry]}")

    elif opcode == "10011":  # BLT 19
        if int(reg[rx]) < int(reg[ry]):
            cp = mem
            print(f"BLT: Jumping to 0x{mem:02X}")
        print(f"BLT: R{rx} = {reg[rx]} and R{ry} = {reg[ry]}")

    elif opcode == "10100":  # JLE 20
        if int(reg[rx]) <= int(reg[ry]):
            cp = mem
            print(f"JLE : Jumping to 0x{mem:02X}")
        print(f"JLE : R{rx} = {reg[rx]} and R{ry} = {reg[ry]}")

    # Instrucciones Especiales
    elif opcode == "00000":  # NOP 0
        print("NOP: No operation")

    elif opcode == "11111":  # HALT 31
        print("HALT: Stopping execution")
        cp = len(memoria)

    elif opcode == "10101":  # PUSH 22
        stack.append(reg[rx])
        print(f"PUSH: Pushed R{rx} = {reg[rx]} to stack")

    elif opcode == "10110":  # POP 23
        reg[rx] = stack.pop()
        print(f"POP: Popped {reg[rx]} to R{rx}")

    elif opcode == "10111":  # CALL 24
        stack.append(cp)
        cp = mem
        print(f"CALL: Jumping to 0x{mem:02X}")

    elif opcode == "11000":  # RET 25
        cp = stack.pop()
        print(f"RET: Returning to 0x{cp:02X}")

    # Entrada y salida
    elif opcode == "11001":  # IN 26
        reg[rx] = input(f"Enter data for R{rx}: ")
        print(f"IN: Input data into R{rx}")

    elif opcode == "11010":  # OUT 27
        print(f"OUT: Output data from R{rx} = {reg[rx]}")

    elif opcode == "11011":  # CMP 29
        if reg[rx] == reg[ry]:
            zero = 1
        else:
            zero = 0
        print(f"CMP: Comparing R{rx} with R{ry}, Zero flag = {zero}")

    elif opcode == "11100":  # CLR 30
        reg[rx] = 0
        print(f"CLR: Cleared R{rx}")

def limpiar():
    global memoria,stack,reg
    memoria = []
    stack = []
    reg = [0, 0, 0, 0]

def factorial():
    while cp < len(memoria):
        try:
            ejecutar_instruccion()
        except Exception as e:
            return "el resultado es: " #direccion de memoria donde se guarda el resultado
            break


 #bubbleSort
def bubbleSort():
    limpiar()
    cargar_memoria_archivo("bubbleSort")
    cp = 9
    while cp <= len(memoria):
        try:
            ejecutar_instruccion()
        except Exception as e:
            print("el resultado es:",memoria[4:9]) #direccion de memoria donde se guarda el resultado
            break

 #binarySearch
def binarySearch():
    limpiar()
    cargar_memoria_archivo("binarySearch")
    cp = 10
    while cp <= len(memoria):
        try:
            ejecutar_instruccion()
        except Exception as e:
            print("el resultado es:",memoria[34]) #direccion de memoria donde se guarda el resultado
            break