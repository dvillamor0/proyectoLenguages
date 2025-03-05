%{
    /**
     * @archivo: preprocesador.l
     * @descripción: Implementación de un preprocesador para manejo de directivas de importación
     * @autor: [Nombre del autor]
     * @fecha: [Fecha de creación/modificación]
     * @versión: 1.0
     */
    
    // Inclusión de bibliotecas estandar para entrada/salida, manejo de memoria y cadenas.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    /**
     * @constante: MAX_BUFFER
     * @descripción: Define el tamaño máximo del buffer para almacenar contenido de archivos
     * @valor: 1000 bytes
     */
    #define MAX_BUFFER 1000
    
    /**
     * @variable: buffer
     * @descripción: Buffer general para operaciones de lectura/escritura
     * @tamaño: MAX_BUFFER bytes
     */
    char buffer[MAX_BUFFER];
    
    /**
     * @variable: lib_content
     * @descripción: Buffer específico para almacenar el contenido de las bibliotecas importadas
     * @tamaño: MAX_BUFFER bytes
     */
    char lib_content[MAX_BUFFER];
    
    /**
     * @variable: import_active
     * @descripción: Bandera que indica si actualmente se está procesando una importación
     * @valores: 0 = no activo, 1 = activo
     * @inicialización: 0
     */
    int import_active = 0;

    /**
     * @función: process_import
     * @descripción: Procesa la directiva de importación leyendo y mostrando el contenido de una biblioteca
     * @parámetros: const char* lib_name - Nombre de la biblioteca a importar
     * @retorno: void
     */
    void process_import(const char* lib_name);
%}

%option noyywrap

/**
 * @sección: Definiciones de patrones léxicos
 * @descripción: Expresiones regulares para identificar diferentes tokens en el código fuente
 */
DIGIT    [0-9]
NUMBER   {DIGIT}+("."{DIGIT}+)?  
ID       [a-zA-Z][a-zA-Z0-9_]*
WS       [ \t]
NL       \r|\n|\r\n
COMMENT  #[^\r\n]*{NL}?

%%

^"#import"[ ]*"<"[^>]*">"{NL}? {
    char lib_name[100];
    sscanf(yytext, "#import <%[^>]>", lib_name);
    process_import(lib_name);
}

{COMMENT}    { 
    printf("\n");
}

{WS}        { 
    if (import_active == 0) {
        ECHO; 
    }
}

{NL}        {
    if (import_active == 0) {
        printf("\n");
    }
}

.           { 
    if (import_active == 0) {
        ECHO; 
    }
}

%%

/**
 * @función: process_import
 * @descripción: Lee y procesa el contenido de un archivo de biblioteca (.lib)
 *               e imprime su contenido en la salida estándar.
 *
 * @parámetros:
 *   - lib_name: Nombre de la biblioteca sin la extensión
 *
 * @funcionamiento:
 *   1. Construye la ruta completa al archivo de biblioteca
 *   2. Intenta abrir el archivo en modo lectura
 *   3. Si la apertura es exitosa, lee todo el contenido en un buffer
 *   4. Imprime el contenido en la salida estándar
 *   5. Cierra el archivo
 *
 * @manejo_errores:
 *   - Muestra un mensaje de error si no puede abrir el archivo
 *   - Controla el tamaño máximo de lectura para evitar desbordamientos
 *
 * @observaciones:
 *   - Utiliza la bandera import_active para evitar procesar el contenido
 *     de la biblioteca como parte del flujo léxico normal
 */
void process_import(const char* lib_name) {
    FILE* lib_file;
    char filename[120];
    
    snprintf(filename, sizeof(filename), "librerias/%s.lib", lib_name);
    
    lib_file = fopen(filename, "r");
    if (!lib_file) {
        fprintf(stderr, "Error: Cannot open library %s\n", filename);
        return;
    }
    
    import_active = 1;
    size_t n = fread(lib_content, 1, MAX_BUFFER - 1, lib_file);
    lib_content[n] = '\0';
    
    printf("%s\n\n", lib_content);
    
    import_active = 0;
    fclose(lib_file);
}

/**
 * @función: main
 * @descripción: Punto de entrada principal del programa que configura la entrada/salida
 *               y ejecuta el analizador léxico.
 *
 * @parámetros:
 *   - argc: Número de argumentos de línea de comandos
 *   - argv: Array de cadenas con los argumentos
 *
 * @retorno:
 *   - 0: Ejecución exitosa
 *   - 1: Error en los argumentos o al abrir archivos
 *
 * @uso_válido:
 *   programa <archivo_entrada> [archivo_salida]
 *
 * @manejo_errores:
 *   - Verifica que el número de argumentos sea correcto (1 o 2 argumentos)
 *   - Valida que se pueda abrir el archivo de entrada
 *   - Verifica que se pueda crear/abrir el archivo de salida (si se especifica)
 *
 * @flujo:
 *   1. Valida argumentos de línea de comandos
 *   2. Abre el archivo de entrada
 *   3. Configura la redirección de salida (opcional)
 *   4. Ejecuta el analizador léxico (yylex)
 *   5. Libera recursos y termina
 */
int main(int argc, char** argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <input_file> [output_file]\n", argv[0]);
        return 1;
    }
    
    FILE* input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Error: Cannot open input file %s\n", argv[1]);
        return 1;
    }
    yyin = input;
    
    if (argc == 3) {
        FILE* output = freopen(argv[2], "w", stdout);
        if (!output) {
            fprintf(stderr, "Error: Cannot open output file %s\n", argv[2]);
            return 1;
        }
    }
    
    yylex();
    
    fclose(yyin);
    return 0;
}