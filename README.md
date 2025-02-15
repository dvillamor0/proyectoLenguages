# proyectoLenguages

Este proyecto tiene como objetivo la implementación de herramientas para el procesamiento y ensamblaje de código, junto con el desarrollo de una interfaz gráfica de usuario (GUI) para su uso.

## Estructura de Directorios

La estructura del proyecto es la siguiente:

.
├── compilados

│   ├── analizador.exe

│   ├── ensamblador

│   ├── ensamblador.exe

│   ├── lex.yy.c

│   ├── linkerLoader

│   ├── linkerLoader.exe

│   └── preprocessor.exe

├── librerias

│   ├── binarySearch.txt

│   ├── bubbleSort.txt

│   ├── factorial copy.txt

│   └── factorial.txt

├── pruebas

│   ├── ejemploEnsamblador.txt

│   ├── ejemplolinker.txt

│   ├── Input.txt

│   ├── salidaCargador.txt

│   └── salidaEnsamblador.txt

├── README.md

├── src

│   ├── analizador.l

│   ├── ensamblador.l

│   ├── linkerLoader.l

│   └── preprocessor.l

└── vista

    ├── Diseño_GUI.py

    ├── Diseño GUI.ui

    ├── Linker.txt

    ├── main.py

    ├── memoria.txt

    └── prueba.py


### 1. `compilados`
Este directorio contiene los ejecutables generados y los archivos intermedios del proceso de compilación.

### 2. `librerias`
Este directorio contiene ejemplos de código fuente en formato de texto. Estos son fragmentos de código que podrían ser utilizados o procesados por el ensamblador y otras herramientas.

### 3. `pruebas`
Contiene archivos de prueba utilizados para verificar el correcto funcionamiento de las herramientas y scripts desarrollados en el proyecto.

### 4. `README.md`
Archivo de documentación principal que proporciona una descripción general del proyecto, su propósito, cómo instalar y utilizar las herramientas, y cualquier otra información relevante para los desarrolladores o usuarios.

### 5. `src`
Este directorio contiene los archivos fuente de las herramientas que forman el proyecto.

- **analizador.l**: Código fuente en el lenguaje Lex que define el analizador lexical.
- **ensamblador.l**: Código fuente en el lenguaje Lex que define el ensamblador.
- **linkerLoader.l**: Código fuente en el lenguaje Lex que define el cargador y enlazador.
- **preprocessor.l**: Código fuente en el lenguaje Lex que define el preprocesador.

### 6. `vista`
Este directorio contiene los archivos relacionados con la interfaz gráfica de usuario (GUI) del proyecto.

- **Diseño_GUI.py**: Código fuente en Python que define la interfaz gráfica de usuario utilizando PyQt o similar.
- **Diseño GUI.ui**: Archivo de diseño de la interfaz gráfica en formato XML, utilizado por el framework para generar la GUI.
- **Linker.txt**: Archivo de texto que podría contener información de configuración o salida relacionada con el cargador y enlazador.
- **main.py**: Archivo principal del proyecto en Python que ejecuta la aplicación y gestiona la interfaz gráfica.
- **memoria.txt**: Archivo de texto que podría contener datos relacionados con la memoria, utilizados en la interfaz o pruebas.
- **prueba.py**: Archivo de prueba en Python para verificar funcionalidades antes de integrarlas con la GUI.

---

## Guía de Uso

### 1. **Compilación**

Para compilar el proyecto, necesitas generar los ejecutables a partir de los archivos de código fuente `.l` ubicados en el directorio `src`. Esto se puede hacer utilizando **Flex** (para generar los analizadores léxicos) y **GCC** (para compilar los archivos C generados por Flex). A continuación se detallan los pasos para compilar en **Windows** y **Linux**, asegurándonos de que los ejecutables se guarden en el directorio `compilados`.

#### En Windows

1. **Instalación de herramientas**:
   - **Flex**: Puedes instalar Flex a través de [Cygwin](https://www.cygwin.com/) o utilizando el paquete [WinFlexBison](https://github.com/lexxmark/winflexbison).
   - **GCC**: Puedes instalar GCC a través de [MinGW](http://mingw-w64.org/doku.php) o usar [MSYS2](https://www.msys2.org/).

2. **Generación de los archivos fuente en C**:
   Para generar los archivos `.c` a partir de los archivos `.l`, abre una terminal (como Cygwin o el terminal de MSYS2) y navega al directorio `src`. Luego, ejecuta el siguiente comando para cada archivo `.l`:

   ```bash
    flex analizador.l -o ../compilados/lex.yy.c
    flex ensamblador.l -o ../compilados/lex.yy.c
    flex linkerLoader.l -o ../compilados/lex.yy.c
    flex preprocessor.l -o ../compilados/lex.yy.c


    gcc -o ../compilados/analizador.exe ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/ensamblador.exe ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/linkerLoader.exe ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/preprocessor.exe ../compilados/lex.yy.c -lfl

    ```

#### En Linux

1. **Instalación de herramientas**:
   - **Flex**: Puedes instalar Flex utilizando el siguiente comando en una terminal:
     ```bash
     sudo apt-get install flex
     ```
   - **GCC**: Si no tienes GCC instalado, puedes instalarlo con:
     ```bash
     sudo apt-get install build-essential
     ```

2. **Generación de los archivos fuente en C**:
   Al igual que en Windows, navega al directorio `src` y ejecuta el siguiente comando para cada archivo `.l`:

   ```bash
    flex analizador.l -o ../compilados/lex.yy.c
    flex ensamblador.l -o ../compilados/lex.yy.c
    flex linkerLoader.l -o ../compilados/lex.yy.c
    flex preprocessor.l -o ../compilados/lex.yy.c


    gcc -o ../compilados/analizador ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/ensamblador ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/linkerLoader ../compilados/lex.yy.c -lfl
    gcc -o ../compilados/preprocessor ../compilados/lex.yy.c -lfl

    ```

### 2. **Pruebas**

   - Los archivos de prueba ubicados en `pruebas` contienen ejemplos y resultados esperados para cada herramienta. Puedes utilizarlos para verificar que los programas funcionan como se espera.

### 3. **Interfaz Gráfica**

   - La interfaz gráfica está construida utilizando Python y la biblioteca PyQt o similar. El archivo `main.py` es el punto de entrada principal para ejecutar la GUI.
   - El archivo `Diseño_GUI.ui` contiene el diseño visual de la interfaz que se puede modificar utilizando un editor visual compatible.

---