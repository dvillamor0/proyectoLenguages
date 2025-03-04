import re
import sys

def debug_print(*args, **kwargs):
    with open('debug_TAC_to_assembler.log', 'a', encoding='utf-8') as f:
        print(*args, **kwargs, file=f)

def tac_to_assembly(tac_file):
    """
    Traduce código de Tres Direcciones (TAC) a instrucciones de ensamblador para una máquina virtual simple.
    
    Este proceso incluye:
    1. Construcción de tablas de constantes y variables
    2. Asignación de direcciones de memoria
    3. Generación de código ensamblador equivalente
    4. Resolución de etiquetas de salto
    
    @param tac_file: Ruta al archivo TAC de entrada
    @return: Tupla con (sección de datos, sección de código)
    """
    # Leer y limpiar el archivo TAC
    with open(tac_file, 'r', encoding='utf-8') as f:
        tac_lines = [line.strip() for line in f if line.strip()]

    # --- Construir la tabla de constantes ---
    # Solo incluimos las constantes que aparecen en el TAC.
    # Se incluye "0" por defecto, ya que es común para comparaciones.
    const_table = {"0": 0}
    next_const_addr = 1

    # Primera pasada: identificar todas las constantes numéricas
    for line in tac_lines:
        # Ignorar etiquetas o líneas de control de flujo
        if line.startswith('L') and ':' in line:
            continue
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue

        # Buscar constantes en asignaciones
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            parts = [p.strip() for p in line.split('=', 1)]
            expr = parts[1]
            
            # Si es un operando solo (no una operación)
            if '+' not in expr and '-' not in expr and '*' not in expr and '/' not in expr and '==' not in expr and '!=' not in expr and '<' not in expr and '<=' not in expr and '>' not in expr and '>=' not in expr:
                if expr.replace('.', '', 1).isdigit() and expr not in const_table:
                    const_table[expr] = next_const_addr
                    next_const_addr += 1
            # Si es una operación, buscar constantes en los operandos
            else:
                # Manejar operadores de comparación también
                operators = r'[+\-*/=<>!]+'
                for op in re.split(operators, expr):
                    op = op.strip()
                    if op and op.replace('.', '', 1).isdigit() and op not in const_table:
                        const_table[op] = next_const_addr
                        next_const_addr += 1

    # --- Construir la tabla de variables ---
    var_table = {}
    next_var_addr = next_const_addr  # Las variables se asignan tras las constantes

    # Segunda pasada: asignar direcciones a todas las variables
    for line in tac_lines:
        # Ignorar etiquetas o líneas de control de flujo
        if line.startswith('L') and ':' in line:
            continue
        if line.startswith('begin_func') or line.startswith('end_func'):
            continue
        if line.startswith('param'):
            param = line.split()[1]
            if param not in var_table:
                var_table[param] = next_var_addr
                next_var_addr += 1

        # Procesar asignaciones y retornos
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [x.strip() for x in line.split('=', 1)]
            if target not in var_table:
                var_table[target] = next_var_addr
                next_var_addr += 1
                
            # Procesar también variables en expresiones de comparación
            if '==' in expr or '!=' in expr or '<' in expr or '<=' in expr or '>' in expr or '>=' in expr:
                # Extraer los operandos de la comparación
                comp_parts = re.split(r'(==|!=|<=|>=|<|>)', expr)
                for part in comp_parts:
                    part = part.strip()
                    if part and not part in ['==', '!=', '<=', '>=', '<', '>'] and not part.replace('.', '', 1).isdigit() and part not in var_table:
                        var_table[part] = next_var_addr
                        next_var_addr += 1
                        
        elif line.startswith('return'):
            ret_var = line.split()[1]
            if ret_var not in var_table and not ret_var.replace('.', '', 1).isdigit():
                var_table[ret_var] = next_var_addr
                next_var_addr += 1

    # --- Construir la sección de datos ---
    total_addresses = next_var_addr  # Suma de direcciones usadas para constantes y variables
    data_section = ["0"] * total_addresses  # Inicializar toda la memoria en "0"
    # Colocar cada constante en su dirección asignada
    for const, addr in const_table.items():
        data_section[addr] = const

    # --- Generar la sección de código ---
    code_section = []
    asm_position = 0

    # Mapeo de etiquetas a posiciones de código ensamblador
    label_to_asm = {}

    # Primera pasada para identificar posiciones de etiquetas
    current_position = len(data_section)
    for line in tac_lines:
        if line.startswith('begin_func'):
            label = line.split(' ')[1]            
            label_to_asm[label] = current_position
            continue
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = current_position
            continue

        # Contar instrucciones para cada tipo de operación
        if '=' in line and ' + ' in line:
            current_position += 4  # LOAD, LOAD, ADD, STORE
        elif '=' in line and ' - ' in line:
            current_position += 4  # LOAD, LOAD, SUB, STORE
        elif '=' in line and ' * ' in line:
            current_position += 4  # LOAD, LOAD, MUL, STORE
        elif '=' in line and ' / ' in line:
            current_position += 4  # LOAD, LOAD, DIV, STORE
        elif '=' in line and ' == ' in line:
            current_position += 2  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' != ' in line:
            current_position += 2  # LOAD, LOAD
        elif '=' in line and ' < ' in line:
            current_position += 2  # LOAD, LOAD
        elif '=' in line and ' <= ' in line:
            current_position += 2  # LOAD, LOAD
        elif '=' in line and ' > ' in line:
            current_position += 2  # LOAD, LOAD
        elif '=' in line and ' >= ' in line:
            current_position += 2  # LOAD, LOAD
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            current_position += 2  # LOAD, STORE
        elif line.startswith('ifz'):
            current_position += 1  # BEQ
        elif line.startswith('goto'):
            current_position += 1  # JUMP
        elif line.startswith('return'):
            current_position += 2  # LOAD, RET
            
    debug_print("Tabla de etiquetas:", label_to_asm)
    
    # Segunda pasada para generar código
    pila_compare = []  # ✅ Pila para almacenar los operadores de comparación
    for line in tac_lines:
        debug_print(f"Procesando línea: {line}")
        # Ignorar directivas de función y parámetros
        if line == tac_lines[0]:
            label = 'main'
            target_addr = var_table[target]
            label_addr = label_to_asm[label]
            print("address:",label_to_asm,label_addr)
            code_section.append(f"CALL [0x{label_addr:X}]")
            asm_position += 1
            continue
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
        # Ignorar etiquetas en esta pasada, ya las procesamos en la primera pasada
        if line.startswith('L') and ':' in line:
            continue

        # Operación de suma: a = b + c
        if '=' in line and ' + ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' + ')]
            
            # Resolver la dirección: si es un literal, usar la tabla de constantes; si es una variable, usar la tabla de variables.
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            # Original: ADD R2, R0, R1
            # VM expects: destination register first, then operands
            code_section.append("ADD R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        # Operación de resta: a = b - c
        elif '=' in line and ' - ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' - ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("SUB R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        # Operación de multiplicación: a = b * c
        elif '=' in line and ' * ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' * ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("MUL R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        # Operación de división: a = b / c
        elif '=' in line and ' / ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' / ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("DIV R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1
        
        # Operación de igualdad: a = b == c
        elif '=' in line and ' == ' in line:
            pila_compare.append('==')
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' == ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            # code_section.append(f"STORE R0, [0x{target_addr:X}]")  # Almacenar 0
            # asm_position += 1
            # code_section.append(f"LOAD R2, [0x1]")  # Cargar 1
            # asm_position += 1
            # code_section.append(f"STORE R2, [0x{target_addr:X}]")  # Almacenar 1
            # asm_position += 1

        # Manejar asignaciones simples: var = literal o var = otra_var
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            
            # Manejo de expresiones de comparación
            if '==' in expr or '!=' in expr or '<' in expr or '<=' in expr or '>' in expr or '>=' in expr:
                # Aquí implementar la lógica para manejar comparaciones
                # Este sería el punto donde necesitamos manejar "a == b" y similares
                op_match = re.search(r'(==|!=|<=|>=|<|>)', expr)
                if op_match:
                    op = op_match.group(1)
                    left, right = [x.strip() for x in expr.split(op)]
                    
                    # Obtener direcciones de los operandos
                    left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table.get(left, 0)
                    right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table.get(right, 0)
                    
                    # Generar código para la comparación
                    code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                    asm_position += 1
                    pila_compare.append(op)
                else:
                    code_section.append(f"# Expresión de comparación no reconocida: {expr}")
                    asm_position += 1
            # Asignación de constante
            elif expr.replace('.', '', 1).isdigit():
                const_addr = const_table[expr]
                code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            # Asignación de variable
            elif expr in var_table:
                source_addr = var_table[expr]
                code_section.append(f"LOAD R0, [0x{source_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
             # Asignacion de llamada a función: var = call func, num_args
            elif 'call' in line:
                target, call_expr = [x.strip() for x in line.split('=', 1)]
                label, num_args = call_expr.split(', ')
                label = label.split()[1]
                target_addr = var_table[target]

                label_addr = label_to_asm[label]
                print("address:",label_to_asm,label_addr)
                code_section.append(f"CALL [0x{label_addr:X}]")
                asm_position += 1
                print("solo funciona con un argumento, argumentos:",num_args)
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1

            # Caso no reconocido
            else:
                code_section.append(f"# Expresión no reconocida: {expr}")
                asm_position += 1

        # Instrucción condicional: ifz condición goto etiqueta
        elif line.startswith('ifz'):
            comparacion = pila_compare.pop()  # ✅ Extrae el último operador de comparación
            parts = line.split()
            cond = parts[1]
            goto_label = parts[3]
            cond_addr = const_table[cond] if cond.replace('.', '', 1).isdigit() else var_table[cond]

            # Mapeo de operadores a instrucciones de ensamblador
            instrucciones_salto = {
                "==": "BEQ", # Si no son iguales, salta y no ejecuta la instruccion dentro
                "!=": "BNE", # Si no son diferentes, salta y no ejecuta la instruccion en la etiqueta
                "<": "BLT", # se invierte el orden de los registros y si no es menor o igual se salta la instruccion
                ">": "BLT", # si no es mayor se salta la instruccion
                "<=": "JLE", # se invierte el orden de los registros y si no es menor se salta la instruccion
                ">=": "JLE"  # si no es mayor o igual se salta la instruccion
            }

            instr_salto = instrucciones_salto.get(comparacion, "NOP")
            # Generación del código de salto con base en las instrucciones de comparación
            if comparacion in ["==", "!="]:
                if goto_label in label_to_asm:
                    code_section.append(f"{instr_salto} R0, R1, [0x{label_to_asm[goto_label]:X}]")
                else:
                    code_section.append(f"{instr_salto} R0, R1, [{goto_label}]")
            elif comparacion in ["<", "<=", ">", ">="]:
                if comparacion in [">", ">="]:
                    if goto_label in label_to_asm:
                        code_section.append(f"{instr_salto} R1, R0, [0x{label_to_asm[goto_label]:X}]")
                    else:
                        code_section.append(f"{instr_salto} R1, R0, [{goto_label}]")
                else:
                    if goto_label in label_to_asm:
                        code_section.append(f"{instr_salto} R0, R1, [0x{label_to_asm[goto_label]:X}]")
                    else:
                        code_section.append(f"{instr_salto} R0, R1, [{goto_label}]")

            asm_position += 1

        # Salto incondicional: goto etiqueta
        elif line.startswith('goto'):
            goto_label = line.split()[1]
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1

        # Retorno de función: return variable
        elif line.startswith('return'):
            ret_var = line.split()[1]
            if ret_var.replace('.', '', 1).isdigit():
                ret_addr = const_table[ret_var]
            else:
                ret_addr = var_table[ret_var]
                
            code_section.append(f"LOAD R0, [0x{ret_addr:X}]")
            asm_position += 1
            code_section.append("RET")
            asm_position += 1

        # Instrucción no implementada o no reconocida
        else:
            code_section.append(f"# Instrucción no implementada: {line}")
            asm_position += 1

    # Resolver referencias a etiquetas en el código
    fixed_code_section = []
    for instr in code_section:
        if instr.startswith("#"):
            fixed_code_section.append(instr)
        else:
            modified_instr = instr
            for label, pos in label_to_asm.items():
                if f"[{label}]" in modified_instr:
                    modified_instr = modified_instr.replace(f"[{label}]", f"[0x{pos:X}]")
            fixed_code_section.append(modified_instr)
    
    debug_print("Tabla de constantes:", const_table)
    debug_print("Tabla de variables:", var_table)
    debug_print("Sección de datos:", data_section)
    debug_print("Sección de código:", fixed_code_section)
    return data_section, fixed_code_section

def main():
    """
    Función principal que procesa los argumentos de línea de comandos, 
    llama al traductor TAC-a-ensamblador y escribe el resultado en un archivo.
    
    Uso desde línea de comandos: python TAC.py <archivo_entrada.tac>
    El archivo de salida tendrá el mismo nombre pero con extensión .asm
    """
    if len(sys.argv) != 2:
        print("Uso: python TAC.py <archivo_entrada.tac>")
        sys.exit(1)
    tac_file = sys.argv[1]
    data_section, code_section = tac_to_assembly(tac_file)
    output_file = tac_file.replace('.tac', '.asm')
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in data_section:
            f.write(f"{data}\n")
        for instr in code_section:
            f.write(f"{instr}\n")
    print(f"\nCódigo ensamblador escrito en {output_file}")

if __name__ == "__main__":
    main()