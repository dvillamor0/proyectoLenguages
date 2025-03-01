# proyectoLenguages

Este proyecto tiene como objetivo la implementación de herramientas para el procesamiento y ensamblaje de código, junto con el desarrollo de una interfaz gráfica de usuario (GUI) para su uso.

## Estructura de Directorios

### 1. `compilados`
Este directorio contiene los ejecutables generados del proceso de compilación.

### 2. `librerias`
Este directorio contiene ejemplos de código fuente en formato de texto. Estos son fragmentos de código que podrían ser utilizados o procesados por el ensamblador y otras herramientas.

### 3. `pruebas`
Contiene archivos de prueba utilizados para verificar el correcto funcionamiento de las herramientas y scripts desarrollados en el proyecto.

### 4. `README.md`
Archivo de documentación principal que proporciona una descripción general del proyecto, su propósito, cómo instalar y utilizar las herramientas, y cualquier otra información relevante para los desarrolladores o usuarios.

### 5. `src`
Este directorio contiene los archivos fuente de las herramientas que forman el proyecto.

- **analizador.l**: Código fuente en el lenguaje Lex que define el analizador lexico.
- **ensamblador.l**: Código fuente en el lenguaje Lex que define el ensamblador.
- **linkerLoader.l**: Código fuente en el lenguaje Lex que define el cargador-enlazador.
- **preprocessor.l**: Código fuente en el lenguaje Lex que define el preprocesador.

### 6. `vista`
Este directorio contiene los archivos relacionados con la interfaz gráfica de usuario (GUI) del proyecto.

- **Diseño_GUI.py**: Código fuente en Python que define la interfaz gráfica de usuario utilizando PyQt.
- **Diseño GUI.ui**: Archivo de diseño de la interfaz gráfica en formato XML, utilizado por el framework para generar la GUI.
- **prueba.py**: Archivo donde se encuentra el simulador del computador.

### 7. `ui`
- **main.py**: Archivo principal del proyecto en Python que ejecuta la aplicación y gestiona la interfaz gráfica.
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
    flex analizador.l
    gcc -o ..\compilados\analizador lex.yy.c -lfl

    flex ensamblador.l
    gcc -o ..\compilados\ensamblador lex.yy.c -lfl

    flex linkerLoader.l
    gcc -o ..\compilados\linkerLoader lex.yy.c -lfl

    flex preprocessor.l
    gcc -o ..\compilados\preprocessor lex.yy.c -lfl

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

   - preprocesador

      ```bash
         flex preprocesador.l &&
         mv lex.yy.c ../compilados/preprocesador.yy.c &&
         gcc -o ../compilados/preprocesador ../compilados/preprocesador.yy.c -lfl
         
   - compilador

      ```bash
         flex analizador_lexico.l &&
         mv lex.yy.c ../compilados/analizadorLexico.yy.c &&
         gcc -o ../compilados/compiler -I. -I../compilados \
         ../compilados/analizadorLexico.yy.c \
         ../compilados/analizador_sintactico.tab.c \
         ast.c \
         analizador_semantico.c \
         intermediate_code.c \
         -lfl

   - ensamblador
      ```bash
         flex ensamblador.l &&
         mv lex.yy.c ../compilados/ensamblador.yy.c &&
         gcc -o ../compilados/ensamblador ../compilados/ensamblador.yy.c -lfl -lm
   - enlazador
      ```bash
         flex linkerLoader.l &&
         mv lex.yy.c ../compilados/linkerLoader.yy.c &&
         gcc -o ../compilados/linkerLoader ../compilados/linkerLoader.yy.c -lfl -lm

### 2. **Pruebas**

   - Los archivos de prueba ubicados en `pruebas` contienen ejemplos y resultados esperados para cada herramienta. Puedes utilizarlos para verificar que los programas funcionan como se espera.

### 3. **Interfaz Gráfica**

   - La interfaz gráfica está construida utilizando Python y la biblioteca PyQt o similar. El archivo `main.py` es el punto de entrada principal para ejecutar la GUI.
   - El archivo `Diseño_GUI.ui` contiene el diseño visual de la interfaz que se puede modificar utilizando un editor visual compatible.

---