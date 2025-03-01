def tac_to_assembly(tac_file):
    """
    Convierte un archivo TAC (Three-Address Code) a código ensamblador para la CPU personalizada.
    
    Args:
        tac_file (str): Ruta al archivo TAC
        
    Returns:
        tuple: (data_section, code_section) conteniendo listas de datos y instrucciones en ensamblador
    """
    # Leer el archivo TAC
    with open(tac_file, 'r') as f:
        tac_lines = f.readlines()
    
    # Eliminar espacios en blanco al inicio/final y líneas vacías
    tac_lines = [line.strip() for line in tac_lines if line.strip()]
    
    # Inicializar estructuras de datos
    data_section = []      # Valores de inicialización de memoria
    code_section = []      # Instrucciones de ensamblador
    temp_vars = {}         # Mapea variables temporales a registros
    variables = {}         # Mapea variables del programa a direcciones de memoria
    memory_values = {}     # Rastrea valores actuales en ubicaciones de memoria
    label_positions = {}   # Mapea etiquetas a posiciones en el TAC
    label_to_asm = {}      # Mapea etiquetas a posiciones en el ensamblador
    
    # Inicializar constantes estándar
    data_section.append("0")   # Dirección 0: Constante 0
    memory_values[0] = "0"
    
    # Primera pasada: identificar todas las variables y asignar direcciones de memoria
    next_addr = 1
    
    for i, line in enumerate(tac_lines):
        if line.startswith('L') and ':' in line:
            # Es una etiqueta (L1:, L2:, etc.)
            label = line.split(':')[0]
            label_positions[label] = i
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            # Asignación de variable
            target = line.split('=', 1)[0].strip()
            expr = line.split('=', 1)[1].strip()
            
            # Agregar variables no temporales a nuestro mapeo
            if target not in variables:
                variables[target] = next_addr
                next_addr += 1
            
            # Si es una constante numérica, agregarla a nuestras constantes
            if expr.replace('.', '', 1).isdigit() and expr not in memory_values.values():
                memory_values[next_addr] = expr
                data_section.append(expr)
                next_addr += 1
    
    # Agregar constantes requeridas
    if "2" not in memory_values.values():
        memory_values[next_addr] = "2"
        data_section.append("2")
        next_addr += 1
    
    # También encontrar todas las variables usadas en las declaraciones de retorno
    for line in tac_lines:
        if line.startswith('return'):
            return_var = line.split()[1]
            if return_var not in variables:
                variables[return_var] = next_addr
                next_addr += 1
    
    # Depuración: Imprimir mapeo de variables
    print("# Variables y sus direcciones de memoria:")
    for var, addr in variables.items():
        print(f"# {var}: dirección {addr}")
    
    # Segunda pasada: Agregar valores iniciales a la memoria
    for var_addr in range(1, next_addr):
        if var_addr not in memory_values:
            # Esta es una variable que aún no tiene un valor inicial
            # La llenaremos con ceros por ahora
            data_section.append("0")  # Valor predeterminado
    
    # Tercera pasada: Generar código ensamblador
    asm_position = 0  # Iniciar posición de código desde 0, separada de la sección de datos
    
    for i, line in enumerate(tac_lines):
        # Saltar declaraciones de función y finalizaciones
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
            
        # Registrar posiciones de etiqueta en ensamblador
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = asm_position
            continue
        
        # Manejar asignaciones de variables (var = algo)
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [part.strip() for part in line.split('=', 1)]
            
            # Asegurar que el objetivo tenga una dirección
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")  # Agregar valor predeterminado a la memoria
                next_addr += 1
                
            # Encontrar dirección del objetivo
            target_addr = variables.get(target)
            
            # Manejar diferentes tipos de expresiones
            if expr.replace('.', '', 1).isdigit():  # Es una constante numérica
                # Encontrar dónde se almacena la constante
                const_addr = None
                for addr, val in memory_values.items():
                    if val == expr:
                        const_addr = addr
                        break
                
                if const_addr is None:
                    # Agregar la constante a la memoria
                    const_addr = next_addr
                    memory_values[next_addr] = expr
                    data_section.append(expr)
                    next_addr += 1
                
                # Cargar la constante en R0 y almacenar en la dirección objetivo
                code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            
            elif '!=' in expr:  # Comparación de desigualdad
                operands = expr.split('!=')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Asegurar que los operandos tengan direcciones
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")  # Agregar valor predeterminado a la memoria
                        next_addr += 1
                
                # Encontrar direcciones para operandos izquierdo y derecho
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Cargar operando izquierdo en R0
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                
                # Cargar operando derecho en R1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Comparar los valores
                code_section.append(f"CMP R0, R1")
                asm_position += 1
                
                # Almacenar el resultado
                code_section.append(f"STORE R0, [0x{target_addr:X}]")  
                asm_position += 1
            
            elif '/' in expr:  # Operación de división
                operands = expr.split('/')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Asegurar que los operandos tengan direcciones
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")  # Agregar valor predeterminado a la memoria
                        next_addr += 1
                
                # Encontrar direcciones para operandos izquierdo y derecho
                left_addr = variables.get(left)
                
                # Manejar operando derecho - podría ser una variable o una constante
                right_addr = None
                if right in variables:
                    right_addr = variables[right]
                else:
                    # Verificar si es una constante
                    for addr, val in memory_values.items():
                        if val == right:
                            right_addr = addr
                            break
                    
                    # Si aún no se encuentra, agregarla
                    if right_addr is None and right.replace('.', '', 1).isdigit():
                        right_addr = next_addr
                        memory_values[next_addr] = right
                        data_section.append(right)
                        next_addr += 1
                
                # Cargar operandos
                if left_addr is not None:
                    code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                    asm_position += 1
                
                if right_addr is not None:
                    code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                    asm_position += 1
                
                # Realizar división
                code_section.append(f"DIV R2, R0, R1")
                asm_position += 1
                
                # Almacenar resultado
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
            
            elif '+' in expr:  # Operación de suma
                operands = expr.split('+')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Asegurar que los operandos tengan direcciones
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")  # Agregar valor predeterminado a la memoria
                        next_addr += 1
                
                # Encontrar direcciones para operandos izquierdo y derecho
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Cargar operando izquierdo en R0
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                
                # Cargar operando derecho en R1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Realizar la suma
                code_section.append(f"ADD R3, R0, R1")
                asm_position += 1
                
                # Almacenar el resultado
                code_section.append(f"STORE R3, [0x{target_addr:X}]")
                asm_position += 1
            
            elif '*' in expr:  # Operación de multiplicación
                operands = expr.split('*')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Asegurar que los operandos tengan direcciones
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")  # Agregar valor predeterminado a la memoria
                        next_addr += 1
                
                # Encontrar direcciones para operandos izquierdo y derecho
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Cargar operando izquierdo en R0
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                
                # Cargar operando derecho en R1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Realizar la multiplicación
                code_section.append(f"MUL R3, R0, R1")
                asm_position += 1
                
                # Almacenar el resultado
                code_section.append(f"STORE R3, [0x{target_addr:X}]")
                asm_position += 1
            
            elif '<' in expr:  # Comparación menor que
                operands = expr.split('<')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Asegurar que los operandos tengan direcciones
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")  # Agregar valor predeterminado a la memoria
                        next_addr += 1
                
                # Encontrar direcciones para operandos izquierdo y derecho
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Cargar operando izquierdo en R0
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                
                # Cargar operando derecho en R1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Comparar los valores
                code_section.append(f"CMP R0, R1")
                asm_position += 1
                
                # Almacenar el resultado
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            
            else:  # Asignación simple de variable (target = var)
                # Asegurar que la variable fuente tenga una dirección
                if expr not in variables and not expr.replace('.', '', 1).isdigit():
                    variables[expr] = next_addr
                    data_section.append("0")  # Agregar valor predeterminado a la memoria
                    next_addr += 1
                
                # Encontrar la dirección de origen
                src_addr = variables.get(expr)
                
                if src_addr is not None:
                    # Cargar desde dirección de origen a R0
                    code_section.append(f"LOAD R0, [0x{src_addr:X}]")
                    asm_position += 1
                    
                    # Almacenar desde R0 a dirección objetivo
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                elif expr.replace('.', '', 1).isdigit():
                    # Es una constante que aún no estaba en la memoria
                    const_addr = next_addr
                    memory_values[next_addr] = expr
                    data_section.append(expr)
                    next_addr += 1
                    
                    # Cargar y almacenar
                    code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                else:
                    # La fuente no es una variable que conocemos
                    # Podría ser una llamada a función u otra expresión
                    # Manejémosla genéricamente con un comentario
                    code_section.append(f"# Asignación desconocida: {target} = {expr}")
                    asm_position += 1
        
        # Manejar saltos condicionales (ifz t1 goto L2)
        elif line.startswith('ifz'):
            parts = line.split()
            condition_var = parts[1]
            goto_label = parts[3]
            
            # Asegurar que la variable de condición tenga una dirección
            if condition_var not in variables:
                variables[condition_var] = next_addr
                data_section.append("0")  # Agregar valor predeterminado a la memoria
                next_addr += 1
            
            # Encontrar dirección para la variable de condición
            condition_addr = variables.get(condition_var)
            
            # Cargar condición en R0
            code_section.append(f"LOAD R0, [0x{condition_addr:X}]")
            asm_position += 1
            
            # Cargar 0 para comparación
            code_section.append(f"LOAD R1, [0x0]")
            asm_position += 1
            
            # Comparar los valores
            code_section.append(f"CMP R0, R1")
            asm_position += 1
            
            # BEQ significa "branch if equal" - usado para ifz (si es cero)
            if goto_label in label_to_asm:
                code_section.append(f"BEQ R0, R1, [0x{label_to_asm[goto_label]:X}]")
            else:
                # Almacenar la etiqueta para resolución posterior
                code_section.append(f"BEQ R0, R1, [{goto_label}]")
            asm_position += 1
        
        # Manejar saltos incondicionales (goto L1)
        elif line.startswith('goto'):
            goto_label = line.split()[1]
            
            # Agregar la instrucción de salto
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                # Almacenar la etiqueta para resolución posterior
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1
        
        # Manejar declaraciones de retorno
        elif line.startswith('return'):
            return_var = line.split()[1]
            
            # Asegurar que la variable de retorno tenga una dirección
            if return_var not in variables:
                variables[return_var] = next_addr
                data_section.append("0")  # Agregar valor predeterminado a la memoria
                next_addr += 1
            
            # Encontrar dirección para la variable de retorno
            return_addr = variables.get(return_var)
            
            # Cargar valor de retorno en R0
            code_section.append(f"LOAD R0, [0x{return_addr:X}]")
            asm_position += 1
            
            # Retornar de la función
            code_section.append("RET")
            asm_position += 1
        
        # Manejar llamadas a funciones (t9 = call sqrt, 1)
        elif 'call' in line:
            parts = line.split('=')
            target = parts[0].strip()
            
            # Asegurar que la variable objetivo tenga una dirección
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")  # Agregar valor predeterminado a la memoria
                next_addr += 1
                
            target_addr = variables.get(target)
            
            # Extraer nombre de función y argumentos
            call_parts = parts[1].strip().split(',')
            func_name = call_parts[0].strip()
            func_name = func_name.replace('call ', '')
            
            # Por ahora, solo agregar un comentario
            code_section.append(f"# Llamada a función: {line}")
            asm_position += 1
    
    # Última pasada: resolver referencias de etiquetas
    fixed_code_section = []
    for instr in code_section:
        if instr.startswith("#"):
            # Mantener comentarios como están
            fixed_code_section.append(instr)
        else:
            # Verificar referencias de etiquetas en la instrucción
            modified_instr = instr
            for label, pos in label_to_asm.items():
                if f"[{label}]" in modified_instr:
                    modified_instr = modified_instr.replace(f"[{label}]", f"[0x{pos:X}]")
            fixed_code_section.append(modified_instr)
    
    return data_section, fixed_code_section

def main():
    """Función principal para ejecutar el convertidor de TAC a ensamblador."""
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python tac_to_assembly.py <archivo_entrada.tac>")
        sys.exit(1)
    
    tac_file = sys.argv[1]
    data_section, code_section = tac_to_assembly(tac_file)
    
    # escribir a un archivo
    output_file = tac_file.replace('.tac', '.asm')
    with open(output_file, 'w') as f:
        for data in data_section:
            f.write(f"{data}\n")
        
        for instr in code_section:
            f.write(f"{instr}\n")
    
    print(f"\nCódigo ensamblador escrito en {output_file}")

if __name__ == "__main__":
    main()