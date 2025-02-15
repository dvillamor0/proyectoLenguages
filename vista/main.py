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
from PyQt5.QtWidgets import QApplication, QMainWindow
from Diseño_GUI import *
from prueba import *
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_values()
        
        self.ui.Boton_Comp.clicked.connect(self.printer)
        self.ui.Boton_Ens.clicked.connect(self.cambiar_valores)
        self.ui.Boton_Carg.clicked.connect(self.ejecutar)
        self.ui.Siguiente.clicked.connect(self.siguiente_inst)
        self.ui.Linker.clicked.connect(self.ejecutar_comando)

    def printer(self):
        limpiar()
        text = self.ui.Input.toPlainText()
        
        with open("Input.txt", "w", encoding="utf-8") as file:
            file.write(text)

    def ejecutar_comando(self):
        # Comando a ejecutar
        comando = "ensamblador.exe < Input.txt > Linker.txt"
        
        try:
            # Ejecutar el comando
            resultado = subprocess.run(comando, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Comando ejecutado con éxito: {resultado.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e.stderr}")
        
        lista_de_datos = []

        # Leer el archivo y agregar el contenido a la lista
        with open("Linker.txt", 'r') as archivo:
            for linea in archivo:
                lista_de_datos.append(linea.strip())

        # Mostrar la lista
        self.ui.listareubi.clear()
        self.ui.listareubi.addItems(lista_de_datos)

    def cambiar_valores(self):
        global cp,memoria
        comando = "linkerLoader.exe < Linker.txt > memoria.txt"
        
        try:
            # Ejecutar el comando
            resultado = subprocess.run(comando, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Comando ejecutado con éxito: {resultado.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {e.stderr}")
        
        memoria = []

        # Leer el archivo y agregar el contenido a la lista
        with open("memoria.txt", 'r') as archivo:
            contenido = archivo.read().strip()

        # Longitud de cada parte
        tamaño_parte = 32
        memoria = [contenido[i:i + tamaño_parte] for i in range(0, len(contenido), tamaño_parte)]
        tmp= self.ui.CP_Set.toPlainText()
        cp = int(tmp)
        self.set_values()

    def ejecutar(self):
        res = self.factorial()
        dir = self.ui.DIR.toPlainText()
        print(res)
        self.ui.Output.setText(res)
        self.set_values()
        
    def set_values(self):
        global memoria
        self.set_Control_Values()
        self.set_REG_Values()
        self.ui.listamem.clear()
        self.ui.listamem.addItems(memoria)
        
        
    def siguiente_inst(self):
        try:
            ejecutar_instruccion()
        except Exception as e:
            res= "No hay más instrucciones"
            self.ui.Consola.setText(res)
        self.set_values()

    def set_REG_Values(self):
        self.ui.REG_Carry.setText(str(carry))
        self.ui.REG_Zero.setText(str(zero))
        self.ui.REG_Neg.setText(str(negativo))
        self.ui.REG_Desb.setText(str(desvordamiento))
        self.ui.REG_A.setText(str(reg[0]))
        self.ui.REG_B.setText(str(reg[1]))
        self.ui.REG_C.setText(str(reg[2]))
        self.ui.REG_D.setText(str(reg[3]))
        #binario_formateado = binario.zfill(16)
        # self.ui.BIN_Carry.setText(bin(carry))
        # self.ui.BIN_Zero.setText(bin(zero))
        # self.ui.BIN_Neg.setText(bin(negativo))
        # self.ui.BIN_Desb.setText(bin(desvordamiento))
        # self.ui.BIN_A.setText(bin(reg[0]))
        # self.ui.BIN_B.setText(bin(reg[1]))
        # self.ui.BIN_C.setText(bin(reg[2]))
        # self.ui.BIN_D.setText(bin(reg[3]))

    def set_Control_Values(self):
        self.ui.IR_Value.setText(str(ir))
        self.ui.CP_Value.setText(str(cp))
    
    def factorial(self):
        print(cp, len(memoria))
        while cp < len(memoria):
            try:
                ejecutar_instruccion()
                print("💀")
            except Exception as e:
                print("❤️")
                return "el resultado es: " #direccion de memoria donde se guarda el resultado
                
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())