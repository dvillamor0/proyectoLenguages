#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "analizador_semantico.h"
#include "analizador_sintactico.tab.h" 

/**
 * Tabla de símbolos externa proporcionada por el analizador léxico/sintáctico.
 * Contiene los nombres y valores de los símbolos encontrados durante el análisis.
 */
extern struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
} symbol_table[];

/**
 * @brief Enumeración que define los tipos de datos soportados por el lenguaje
 * 
 * Incluye tipos básicos (entero, flotante, natural), tipo void,
 * y tipos derivados para arreglos de diferentes tipos de elementos.
 */
typedef enum {
    TYPE_UNKNOWN,
    TYPE_INTEGER,
    TYPE_FLOAT,
    TYPE_NATURAL,
    TYPE_VOID,
    TYPE_ARRAY_INTEGER,  
    TYPE_ARRAY_FLOAT,    
    TYPE_ARRAY_NATURAL   
} DataType;

/**
 * @brief Estructura que almacena la información de un símbolo
 * 
 * Contiene todos los metadatos relevantes para variables, funciones y arreglos:
 * - Nombre del símbolo
 * - Tipo de dato
 * - Indicador si es función
 * - Tipo de retorno (para funciones)
 * - Tipos de parámetros (para funciones)
 * - Número de parámetros (para funciones)
 * - Tamaño del arreglo (para arreglos)
 * - Tipo de elementos (para arreglos)
 */
typedef struct {
    char *name;
    DataType type;
    int is_function;
    DataType return_type;
    DataType *param_types;
    int param_count;
    int array_size;     
    DataType element_type; 
} SymbolInfo;

/**
 * @brief Estructura que representa la tabla de símbolos completa
 * 
 * Es una colección dinámica de símbolos con gestión automática de capacidad.
 */
typedef struct {
    SymbolInfo *entries;  // Arreglo dinámico de entradas
    int size;             // Número actual de símbolos
    int capacity;         // Capacidad total disponible
} SymbolTable;

// Declaración de funciones estáticas para manejo de la tabla de símbolos y análisis semántico
static SymbolTable* create_symbol_table();
static void add_symbol(SymbolTable *table, const char *name, DataType type);
static void add_function(SymbolTable *table, const char *name, DataType return_type);
static SymbolInfo* lookup_symbol(SymbolTable *table, const char *name);
static DataType check_types(Node *node, SymbolTable *table);
static void analyze_semantics(Node *root, SymbolTable *table);

/**
 * @brief Crea e inicializa una tabla de símbolos
 * 
 * Reserva memoria para la tabla y su arreglo de entradas con una capacidad inicial.
 * 
 * @return Puntero a la nueva tabla de símbolos inicializada
 */
static SymbolTable* create_symbol_table() {
    SymbolTable *table = malloc(sizeof(SymbolTable));
    table->capacity = 100;
    table->size = 0;
    table->entries = malloc(sizeof(SymbolInfo) * table->capacity);
    return table;
}

/**
 * @brief Agrega un símbolo (variable) a la tabla de símbolos
 * 
 * Si la tabla está llena, duplica automáticamente su capacidad antes de agregar.
 * 
 * @param table Tabla de símbolos donde agregar
 * @param name Nombre del símbolo a agregar
 * @param type Tipo de dato del símbolo
 */
static void add_symbol(SymbolTable *table, const char *name, DataType type) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = type;
    table->entries[table->size].is_function = 0;
    table->entries[table->size].array_size = 0;  
    table->size++;
}

/**
 * @brief Agrega una función a la tabla de símbolos
 * 
 * Registra una función con su tipo de retorno y prepara la estructura para
 * almacenar información sobre sus parámetros.
 * 
 * @param table Tabla de símbolos donde agregar
 * @param name Nombre de la función
 * @param return_type Tipo de retorno de la función
 */
static void add_function(SymbolTable *table, const char *name, DataType return_type) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = return_type;
    table->entries[table->size].is_function = 1;
    table->entries[table->size].return_type = return_type;
    table->entries[table->size].param_types = NULL;
    table->entries[table->size].param_count = 0;
    table->size++;
}

/**
 * @brief Agrega un arreglo a la tabla de símbolos
 * 
 * Determina el tipo de arreglo basado en el tipo de sus elementos y
 * almacena metadatos adicionales como tamaño y tipo de elementos.
 * 
 * @param table Tabla de símbolos donde agregar
 * @param name Nombre del arreglo
 * @param elemType Tipo de los elementos del arreglo
 * @param size Tamaño del arreglo (número de elementos)
 */
