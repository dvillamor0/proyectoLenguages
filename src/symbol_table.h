#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Tipos de símbolos
typedef enum {
    TYPE_INT,
    TYPE_STRING,
    TYPE_LIST,
    TYPE_UNKNOWN
} SymbolType;

// Estructura para almacenar información del símbolo
typedef struct Symbol {
    char *name;              // Nombre del símbolo
    SymbolType type;        // Tipo del símbolo
    int scope;              // Nivel de ámbito
    struct Symbol *next;    // Siguiente símbolo en la tabla
} Symbol;

// Estructura para la tabla de símbolos
typedef struct {
    Symbol *head;           // Cabeza de la lista de símbolos
    int current_scope;      // Ámbito actual
} SymbolTable;

// Funciones de la tabla de símbolos
SymbolTable* create_symbol_table();
void enter_scope(SymbolTable *table);
void exit_scope(SymbolTable *table);
Symbol* insert_symbol(SymbolTable *table, const char *name, SymbolType type);
Symbol* lookup_symbol(SymbolTable *table, const char *name);
Symbol* lookup_symbol_in_scope(SymbolTable *table, const char *name, int scope);
void delete_symbol_table(SymbolTable *table);
void print_symbol_table(SymbolTable *table);
const char* get_type_name(SymbolType type);

#endif // SYMBOL_TABLE_H