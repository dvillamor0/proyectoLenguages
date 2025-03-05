import re
import sys

def debug_print(*args, **kwargs):
    with open('debug_TAC_to_assembler.log', 'a', encoding='utf-8') as f:
        print(*args, **kwargs, file=f)

def manejarOperacion(tac_lines,i):
    #t5 = a + t4
    pass

def manejarFunction(tac_lines,i):
    pass
    
def manejarParametro(tac_lines,i):
    pass

def manejarGoto(tac_lines,i):
    pass

def manejarIf(tac_lines,i):
    pass

def manejarComparacion(tac_lines,i):

    pass

def manejarRegreso(tac_lines,i):
    pass

def manejarAsignacion(tac_lines,i, variables, ensamblador):

    line = tac_lines[i]
    destino = line.split("=")[0].strip()
    direccion = variables[destino]
    operancion = line.split("=")[1].strip()
    operando1 = operancion.split(" ")[0].strip()
    simbolo = operancion.split(" ")[1].strip()
    operando2 = operancion.split(" ")[2].strip()
    if operando1.isnumeric() and :
        #t1 = 5
        #load operando 1
        ensamblador += f"{operando1}\n"
        return
    #load operando 1
    ensamblador += f"LOAD R0, {variables[operando1]}\n"

    if simbolo:
        #load operando 2
        ensamblador += f"LOAD R1, {variables[operando2]}\n"

        if simbolo == "+":
            #suma
            ensamblador += f"ADD R0, R0, R1\n"            
            pass
        elif simbolo == "-":
            #resta
            ensamblador += f"SUB R0, R0, R1\n"
            pass
        elif simbolo == "*":
            #multiplicacion
            ensamblador += f"MUL R0, R0, R1\n"
            pass
        elif simbolo == "/":
            #division
            ensamblador += f"DIV R0, R0, R1\n"
            pass
        else:
            print("Operacion no soportada")
        #store
    ensamblador += f"STORE R0, {direccion}\n"
    pass

def guardarEtiqueta(tac_lines,i):
    pass


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

    addr = 0
    comandosDelTAC = {
        "=": manejarAsignacion,
        "goto": manejarGoto,
        "ifz": manejarIf,
      	"param":manejarParametro,
      	"ret": manejarRegreso
    }
    etiquetaYfuncion = {}

    # Primera pasada: identificar todas las etiquetas y funciones
    for i, line in enumerate(tac_lines):
        if line.startswith('L') or line.startswith('begin_function'):
            etiquetaYfuncion[line] = addr
            addr += 1

    variables = {}

    for i, line in enumerate(tac_lines):
        # Extraer los comandos de la línea
        comandos = re.findall(r'\b\w+\b', line)
        if len(comandos) == 0:
            print("Comando no encontrado")
        for comando in comandos:
            print("Se esta procesando el comando:",comando)
            comandosDelTAC[comando](tac_lines,i)
        addr += 1

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