static void add_array_symbol(SymbolTable *table, const char *name, DataType elemType, int size) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    // Determina el tipo de arreglo basado en el tipo de elementos
    DataType arrayType;
    switch (elemType) {
        case TYPE_INTEGER:
            arrayType = TYPE_ARRAY_INTEGER;
            break;
        case TYPE_FLOAT:
            arrayType = TYPE_ARRAY_FLOAT;
            break;
        case TYPE_NATURAL:
            arrayType = TYPE_ARRAY_NATURAL;
            break;
        default:
            fprintf(stderr, "Semantic Error: Cannot create array of type %d\n", elemType);
            arrayType = TYPE_UNKNOWN;
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = arrayType;
    table->entries[table->size].element_type = elemType;
    table->entries[table->size].is_function = 0;
    table->entries[table->size].array_size = size;
    table->size++;
}

/**
 * @brief Busca un símbolo en la tabla por su nombre
 * 
 * Recorre secuencialmente todas las entradas hasta encontrar una coincidencia.
 * 
 * @param table Tabla de símbolos donde buscar
 * @param name Nombre del símbolo a buscar
 * @return Puntero a la información del símbolo o NULL si no se encuentra
 */
static SymbolInfo* lookup_symbol(SymbolTable *table, const char *name) {
    for (int i = 0; i < table->size; i++) {
        if (strcmp(table->entries[i].name, name) == 0) {
            return &table->entries[i];
        }
    }
    return NULL;
}

/**
 * @brief Convierte un token de tipo a su representación interna de tipo de dato
 * 
 * @param token Token que representa un tipo de dato (TOKEN_ENT, TOKEN_FLO, etc.)
 * @return Tipo de dato correspondiente al token
 */
static DataType get_type_from_token(int token) {
    switch (token) {
        case TOKEN_ENT:
            return TYPE_INTEGER;
        case TOKEN_FLO:
            return TYPE_FLOAT;
        case TOKEN_NAT:
            return TYPE_NATURAL;
        default:
            return TYPE_UNKNOWN;
    }
}

/**
 * @brief Obtiene el tipo de elemento correspondiente a un tipo de arreglo
 * 
 * @param arrayType Tipo de arreglo (TYPE_ARRAY_INTEGER, etc.)
 * @return Tipo de los elementos contenidos en el arreglo
 */
static DataType get_element_type(DataType arrayType) {
    switch (arrayType) {
        case TYPE_ARRAY_INTEGER:
            return TYPE_INTEGER;
        case TYPE_ARRAY_FLOAT:
            return TYPE_FLOAT;
        case TYPE_ARRAY_NATURAL:
            return TYPE_NATURAL;
        default:
            return TYPE_UNKNOWN;
    }
}

/**
 * @brief Verifica y deduce el tipo de una expresión en el AST
 * 
 * Analiza recursivamente cada nodo para determinar su tipo resultante,
 * realizando verificaciones de compatibilidad de tipos donde corresponda.
 * 
 * @param node Nodo del AST a verificar
 * @param table Tabla de símbolos actual
 * @return Tipo de dato resultante de la expresión
 */
