#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "analizador_sintactico.tab.h"
#define DEBUG 1  // Cambiar a 0 para desactivar la depuración

/**
 * Macro para escritura de mensajes de depuración al archivo log.
 * Solo escribe si DEBUG está activado.
 */
#define LOG(fmt, ...) \
    if (DEBUG) { \
        FILE *debug_file = fopen("debug_intermediate.log", "a"); \
        fprintf(debug_file, fmt, ##__VA_ARGS__); \
        fclose(debug_file); \
    }

/**
 * Tabla de símbolos externa que contiene los identificadores del programa.
 * Almacena nombres, tipos y valores para cada símbolo encontrado durante
 * el análisis sintáctico.
 */
extern struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
        unsigned int natural_value;
    } value;
} symbol_table[];

/**
 * Estructura para gestionar los nombres temporales y etiquetas
 * durante la generación de código intermedio.
 * - next_temp: Contador para el siguiente temporal
 * - temp_names: Array de nombres de temporales
 * - capacity: Capacidad actual del array
 * - next_label: Contador para la siguiente etiqueta
 */
typedef struct {
    int next_temp;
    char **temp_names;
    int capacity;
    int next_label;
} TempManager;

static TempManager *temp_mgr;
static char *generate_code(Node *node, FILE *output);

/**
 * Inicializa el administrador de temporales y etiquetas.
 * Asigna memoria para la estructura y para el array de nombres con una
 * capacidad inicial de 100 elementos.
 * 
 * @return Puntero al TempManager inicializado
 */
static TempManager *init_temp_manager() {
    TempManager *mgr = malloc(sizeof(TempManager));
    mgr->next_temp = 1;
    mgr->next_label = 1;
    mgr->capacity = 100;
    mgr->temp_names = malloc(sizeof(char*) * mgr->capacity);
    return mgr;
}

/**
 * Genera un nuevo nombre para una variable temporal (t1, t2, etc.).
 * Si se alcanza la capacidad actual, duplica el tamaño del array.
 * 
 * @return String con el nombre del nuevo temporal
 */
static char *new_temp() {
    if (temp_mgr->next_temp >= temp_mgr->capacity) {
        temp_mgr->capacity *= 2;
        temp_mgr->temp_names = realloc(temp_mgr->temp_names, sizeof(char*) * temp_mgr->capacity);
    }
    
    char *temp = malloc(20);
    sprintf(temp, "t%d", temp_mgr->next_temp++);
    return temp;
}

/**
 * Genera un nuevo nombre para una etiqueta (L1, L2, etc.)
 * Utilizado para saltos en estructuras de control.
 * 
 * @return String con el nombre de la nueva etiqueta
 */
static char *new_label() {
    char *label = malloc(20);
    sprintf(label, "L%d", temp_mgr->next_label++);
    return label;
}

/**
 * Obtiene el nombre de un símbolo de la tabla de símbolos.
 * 
 * @param symbol_index Índice en la tabla de símbolos
 * @return Nombre del símbolo
 */
static char *get_symbol_name(int symbol_index) {
    return symbol_table[symbol_index].name;
}

/**
 * Procesa operaciones binarias (suma, resta, multiplicación, división, comparaciones)
 * y genera el código intermedio correspondiente.
 * 
 * @param node Nodo del AST que representa la operación binaria
 * @param output Archivo donde se escribe el código intermedio
 * @return Nombre del temporal que almacena el resultado
 */
