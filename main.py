# import sys
# from Diseño_GUI import *
# from PyQt5.QtWidgets import QApplication

# app = QApplication(sys.argv)
# window = Ui_MainWindow()
# Form = QtWidgets.QMainWindow()
# window.setupUi(Form)
# Form.show()
# sys.exit(app.exec_())

import sys
import tempfile
from assets.memoria import Memoria
from assets.IdentificarDato import GetEntero, GetFloat, GetNatural, GetBooleano, GetCaracterUtf16
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QApplication, QMainWindow
from vista.Diseno_GUI import *
from vista.prueba import *
import subprocess
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cp = 0
        self.registro = [0,0,0,0]
        self.carry = 0
        self.zero = 0
        self.negative = 0
        self.desbordamiento = 0
        self.config_input = {"text": "", "reg_input": 0, "Exxecute_all": False}
        self.set_REG_Values([0,0,0,0])
        self.setCarry(0)
        self.setZero(0)
        self.setNegative(0)
        self.setDesb(0)
        self.ui.input_button.setDisabled(True)
        self.memoria = Memoria(self.ui)
        self.ui.preprocesar_button.clicked.connect(self.Preprocesado)
        self.ui.ensamblador_button.clicked.connect(self.Ensamblador)
        self.ui.Linker_button.clicked.connect(self.EnlazadorCargador)
        self.ui.Read_Next_Instruction.clicked.connect(self.LeerInstruccion)
        self.ui.Exxecute_instructions.clicked.connect(self.LeerInstrucciones)
        self.ui.input_button.clicked.connect(self.getInput)
        self.ui.Charge_cp.clicked.connect(self.cargarCp)
        self.funciones = {
            "NOP" : self.NOP,
            "LOAD" : self.LOAD,
            "STORE" : self.STORE,
            "MOVE" : self.MOVE,
            "ADD" : self.ADD,
            "SUB" : self.SUB,
            "MUL" : self.MUL,
            "DIV" : self.DIV,
            "AND" : self.AND,
            "OR" : self.OR,
            "NOR" : self.NOR,
            "NOT" : self.NOT,
            "SHL" : self.SHL,
            "SHR" : self.SHR,
            "ROL" : self.ROL,
            "ROR" : self.ROR,
            "JUMP" : self.JUMP,
            "BEQ" : self.BEQ,
            "BNE" : self.BNE,
            "BLT" : self.BLT,
            "JLE" : self.JLE,
            "PUSH" : self.PUSH,
            "POP" : self.POP,
            "CALL" : self.CALL,
            "RET" : self.RET,
            "IN" : self.IN,
            "OUT" : self.OUT,
            "CMP" : self.CMP,
            "CLR" : self.CLR,
            "LOADR" : self.LOADR,
            "STORER" : self.STORER,
            "HALT" : self.HALT,
        }

    def cargarCp(self):
        valor = self.ui.CP_Set.toPlainText()
        try:
            valor = int(valor)
            self.setCp(valor)
        except ValueError as e:
            print(f"Error: '{valor}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
             
    def getInput(self):
        valor = self.ui.Input.toPlainText()
        self.guardar_en_registro(self.config_input["reg_input"], int(valor))
        Llama_all = self.config_input['Exxecute_all']
        self.config_input = {"text": "", "reg_input": 0, "Exxecute_all": False}
        self.ui.Read_Next_Instruction.setDisabled(False)
        self.ui.Exxecute_instructions.setDisabled(False)
        self.ui.input_button.setDisabled(True)
        if(Llama_all):
            self.LeerInstrucciones()
        
    def setCp(self,new_cp):
        try:
            self.cp = new_cp
            self.ui.CP_Set.setPlainText(str(new_cp))
            self.memoria.mover_cp(int(new_cp))
        except ValueError as e:
            print(f"Error: '{new_cp}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
            
    def setDir(self,new_dir):
        try:
            self.dir = new_dir
            self.ui.DIR.setPlainText(str(new_dir))
        except ValueError as e:
            print(f"Error: '{new_dir}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Instruccion]: "+ str(e))
        
    def actualizarTablaMemoria(self):
        """ Actualiza la tabla de memoria en la interfaz. """
        self.ui.table_memoria.setRowCount(len(self.memoria))

        for i, (direccion, valor) in enumerate(self.memoria.items()):
            self.ui.table_memoria.setItem(i, 0, QtWidgets.QTableWidgetItem(str(valor)))
            item = self.ui.table_memoria(str(valor))
            # Resaltar la fila si es la dirección de `cp`
            if direccion == self.cp:
                item.setBackground(QColor(255, 255, 0))  # Amarillo
            else:
                item.setBackground(QColor(255, 255, 255))  # Blanco

            self.ui.table_memoria.setItem(i, 0, item)
       
    def int_to_bin16(self,numero):
        if numero < 0:
            numero = (1 << 16) + numero  # Convierte a complemento a dos si es negativo
        return format(numero & 0xFFFF, '016b')  # Asegura 16 bits
 
    def guardar_en_registro(self,indice,value):
        temp_reg = self.registro
        temp_reg[indice] = value
        self.set_REG_Values(temp_reg)
        
    def set_REG_Values(self,arreglo):
        self.registro[0] = arreglo[0]
        self.registro[1] = arreglo[1]
        self.registro[2] = arreglo[2]
        self.registro[3] = arreglo[3]
        self.ui.REG_A.setText(str(arreglo[0]))
        self.ui.REG_B.setText(str(arreglo[1]))
        self.ui.REG_C.setText(str(arreglo[2]))
        self.ui.REG_D.setText(str(arreglo[3]))
        self.ui.BIN_A.setText(self.int_to_bin16(arreglo[0]))
        self.ui.BIN_B.setText(self.int_to_bin16(arreglo[1]))
        self.ui.BIN_C.setText(self.int_to_bin16(arreglo[2]))
        self.ui.BIN_D.setText(self.int_to_bin16(arreglo[3]))
      
    def setCarry(self,caryy):
        self.carry = caryy
        self.ui.REG_Carry.setText(str(caryy))
      
    def setZero(self,zero):
        self.zero = zero
        self.ui.REG_Zero.setText(str(zero))
        
    def setNegative(self,negative):
        self.negative = negative
        self.ui.REG_Neg.setText(str(negativo))
        
    def setDesb(self,desbordamiento):
        self.desbordamiento = desbordamiento
        self.ui.REG_Desb.setText(str(desbordamiento))
    
    def resetBanderas(self):
        self.setCarry(0)
        self.setZero(0)
        self.setNegative(0)
        self.setDesb(0)
        
    def Preprocesado(self):
        texto = self.ui.codigofuente_input.toPlainText()  # Obtener el texto del QTextEdit

        # Crear un archivo temporal para pasar el contenido al analizador Flex
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(texto.encode("utf-8"))
            temp_file_path = temp_file.name

        # Ejecutar el analizador léxico en Flex (asumiendo que ya compilaste el ejecutable)
        flex_executable = "./compilados/preprocessor.exe"  # Asegúrate de que `scanner` es el ejecutable de Flex generado con `gcc`
        try:
            result = subprocess.run(
                [flex_executable, temp_file_path],  # Ejecuta el scanner con el archivo temporal
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout  # Obtener la salida del scanner
            self.ui.codigo_preprocesado_input.setPlainText(output)
        except Exception as e:
            self.ui.Output.setPlainText("[Error Preprocesado]: "+ str(e))
        
    def Ensamblador(self):
        texto = self.ui.assembler_input.toPlainText()  # Obtener el texto del QTextEdit

        # Crear un archivo temporal para pasar el contenido al analizador Flex
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(texto.encode("utf-8"))
            temp_file_path = temp_file.name

        # Ejecutar el analizador léxico en Flex (asumiendo que ya compilaste el ejecutable)
        flex_executable = "./compilados/ensamblador"
        if os.name != 'posix':
            flex_executable += ".exe"
        try:
            result = subprocess.run(
                [flex_executable, temp_file_path],  # Ejecuta el scanner con el archivo temporal
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout  # Obtener la salida del scanner
            self.ui.binary_input.setPlainText(output)
        except Exception as e:
            self.ui.Output.setPlainText("[Error Preprocesado]: "+ str(e))
        
    def EnlazadorCargador(self):
        direccion_referencia = self.ui.linker_input.toPlainText()
        try:
            direccion_referencia = int(direccion_referencia)
            # Lee el código reubicable desde la UI
            texto = self.ui.binary_input.toPlainText()  
            texto_modificado = f"#{direccion_referencia}\n{texto}"

            # Define el comando según el sistema operativo
            comando = "./compilados/linkerLoader"
            if os.name != 'posix':  # Si es Windows, agrega ".exe"
                comando += ".exe"

            try:
                # Ejecuta el comando pasando los datos como entrada estándar
                proceso = subprocess.run(
                    [comando, str(direccion_referencia)],  # Argumentos
                    input=texto_modificado,  # Envía el código reubicable como entrada
                    text=True,  # Modo texto
                    capture_output=True  # Captura la salida del proceso
                )

                # Divide la salida en líneas
                resultado = proceso.stdout.strip().split("\n")

                # Mostrar la salida en el campo de texto
                self.ui.binary_input.setPlainText(proceso.stdout.strip())

                # Escribir la salida en la dirección relativa en la memoria
                for i, valor in enumerate(resultado):
                    direccion = direccion_referencia + i  # Ajusta la dirección según la salida
                    if direccion < len(self.memoria):
                        self.memoria[direccion] = valor  # Almacena en la memoria

                # Actualizar la tabla de memoria en la UI
                self.setCp(direccion_referencia)

                # Si hay errores, también los muestra
                if proceso.stderr:
                    print(f"Error en linkerLoader: {proceso.stderr}")
                    self.ui.Output.append("[Error Linker]: " + proceso.stderr)

            except FileNotFoundError:
                self.ui.Output.setPlainText("[Error]: No se encontró el ejecutable del linkerLoader.")
            except Exception as e:
                self.ui.Output.setPlainText("[Error inesperado]: " + str(e))
        except ValueError as e:
            print(f"Error: '{direccion_referencia}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
        
    def LeerDato(self,direccion):
        instruccion = self.memoria.leer_memoria(direccion)
        return self.EjecutarComando(instruccion)
        
    def LeerInstruccion(self):
        instruccion = self.memoria.leer_memoria(self.cp)
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":False} 
        try:
            self.resetBanderas()
            #Ejecuta instruccion
            self.EjecutarComando(instruccion)
            self.setCp(self.cp+1)      
        except ValueError as e:
            self.ui.Output.setPlainText("[Error Ejecutando]: "+ str(e))
            
    def LeerInstrucciones(self):
        instruccion = self.memoria.leer_memoria(self.cp)
        while(self.IdentificarComando(instruccion) != 'HALT' 
              and self.IdentificarComando(instruccion) != 'IN' 
              and self.memoria.leer_memoria(self.cp) != 0 ):
            self.LeerInstruccion()
        if(self.IdentificarComando(instruccion) == 'IN'):
            self.config_input = {"text":"","reg_input":reg,"Exxecute_all":True} 
            try:
                #Ejecuta instruccion
                self.EjecutarComando(instruccion)
                self.setCp(self.cp+1)      
            except ValueError as e:
                self.ui.Output.setPlainText("[Error Ejecutando]: "+ str(e))
        
    def EjecutarComando(self,instruccion):
        nombre_comando = self.IdentificarComando(instruccion)
        self.setDir(instruccion)
        funcion = self.funciones.get(nombre_comando)  # Obtener la función con el mismo nombre
            
        if funcion:
            try:
                # Asegurar que la instrucción se maneje como cadena binaria y tenga 32 bits
                binario = str(instruccion).zfill(32)  # Asegurar que tenga 32 bits, rellenando con ceros a la izquierda
                print("🚀 ~ instruccion:", str(funcion))
                resto_instruccion = binario[5:]  # Convertir los 27 bits restantes a entero
                return funcion(resto_instruccion)
            except ValueError:
                print("Error: La instrucción debe ser un número entero.")
        else:
            print(f"Error: La función {nombre_comando} no está definida.")

    def IdentificarComando(self,instruccion):
        commandos = [
            "NOP", "LOAD", "STORE", "MOVE", "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOR",
            "NOT", "SHL", "SHR", "ROL", "ROR", "JUMP", "BEQ", "BNE", "BLT", "JLE", "PUSH", 
            "POP", "CALL", "RET", "IN", "OUT", "CMP", "CLR", "LOADR", "STORER", "HALT"
        ]
        
        try:
            binario = str(instruccion).zfill(32)  # Asegurar que tenga 32 bits, llenando con ceros a la izquierda
            
            # Extraer los primeros 5 bits del binario
            opcode_binario = binario[:5]
            opcode = int(opcode_binario, 2)  # Convertir los primeros 5 bits a entero

            if 0 <= opcode < len(commandos):
                return commandos[opcode]
            else:
                print(f"Error: Código de instrucción fuera de rango ({opcode}).")
                return "ERROR"
        except ValueError:
            print("Error: La instrucción debe ser un número entero.")
            return "ERROR"

    def NOP(self,instruccion):
        type_dato = instruccion[:6]
        tipo_dato = int(type_dato, 2)
        
        # Determinar el tipo de dato según el valor de los primeros 6 bits
        if tipo_dato == 1:
            return GetBooleano(instruccion[6:])
        elif tipo_dato == 2:
            return GetNatural(instruccion[6:])
        elif tipo_dato == 3:
            return GetEntero(instruccion[6:])
        elif tipo_dato == 4:
            return GetFloat(instruccion[6:])
        elif tipo_dato == 5:
            return GetCaracterUtf16(instruccion[6:])
        else:
            print("Error: La instrucción debe ser un número entero.")
            return "ERROR"
        
    def LOAD(self,instruccion):
        reg_destino = int(instruccion[:2], 2)
        dir_origen = int(instruccion[2:], 2)
        self.guardar_en_registro(reg_destino,self.LeerDato(dir_origen))
      
    def STORE(self,instruccion):
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        self.memoria.escribir_memoria(reg_origen,self.LeerDato(dir_destino))
        return 0
        
    def MOVE(self,instruccion):
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_origen,self.LeerDato(reg_destino))
        return 0
        
    def ADD(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        suma = self.registro[reg_1] + self.registro[reg_2]
        if suma > 2097151:
            self.setDesb(1)
            self.setCarry(1)
        if suma == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,suma)
        return 0
        
    def SUB(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        resta = self.registro[reg_1] - self.registro[reg_2]
        if resta == 0:
            self.setZero(1)
        if resta < 0:
            self.setNegative(1)
        self.guardar_en_registro(reg_destino,resta)
        return 0
        
    def MUL(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        multi = self.registro[reg_1] * self.registro[reg_2]
        if multi > 2097151:
            self.setDesb(1)
            self.setCarry(1)
        if multi == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,multi)
        return 0
        
    def DIV(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        div = self.registro[reg_1] / self.registro[reg_2]
        if div == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,div)
        return 0
        
    def AND(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] & self.registro[reg_2]))
        return 0
        
    def OR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] | self.registro[reg_2]))
        return 0
        
    def NOR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(~(self.registro[reg_1] | self.registro[reg_2])))
        return 0
        
    def NOT(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        self.guardar_en_registro(reg_1,int(~(self.registro[reg_1])))
        return 0
        
    def SHL(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_1,self.registro[reg_1] << self.registro[reg_2])
        return 0
        
    def SHR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)  
        reg_2 = int(instruccion[2:4], 2) 
        self.guardar_en_registro(reg_1,self.registro[reg_1] >> self.registro[reg_2])
        return 0
        
    def ROL(self, instruccion):
        reg_1 = int(instruccion[:2], 2)  # Índice del registro destino
        reg_2 = int(instruccion[2:4], 2)  # Índice del registro que contiene el número de rotaciones

        tmp_reg = self.registro
        valor = tmp_reg[reg_1]  # Valor del registro a rotar
        n_bits = tmp_reg[reg_2]  # Número de bits a rotar

        BITS = 16
        n_bits %= BITS  # Asegurar que la rotación no exceda el tamaño del dato
        
        self.guardar_en_registro(reg_1,((valor << n_bits) & ((1 << BITS) - 1)) | (valor >> (BITS - n_bits)))
        return 0
        
    def ROR(self, instruccion):
        reg_1 = int(instruccion[:2], 2)  # Índice del registro destino
        reg_2 = int(instruccion[2:4], 2)  # Índice del registro que contiene el número de rotaciones

        tmp_reg = self.registro
        valor = tmp_reg[reg_1]  # Valor del registro a rotar
        n_bits = tmp_reg[reg_2]  # Número de bits a rotar

        BITS = 16
        n_bits %= BITS  # Asegurar que la rotación no exceda el tamaño del dato
        
        self.guardar_en_registro(reg_1,(valor >> n_bits) | ((valor & ((1 << n_bits) - 1)) << (BITS - n_bits)))
        return 0

    def JUMP(self,instruccion):
        dir_destino = int(instruccion, 2)        
        self.setCp(dir_destino)
        return 0

    def BEQ(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        if(self.registro[reg_1] == self.registro[reg_2]):
            self.setZero(1)
            self.setCp(dir_destino)

    def BNE(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] != self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def BLT(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] < self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def JLE(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] < self.registro[reg_2]:
            self.setNegative(1)            
        if self.registro[reg_1] == self.registro[reg_2]:
            self.setZero(1)
        
        if self.registro[reg_1] <= self.registro[reg_2]:
            self.setCp(dir_destino)

    def PUSH(self,instruccion):
        reg_index = int(instruccion[:2], 2)
        direccion = self.registro[reg_index]
        self.memoria.push_stack(direccion)
        return 0

    def POP(self,instruccion):
        reg_index = int(instruccion[:2], 2)
        direccion = self.memoria.pop_stack()
        self.guardar_en_registro(reg_index,direccion)
        return 0

    def CALL(self,instruccion):
        direccion = int(instruccion, 2)
        self.memoria.push_stack(self.cp)
        self.setCp(direccion)
        return 0

    def RET(self,instruccion):
        direccion = self.memoria.pop_stack()
        self.setCp(direccion-1)
        return 0

    def IN(self, instruccion):
        """Espera la entrada del usuario y la almacena en el registro correspondiente."""
        print("IN", instruccion)
        reg = int(instruccion[:2], 2)  # Obtener el índice del registro
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":self.config_input['Exxecute_all']}
        self.ui.input_button.setDisabled(False)
        self.ui.Read_Next_Instruction.setDisabled(True)
            
    def OUT(self,instruccion):
        reg_1 = int(instruccion[:2], 2)        
        self.ui.Output.setPlainText(str(self.registro[reg_1]))
        return 0

    def CMP(self,instruccion):
        print("CMP",instruccion)
        return 0

    def CLR(self,instruccion):
        print("CLR",instruccion)
        return 0

    def LOADR(self,instruccion):
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.registro[reg_destino] = self.registro[reg_origen]

    def STORER(self,instruccion):
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        self.memoria.escribir_memoria(reg_origen,self.LeerDato(dir_destino))
        return 0

    def HALT(self,instruccion):
        return 0  
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())