static DataType check_types(Node *node, SymbolTable *table) {
    if (!node) return TYPE_VOID;
    
    switch (node->type) {
        case NODE_NUMBER: {
            // Identifica el tipo del número basado en su representación y tipo asignado
            if (symbol_table[node->symbol_index].type == 3) {  
                return TYPE_NATURAL;
            }
            
            // Determina si es flotante o entero basado en la presencia de punto decimal o notación científica
            const char *num_str = symbol_table[node->symbol_index].name;
            return (strchr(num_str, '.') || strchr(num_str, 'e') || strchr(num_str, 'E'))
                   ? TYPE_FLOAT : TYPE_INTEGER;
        }
        
        case NODE_IDENTIFIER: {
            // Obtiene el nombre del identificador y lo busca en la tabla
            const char *id_name = symbol_table[node->symbol_index].name;
            SymbolInfo *info = lookup_symbol(table, id_name);
            if (!info) {
                fprintf(stderr, "Semantic Error: Undefined identifier '%s'\n", id_name);
                return TYPE_UNKNOWN;
            }
            return info->type;
        }
        
        case NODE_BINARY_OP: {
            // Comprueba los tipos de las subexpresiones y determina el tipo de la operación
            DataType left_type = check_types(node->left, table);
            DataType right_type = check_types(node->right, table);
            
            // Las operaciones entre tipos mixtos producen resultados tipo float
            if (left_type == TYPE_FLOAT || right_type == TYPE_FLOAT) {
                return TYPE_FLOAT;
            }
            return TYPE_INTEGER;
        }
        
        case NODE_FUNCTION_CALL: {
            // Obtiene el nombre de la función y verifica que sea una función
            const char *func_name = symbol_table[node->left->symbol_index].name;
            SymbolInfo *func = lookup_symbol(table, func_name);
            
            if (!func || !func->is_function) {
                fprintf(stderr, "Semantic Error: '%s' is not a function\n", func_name);
                return TYPE_UNKNOWN;
            }
            
            // Verifica los argumentos de la llamada a la función
            Node *arg = node->right;
            int arg_count = 0;
            while (arg) {
                DataType arg_type = check_types(arg, table);
                if (arg_count < func->param_count &&
                    arg_type != func->param_types[arg_count]) {
                    fprintf(stderr, "Semantic Error: Type mismatch in argument %d of '%s'\n",
                            arg_count + 1, func_name);
                }
                arg = arg->next;
                arg_count++;
            }
            
            if (arg_count != func->param_count) {
                fprintf(stderr, "Semantic Error: Wrong number of arguments for '%s'\n", func_name);
            }
            
            return func->return_type;
        }

        case NODE_ARRAY_ACCESS: {
            // Verifica que el identificador sea un arreglo
            const char *id_name = symbol_table[node->left->symbol_index].name;
            SymbolInfo *info = lookup_symbol(table, id_name);
            if (!info) {
                fprintf(stderr, "Semantic Error: Undefined identifier '%s'\n", id_name);
                return TYPE_UNKNOWN;
            }
            
            // Comprueba que sea un tipo de arreglo
            if (info->type != TYPE_ARRAY_INTEGER && 
                info->type != TYPE_ARRAY_FLOAT && 
                info->type != TYPE_ARRAY_NATURAL) {
                fprintf(stderr, "Semantic Error: '%s' is not an array\n", id_name);
                return TYPE_UNKNOWN;
            }
            
            // Verifica que el índice sea un entero o natural
            DataType index_type = check_types(node->right, table);
            if (index_type != TYPE_INTEGER && index_type != TYPE_NATURAL) {
                fprintf(stderr, "Semantic Error: Array index must be integer or natural, got %d\n", index_type);
            }
            
            // Retorna el tipo de elemento del arreglo
            return info->element_type;
        }
        
        case NODE_ARRAY_LITERAL: {
            // Verifica que todos los elementos tengan el mismo tipo
            DataType element_type = TYPE_UNKNOWN;
            Node *element = node->left;
            
            if (element) {
                element_type = check_types(element, table);
                element = element->next;
                
                while (element) {
                    DataType current_type = check_types(element, table);
                    if (current_type != element_type) {
                        fprintf(stderr, "Semantic Error: Array elements must have the same type\n");
                        break;
                    }
                    element = element->next;
                }
            }
            
            // Determina el tipo de arreglo basado en el tipo de elementos
            switch (element_type) {
                case TYPE_INTEGER:
                    return TYPE_ARRAY_INTEGER;
                case TYPE_FLOAT:
                    return TYPE_ARRAY_FLOAT;
                case TYPE_NATURAL:
                    return TYPE_ARRAY_NATURAL;
                default:
                    return TYPE_UNKNOWN;
            }
        }
        
        case NODE_ARRAY_ASSIGNMENT: {
            // Verifica el acceso al arreglo
            DataType element_type = check_types(node->left, table);
            
            // Verifica el valor que se está asignando
            DataType value_type = check_types(node->right, table);
            
            // Comprueba compatibilidad de tipos
            if (element_type != value_type) {
                fprintf(stderr, "Semantic Error: Type mismatch in array assignment\n");
            }
            
            return element_type;
        }
        
        default:
            return TYPE_UNKNOWN;
    }
}

/**
 * @brief Realiza el análisis semántico completo sobre el AST
 * 
 * Recorre el árbol de forma recursiva, procesando cada nodo según su tipo,
 * verificando declaraciones, asignaciones, operaciones y estructuras de control.
 * 
 * @param root Nodo raíz del AST a analizar
 * @param table Tabla de símbolos a utilizar/actualizar
 */