static char *process_binary_op(Node *node, FILE *output) {
    char *left = generate_code(node->left, output);
    char *right = generate_code(node->right, output);
    char *temp = new_temp();
    
    switch (node->type) {
        case NODE_ADD:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
            LOG("%s = %s + %s\n", temp, left, right);
            break;
        case NODE_SUB:
            fprintf(output, "%s = %s - %s\n", temp, left, right);
            LOG("%s = %s - %s\n", temp, left, right);
            break;
        case NODE_MUL:
            fprintf(output, "%s = %s * %s\n", temp, left, right);
            LOG("%s = %s * %s\n", temp, left, right);
            break;
        case NODE_DIV:
            fprintf(output, "%s = %s / %s\n", temp, left, right);
            LOG("%s = %s / %s\n", temp, left, right);
            break;
        case NODE_BINARY_OP:
            switch (node->symbol_index) {
                case TOKEN_RELOP_EQ:
                    fprintf(output, "%s = %s != %s\n", temp, left, right);
                    LOG("%s = %s != %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_NE:
                    fprintf(output, "%s = %s == %s\n", temp, left, right);
                    LOG("%s = %s == %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LT:
                    fprintf(output, "%s = %s >= %s\n", temp, left, right);
                    LOG("%s = %s >= %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LE:
                    fprintf(output, "%s = %s > %s\n", temp, left, right);
                    LOG("%s = %s > %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GT:
                    fprintf(output, "%s = %s <= %s\n", temp, left, right);
                    LOG("%s = %s <= %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GE:
                    fprintf(output, "%s = %s < %s\n", temp, left, right);
                    LOG("%s = %s < %s\n", temp, left, right);
                    break;
                case TOKEN_PLUS:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
                    LOG("%s = %s + %s\n", temp, left, right);
                    break;
                case TOKEN_MINUS:
                    fprintf(output, "%s = %s - %s\n", temp, left, right);
                    LOG("%s = %s - %s\n", temp, left, right);
                    break;
                case TOKEN_MULT:
                    fprintf(output, "%s = %s * %s\n", temp, left, right);
                    LOG("%s = %s * %s\n", temp, left, right);
                    break;
                case TOKEN_DIV:
                    fprintf(output, "%s = %s / %s\n", temp, left, right);
                    LOG("%s = %s / %s\n", temp, left, right);
                    break;
                default:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
                    LOG("%s = %s + %s\n", temp, left, right);
            }
            break;
        default:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
            LOG("%s = %s + %s\n", temp, left, right);
    }
    
    return temp;
}

/**
 * Procesa la definición de una función en el AST y genera el código intermedio.
 * Incluye declaraciones de parámetros y el cuerpo de la función.
 * 
 * @param node Nodo del AST que representa la función
 * @param output Archivo de salida
 */
static void process_function_def(Node *node, FILE *output) {
    fprintf(output, "begin_func %s\n", get_symbol_name(node->symbol_index));
    LOG("begin_func %s\n", get_symbol_name(node->symbol_index))
    
    if (node->left) {
        Node *param = node->left;
        while (param) {
            fprintf(output, "param %s\n", get_symbol_name(param->symbol_index));
            LOG("param %s\n", get_symbol_name(param->symbol_index));
            param = param->next;
        }
    }
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "end_func\n\n");
    LOG("end_func\n\n");
}

/**
 * Procesa una estructura condicional (if) y genera el código intermedio con
 * las etiquetas de salto correspondientes.
 * 
 * @param node Nodo del AST que representa la estructura if
 * @param output Archivo de salida
 */
static void process_if_statement(Node *node, FILE *output) {
    char *condition = generate_code(node->left, output);
    char *label_else = new_label();
    char *label_end = new_label();
    
    fprintf(output, "ifz %s goto %s\n", condition, label_else);
    LOG("ifz %s goto %s\n", condition, label_else);
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "goto %s\n", label_end);
    LOG("goto %s\n", label_end)
    fprintf(output, "%s:\n", label_else);
    LOG("%s:\n", label_else)
    fprintf(output, "%s:\n", label_end);
    LOG("%s:\n", label_end)
}

/**
 * Procesa un bucle while y genera el código intermedio con las etiquetas
 * para el inicio y fin del bucle.
 * 
 * @param node Nodo del AST que representa el bucle while
 * @param output Archivo de salida
 */
static void process_while_statement(Node *node, FILE *output) {
    char *label_start = new_label();
    char *label_end = new_label();
    
    fprintf(output, "%s:\n", label_start);
    LOG( "%s:\n", label_start)
    char *condition = generate_code(node->left, output);
    fprintf(output, "ifz %s goto %s\n", condition, label_end);
    LOG( "ifz %s goto %s\n", condition, label_end)
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "goto %s\n", label_start);
    LOG( "goto %s\n", label_start)
    fprintf(output, "%s:\n", label_end);
    LOG( "%s:\n", label_end)
}

/**
 * Procesa una llamada a función y genera el código intermedio necesario.
 * Prepara los parámetros de la llamada y asigna el resultado a un temporal.
 * 
 * @param node Nodo del AST que representa la llamada a función
 * @param output Archivo de salida
 * @return Nombre del temporal que contiene el resultado de la llamada
 */
static char *process_function_call(Node *node, FILE *output) {
    Node *arg = node->right;
    int arg_count = 0;
    
    while (arg) {
        char *arg_result = generate_code(arg, output);
        fprintf(output, "param %s\n", arg_result);
        LOG("param %s\n", arg_result);
        arg = arg->next;
        arg_count++;
    }
    
    char *temp = new_temp();
    char *func_name = get_symbol_name(node->left->symbol_index);
    fprintf(output, "%s = call %s, %d\n", temp, func_name, arg_count);
    LOG("%s = call %s, %d\n", temp, func_name, arg_count);
    
    return temp;
}

/**
 * Procesa un literal de array (ej: [1, 2, 3]) y genera el código para
 * crear y llenar un array con los elementos dados.
 * 
 * @param node Nodo que representa el literal de array
 * @param output Archivo de salida
 * @return Nombre del temporal que contiene el array
 */
static char *process_array_literal(Node *node, FILE *output) {
    // Contar los elementos en el array
    int count = 0;
    Node *element = node->left;
    while (element) {
        count++;
        element = element->next;
    }
    
    // Crear un nuevo temporal para el array
    char *array_temp = new_temp();
    
    // Reservar espacio para el array
    fprintf(output, "%s = new_array %d\n", array_temp, count);
    LOG("%s = new_array %d\n", array_temp, count);
    
    // Inicializar cada elemento
    element = node->left;
    int index = 0;
    
    while (element) {
        char *elem_value = generate_code(element, output);
        fprintf(output, "%s[%d] = %s\n", array_temp, index, elem_value);
        LOG("%s[%d] = %s\n", array_temp, index, elem_value);
        
        element = element->next;
        index++;
    }
    
    return array_temp;
}

/**
 * Procesa un acceso a elemento de array (ej: arr[i]) y genera
 * el código intermedio para obtener el valor.
 * 
 * @param node Nodo que representa el acceso al array
 * @param output Archivo de salida
 * @return Nombre del temporal con el valor obtenido
 */
static char *process_array_access(Node *node, FILE *output) {
    char *array_name = get_symbol_name(node->left->symbol_index);
    char *index = generate_code(node->right, output);
    char *temp = new_temp();
    
    // Acceder al elemento del array
    fprintf(output, "%s = %s[%s]\n", temp, array_name, index);
    LOG("%s = %s[%s]\n", temp, array_name, index);
    
    return temp;
}

/**
 * Procesa una asignación a elemento de array (ej: arr[i] = valor) y
 * genera el código intermedio correspondiente.
 * 
 * @param node Nodo que representa la asignación a array
 * @param output Archivo de salida
 */
static void process_array_assignment(Node *node, FILE *output) {
    // Obtener información de acceso al array
    char *array_name = get_symbol_name(node->left->left->symbol_index);
    char *index = generate_code(node->left->right, output);
    
    // Obtener el valor a asignar
    char *value = generate_code(node->right, output);
    
    // Generar la asignación
    fprintf(output, "%s[%s] = %s\n", array_name, index, value);
    LOG("%s[%s] = %s\n", array_name, index, value);
}

/**
 * Procesa una declaración de array (ej: int arr[10]) y genera
 * el código para crear el array.
 * 
 * @param node Nodo que representa la declaración de array
 * @param output Archivo de salida
 */
static void process_array_declaration(Node *node, FILE *output) {
    char *array_name = get_symbol_name(node->left->symbol_index);
    
    // Verificar si es una declaración con inicialización
    if (node->right && node->right->type == NODE_ARRAY_INIT) {
        // Obtener expresión de tamaño
        char *size = generate_code(node->right->left->left, output);
        
        // Obtener expresión de inicialización
        char *init = generate_code(node->right->right, output);
        
        // Reservar e inicializar
        fprintf(output, "%s = new_array %s\n", array_name, size);
        LOG("%s = new_array %s\n", array_name, size);
        
        fprintf(output, "%s = %s\n", array_name, init);
        LOG("%s = %s\n", array_name, init);
    } else {
        // Declaración simple con tamaño
        char *size = generate_code(node->right, output);
        
        // Reservar array
        fprintf(output, "%s = new_array %s\n", array_name, size);
        LOG("%s = new_array %s\n", array_name, size);
    }
}

/**
 * Función principal de generación de código que recorre el AST recursivamente.
 * Determina el tipo de nodo y llama a la función específica correspondiente.
 * 
 * @param node Nodo actual del AST
 * @param output Archivo de salida
 * @return Resultado de la operación (nombre de temporal o variable)
 */
static char *generate_code(Node *node, FILE *output) {
    if (!node) return NULL;
    
    char *result = NULL;
    
    switch (node->type) {
        case NODE_PROGRAM:
            if (node->left) result = generate_code(node->left, output);
            break;
            
        case NODE_FUNCTION:
            process_function_def(node, output);
            break;
            
        case NODE_BLOCK:
            if (node->left) {
                result = generate_code(node->left, output);
            }
            break;
            
        case NODE_DECLARATION:
        case NODE_ASSIGNMENT: {
            char *expr_result = generate_code(node->right, output);
            char *var_name = get_symbol_name(node->left->symbol_index);
            fprintf(output, "%s = %s\n", var_name, expr_result ? expr_result : "0");
            result = var_name;
            break;
        }
            
        case NODE_RETURN: {
            char *expr_result = generate_code(node->left, output);
            fprintf(output, "return %s\n", expr_result);
            break;
        }
            
        case NODE_BINARY_OP:
        case NODE_ADD:
        case NODE_SUB:
        case NODE_MUL:
        case NODE_DIV:
            result = process_binary_op(node, output);
            break;
            
        case NODE_NUMBER: {
            char *temp = new_temp();
            
            // Verificar si es un número natural en la tabla de símbolos
            if (symbol_table[node->symbol_index].type == 3) {  // 3 = SYMTAB_NATURAL
                // Para números naturales, usar el valor numérico directamente
                unsigned int natural_value = symbol_table[node->symbol_index].value.natural_value;
                fprintf(output, "%s = %u\n", temp, natural_value);
                LOG("%s = %u (natural)\n", temp, natural_value);
            } else {
                // Para números regulares, usar la representación en string como antes
                const char *num_str = get_symbol_name(node->symbol_index);
                fprintf(output, "%s = %s\n", temp, num_str);
                LOG("%s = %s\n", temp, num_str);
            }
            
            return temp;
        }
        
        case NODE_IDENTIFIER:
            result = get_symbol_name(node->symbol_index);
            break;
            
        case NODE_FUNCTION_CALL:
            result = process_function_call(node, output);
            break;
            
        case NODE_IF:
            process_if_statement(node, output);
            break;
            
        case NODE_WHILE:
            process_while_statement(node, output);
            break;
            
        // Casos para operaciones de array
        case NODE_ARRAY_LITERAL:
            result = process_array_literal(node, output);
            break;
            
        case NODE_ARRAY_ACCESS:
            result = process_array_access(node, output);
            break;
            
        case NODE_ARRAY_ASSIGNMENT:
            process_array_assignment(node, output);
            break;
            
        case NODE_ARRAY_DECL:
            process_array_declaration(node, output);
            break;
            
        case NODE_ARRAY_SIZE:
        case NODE_ARRAY_TYPE:
            // Estos nodos son procesados por sus nodos padre
            break;
    }
    
    if (node->next && node->type != NODE_BLOCK) {
        generate_code(node->next, output);
    }
    
    return result;
}

/**
 * Punto de entrada principal para generar código intermedio a partir del AST.
 * Inicializa el administrador de temporales, procesa el AST completo y libera
 * los recursos utilizados.
 * 
 * @param ast Raíz del AST que representa el programa
 * @param output_file Nombre del archivo de salida
 */
void generate_intermediate_code(Node *ast, const char *output_file) {
    if (!ast) return;
    
    FILE *output = fopen(output_file, "w");
    if (!output) {
        fprintf(stderr, "Could not open output file %s\n", output_file);
        LOG("Could not open output file %s\n", output_file);
        return;
    }
    
    temp_mgr = init_temp_manager();
    generate_code(ast, output);
    
    fclose(output);
    
    for (int i = 0; i < temp_mgr->next_temp; i++) {
        free(temp_mgr->temp_names[i]);
    }
    free(temp_mgr->temp_names);
    free(temp_mgr);
}