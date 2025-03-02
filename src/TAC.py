import re
import sys

def tac_to_assembly(tac_file):
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
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue

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
    current_position = 0
    for line in tac_lines:
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
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' != ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' < ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' <= ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' > ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' >= ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            current_position += 2  # LOAD, STORE
        elif line.startswith('ifz'):
            current_position += 4  # LOAD, LOAD, CMP, BEQ
        elif line.startswith('goto'):
            current_position += 1  # JUMP
        elif line.startswith('return'):
            current_position += 2  # LOAD, RET

    # Segunda pasada para generar código
    for line in tac_lines:
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
        if line.startswith('L') and ':' in line:
            continue

        # Ejemplo: manejo de la suma en operaciones aritméticas
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

        # Manejar otras operaciones aritméticas
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
        
        # Manejar operaciones de comparación
        elif '=' in line and ' == ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' == ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            code_section.append("CMP R0, R1")
            asm_position += 1
            # Almacenar el resultado de la comparación (1 si igual, 0 si diferente)
            code_section.append(f"BEQ R0, R1, [0x{asm_position+2:X}]")
            asm_position += 1
            code_section.append(f"STORE R0, [0x{target_addr:X}]")  # Almacenar 0
            asm_position += 1
            code_section.append(f"LOAD R2, [0x1]")  # Cargar 1
            asm_position += 1
            code_section.append(f"STORE R2, [0x{target_addr:X}]")  # Almacenar 1
            asm_position += 1

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
                    code_section.append("CMP R0, R1")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                else:
                    code_section.append(f"# Expresión de comparación no reconocida: {expr}")
                    asm_position += 1
            elif expr.replace('.', '', 1).isdigit():
                const_addr = const_table[expr]
                code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            elif expr in var_table:
                source_addr = var_table[expr]
                code_section.append(f"LOAD R0, [0x{source_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            else:
                code_section.append(f"# Expresión no reconocida: {expr}")
                asm_position += 1

        elif line.startswith('ifz'):
            parts = line.split()
            cond = parts[1]
            goto_label = parts[3]
            cond_addr = const_table[cond] if cond.replace('.', '', 1).isdigit() else var_table[cond]
            
            code_section.append(f"LOAD R0, [0x{cond_addr:X}]")
            asm_position += 1
            code_section.append("LOAD R1, [0x0]")
            asm_position += 1
            code_section.append("CMP R0, R1")
            asm_position += 1
            
            if goto_label in label_to_asm:
                # FIXED: Changed format to match VM's expected bit pattern for BEQ
                code_section.append(f"BEQ R0, R1, [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"BEQ R0, R1, [{goto_label}]")
            asm_position += 1

        elif line.startswith('goto'):
            goto_label = line.split()[1]
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1

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

    return data_section, fixed_code_section

def main():
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