static void analyze_semantics(Node *root, SymbolTable *table) {
    if (!root) return;
    
    switch (root->type) {
        case NODE_FUNCTION: {
            // Procesa una definición de función
            const char *func_name = symbol_table[root->symbol_index].name;
            DataType return_type = TYPE_VOID;
            add_function(table, func_name, return_type);
            
            // Procesa los parámetros de la función
            Node *param = root->left;
            while (param) {
                const char *param_name = symbol_table[param->symbol_index].name;
                DataType param_type = TYPE_FLOAT;  // Se asume que el tipo de parámetro es float
                add_symbol(table, param_name, param_type);
                param = param->next;
            }
            
            // Analiza el cuerpo de la función
            analyze_semantics(root->right, table);
            break;
        }
        
        case NODE_DECLARATION: {
            // Procesa una declaración de variable
            const char *var_name = symbol_table[root->left->symbol_index].name;
            DataType expr_type = check_types(root->right, table);
            add_symbol(table, var_name, expr_type);
            break;
        }
        
        case NODE_ASSIGNMENT: {
            // Procesa una asignación a una variable
            const char *var_name = symbol_table[root->left->symbol_index].name;
            SymbolInfo *var = lookup_symbol(table, var_name);
            
            if (!var) {
                fprintf(stderr, "Semantic Error: Assignment to undefined variable '%s'\n", var_name);
                break;
            }
            
            DataType expr_type = check_types(root->right, table);
            if (var->type != expr_type) {
                if (var->type == TYPE_FLOAT && expr_type == TYPE_INTEGER) {
                    // Conversión permitida de entero a float
                } else {
                    fprintf(stderr, "Semantic Error: Type mismatch in assignment to '%s'\n", var_name);
                }
            }
            break;
        }
        
        case NODE_ARRAY_DECL: {
            // Procesa una declaración de arreglo
            const char *array_name = symbol_table[root->left->symbol_index].name;
            
            // Verifica si es una declaración con inicialización
            if (root->right && root->right->type == NODE_ARRAY_INIT) {
                // Obtiene el tipo y tamaño
                Node *size_and_type = root->right->left;
                Node *init_value = root->right->right;
                
                // Verifica la expresión de tamaño
                DataType size_type = check_types(size_and_type->left, table);
                if (size_type != TYPE_INTEGER && size_type != TYPE_NATURAL) {
                    fprintf(stderr, "Semantic Error: Array size must be an integer or natural\n");
                }
                
                // Obtiene el tipo de elemento del nodo NODE_ARRAY_TYPE
                DataType elem_type = get_type_from_token(size_and_type->right->symbol_index);
                
                // Verifica el inicializador
                DataType init_type = check_types(init_value, table);
                
                // Determina el tipo de arreglo esperado basado en el tipo de elemento
                DataType expected_array_type;
                switch (elem_type) {
                    case TYPE_INTEGER:
                        expected_array_type = TYPE_ARRAY_INTEGER;
                        break;
                    case TYPE_FLOAT:
                        expected_array_type = TYPE_ARRAY_FLOAT;
                        break;
                    case TYPE_NATURAL:
                        expected_array_type = TYPE_ARRAY_NATURAL;
                        break;
                    default:
                        expected_array_type = TYPE_UNKNOWN;
                }
                
                // Verifica si el tipo del inicializador coincide con el tipo de arreglo esperado
                if (init_type != expected_array_type) {
                    fprintf(stderr, "Semantic Error: Array initializer type mismatch\n");
                }
                
                // Agrega el arreglo a la tabla de símbolos
                // Para simplificar, no se calcula el tamaño exacto en tiempo de compilación
                add_array_symbol(table, array_name, elem_type, 0);
            } else {
                // Declaración simple de arreglo sin inicialización
                DataType elem_type = get_type_from_token(root->right->symbol_index);
                
                // Verifica la expresión de tamaño
                DataType size_type = check_types(root->right, table);
                if (size_type != TYPE_INTEGER && size_type != TYPE_NATURAL) {
                    fprintf(stderr, "Semantic Error: Array size must be an integer or natural\n");
                }
                
                // Agrega el arreglo a la tabla de símbolos
                add_array_symbol(table, array_name, elem_type, 0);
            }
            break;
        }
        
        case NODE_ARRAY_ASSIGNMENT: {
            // La semántica del acceso al arreglo se verifica en check_types
            check_types(root, table);
            break;
        }
        
        case NODE_IF:
        case NODE_WHILE: {
            // Verifica que la condición sea un valor numérico
            DataType cond_type = check_types(root->left, table);
            if (cond_type != TYPE_INTEGER && cond_type != TYPE_FLOAT) {
                fprintf(stderr, "Semantic Error: Condition must be numeric\n");
            }
            analyze_semantics(root->right, table);
            break;
        }
        
        case NODE_RETURN: {
            // Verifica el tipo del valor de retorno
            DataType return_type = check_types(root->left, table);
            break;
        }
    }
    
    // Continúa con el siguiente nodo en la secuencia
    if (root->next) {
        analyze_semantics(root->next, table);
    }
}

/**
 * @brief Inicializa y ejecuta el análisis semántico del AST
 * 
 * Punto de entrada principal para el análisis semántico:
 * 1. Crea una tabla de símbolos
 * 2. Instala funciones predefinidas
 * 3. Analiza el AST completo
 * 
 * @param ast Árbol de sintaxis abstracta completo a analizar
 */
void init_semantic_analysis(Node *ast) {
    SymbolTable *table = create_symbol_table();
    
    // Registra funciones predefinidas del lenguaje
    add_function(table, "sqrt", TYPE_FLOAT);
    add_function(table, "power", TYPE_FLOAT);
    
    // Inicia el proceso de análisis semántico
    analyze_semantics(ast, table);
}