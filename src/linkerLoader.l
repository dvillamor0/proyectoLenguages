%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

/**
 * @brief Imprime un número en formato binario utilizando exactamente 21 bits
 * 
 * Esta función convierte un número entero a su representación binaria
 * y lo escribe en el archivo de salida especificado, asegurando que
 * siempre se impriman exactamente 21 bits (desde el más significativo al menos).
 * 
 * @param output Puntero al archivo donde se escribirá la salida
 * @param num Número entero a convertir y mostrar en binario
 */
void print_binary(FILE* output, int num) {
    unsigned int mask = 1 << 20; // Mascara para el bit mas significativo (bit 20)
    
    // Imprimir los 21 bits
    for (int i = 0; i < 21; i++) {
        if (num & mask) {
            fprintf(output, "1");
        } else {
            fprintf(output, "0");
        }
        mask >>= 1;  // Desplazar la mascara para el siguiente bit
    }
}

/**
 * @brief Verifica si una línea contiene una dirección relativa entre paréntesis
 * 
 * Una dirección relativa se identifica por la presencia de paréntesis
 * de apertura y cierre en la línea de texto.
 * 
 * @param line Cadena de texto a analizar
 * @return 1 si la línea contiene una dirección relativa, 0 en caso contrario
 */
int contains_relative_address(const char* line) {
    return (strstr(line, "(") != NULL && strstr(line, ")") != NULL);
}

/**
 * @brief Extrae el valor numérico de una dirección relativa entre paréntesis
 * 
 * Busca el primer paréntesis de apertura y el primer paréntesis de cierre
 * en la línea, y extrae el número entero que se encuentra entre ellos.
 * 
 * @param line Cadena de texto de la cual extraer la dirección
 * @return El valor numérico de la dirección relativa, o 0 si no se encuentra
 */
int extract_address(const char* line) {
    const char* start = strchr(line, '(');
    if (start == NULL) return 0;
    
    const char* end = strchr(start, ')');
    if (end == NULL) return 0;
    
    // Crear una subcadena para el numero
    int len = end - start - 1;
    char num_str[32] = {0};
    strncpy(num_str, start + 1, len);
    
    return atoi(num_str);
}

/**
 * @brief Reemplaza una dirección relativa por su equivalente absoluta en formato binario
 * 
 * Esta función toma una línea de texto que contiene una dirección relativa,
 * calcula su dirección absoluta sumando la base, y reemplaza la dirección relativa
 * con la representación binaria de 21 bits de la dirección absoluta.
 * 
 * @param line Línea de texto original con la dirección relativa
 * @param rel_addr Valor de la dirección relativa
 * @param base_addr Dirección base para el cálculo de la dirección absoluta
 * @return Puntero a una cadena estática con la línea modificada
 */
char* replace_address(const char* line, int rel_addr, int base_addr) {
    static char result[1024];
    const char* start = strchr(line, '(');
    const char* end = strchr(line, ')');
    
    if (start == NULL || end == NULL) {
        strcpy(result, line);
        return result;
    }
    
    // Calcular la direccion absoluta
    int abs_addr = base_addr + rel_addr;
    
    // Copiar la parte antes del parentesis
    int prefix_len = start - line;
    strncpy(result, line, prefix_len);
    result[prefix_len] = '\0';
    
    // Anadir la direccion absoluta en binario
    char binary[32] = {0};
    sprintf(binary, "");
    for (int i = 20; i >= 0; i--) {
        binary[20-i] = ((abs_addr >> i) & 1) ? '1' : '0';
    }
    binary[21] = '\0';
    
    strcat(result, binary);
    
    // Anadir la parte despues del parentesis
    strcat(result, end + 1);
    
    return result;
}

// Variable global que almacena la dirección base actual para cálculos de relocalización
int direccionInicial = 0;  // Direccion base para la relocalizacion

%}

%option noyywrap

/* Regular definitions */
delim       [ \t\n]
ws          {delim}+
digit       [0-9]
number      {digit}+(\.{digit}+)?(e[+-]?{digit}+)?

relative    \#([0-9]+)      
dir         \([0-9]+\)       

%%
{ws}        { fprintf(yyout, "\n"); }

{relative}  { 
    direccionInicial = atoi(yytext + 1); 
    fprintf(yyout, "\n");  
}

{dir}       { 
    int dir_value = atoi(yytext + 1); 
    int suma = direccionInicial + dir_value;
    print_binary(yyout, suma);  
}

.|\n { fprintf(yyout, "%s", yytext); }

%%

/**
 * @brief Procesa un archivo de entrada, reemplazando direcciones relativas por absolutas
 * 
 * Esta función lee un archivo línea por línea, identifica las direcciones relativas,
 * las convierte a direcciones absolutas en formato binario, y escribe el resultado
 * en un archivo de salida.
 * 
 * @param input_file Ruta al archivo de entrada
 * @param output_file Ruta al archivo de salida
 * @param base_address Dirección base para los cálculos de relocalización
 */
void process_file(const char* input_file, const char* output_file, int base_address) {
    FILE* in = fopen(input_file, "r");
    FILE* out = fopen(output_file, "w");
    
    if (!in || !out) {
        fprintf(stderr, "Error opening files\n");
        if (in) fclose(in);
        if (out) fclose(out);
        return;
    }
    
    char line[1024];
    
    // Establecer la direccion base
    direccionInicial = base_address;
    
    while (fgets(line, sizeof(line), in)) {
        // Eliminar el salto de linea final si existe
        size_t len = strlen(line);
        if (len > 0 && line[len-1] == '\n') {
            line[len-1] = '\0';
        }
        
        if (contains_relative_address(line)) {
            // La linea contiene una direccion relativa
            int rel_addr = extract_address(line);
            char* new_line = replace_address(line, rel_addr, direccionInicial);
            fprintf(out, "%s\n", new_line);
        } else {
            // La linea no contiene direccion relativa, copiarla tal cual
            fprintf(out, "%s\n", line);
        }
    }
    
    fclose(in);
    fclose(out);
    printf("Processing complete. Output written to %s\n", output_file);
}

/**
 * @brief Función principal del programa
 * 
 * Procesa los argumentos de línea de comandos, establece los valores predeterminados
 * si es necesario, y llama a la función principal de procesamiento.
 * 
 * @param argc Número de argumentos de línea de comandos
 * @param argv Array de cadenas con los argumentos de línea de comandos
 * @return 0 si la ejecución fue exitosa, 1 en caso de error
 */
int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Usage: %s [base_address] [input_file] [output_file]\n", argv[0]);
        printf("  base_address: Base address for relocation (default: 0)\n");
        printf("  input_file: Binary input file (default: output.bin)\n");
        printf("  output_file: Output file (default: executable.bin)\n");
        return 1;
    }
    
    int base_address = 0;
    const char* input_file = "output.bin";
    const char* output_file = "executable.bin";
    
    if (argc >= 2) {
        base_address = atoi(argv[1]);
    }
    
    if (argc >= 3) {
        input_file = argv[2];
    }
    
    if (argc >= 4) {
        output_file = argv[3];
    }
    
    printf("Loading from: %s\n", input_file);
    printf("Base address: %d\n", base_address);
    printf("Output file: %s\n", output_file);
    
    process_file(input_file, output_file, base_address);
    
    return 0;
}