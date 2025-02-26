%{
    // Inclusión de bibliotecas estandar para entrada/salida, manejo de memoria y cadenas.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    // Definicion del tamaño maximo del buffer.
    #define MAX_BUFFER 1000
    char buffer[MAX_BUFFER];
    char lib_content[MAX_BUFFER];
    int import_active = 0;

    // Declaracion de la funcion que procesa la importacion de bibliotecas.
    void process_import(const char* lib_name);
%}

%option noyywrap

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

/*
 * Funcion: process_import
 * -------------------------
 * Lee el contenido de una biblioteca y lo imprime.
 *
 * Parametro:
 *   lib_name - Nombre de la biblioteca sin la extension.
 *
 * Procedimiento:
 *   - Construye el nombre del archivo agregando ".lib".
 *   - Abre el archivo y, si se abre correctamente, lee su contenido.
 *   - Imprime el contenido y cierra el archivo.
 */
void process_import(const char* lib_name) {
    FILE* lib_file;
    char filename[120];
    
    snprintf(filename, sizeof(filename), "%s.lib", lib_name);
    
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

/*
 * Funcion: main
 * ---------------
 * Funcion principal del programa.
 *
 * Procedimiento:
 *   - Verifica que se proporcione uno o dos argumentos.
 *   - Abre el archivo de entrada y, si se especifica, redirige la salida a un archivo.
 *   - Ejecuta el analizador lexico y cierra el archivo de entrada.
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
