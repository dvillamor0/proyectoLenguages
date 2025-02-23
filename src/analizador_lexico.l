%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "analizador_sintactico.tab.h"

#define MAX_SYMBOLS 1000
#define DEBUG_LEXER 1  // Debug flag

#define SYMTAB_IDENTIFIER 1
#define SYMTAB_NUMBER 2

// ANSI color codes for debug output
#define ANSI_COLOR_RED     "\x1b[31m"
#define ANSI_COLOR_GREEN   "\x1b[32m"
#define ANSI_COLOR_YELLOW  "\x1b[33m"
#define ANSI_COLOR_BLUE    "\x1b[34m"
#define ANSI_COLOR_RESET   "\x1b[0m"

typedef struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
} SymbolEntry;

SymbolEntry symbol_table[MAX_SYMBOLS];
int symbol_count = 0;

// Debug function declarations
void debug_print_token(int token, int symbol_index);
void debug_print_symbol_table(void);
const char* get_token_name(int token);

int install_id(char *lexeme);
int install_num(char *lexeme);
%}

%option noyywrap
%option yylineno

/* Regular definitions */
DIGIT       [0-9]
LETTER      [a-zA-Z]
ID          {LETTER}({LETTER}|{DIGIT})*
NUMBER      {DIGIT}+(\.{DIGIT}+)?([Ee][+-]?{DIGIT}+)?
WHITESPACE  [ \t\n\r]+
COMMENT     #[^\n]*\n

%%

{WHITESPACE}    { if (DEBUG_LEXER) printf(ANSI_COLOR_BLUE "Skipping whitespace: '%s'\n" ANSI_COLOR_RESET, yytext); }
{COMMENT}       { if (DEBUG_LEXER) printf(ANSI_COLOR_GREEN "Skipping comment: '%s'\n" ANSI_COLOR_RESET, yytext); }

"Fun"       { if (DEBUG_LEXER) debug_print_token(TOKEN_FUN, -1); return TOKEN_FUN; }
"Ret"       { if (DEBUG_LEXER) debug_print_token(TOKEN_RET, -1); return TOKEN_RET; }
"If"        { if (DEBUG_LEXER) debug_print_token(TOKEN_IF, -1); return TOKEN_IF; }
"While"     { if (DEBUG_LEXER) debug_print_token(TOKEN_WHILE, -1); return TOKEN_WHILE; }
"Ent"       { if (DEBUG_LEXER) debug_print_token(TOKEN_ENT, -1); return TOKEN_ENT; }
"Flo"       { if (DEBUG_LEXER) debug_print_token(TOKEN_FLO, -1); return TOKEN_FLO; }

"<"         { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_LT, -1); return TOKEN_RELOP_LT; }
"<="        { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_LE, -1); return TOKEN_RELOP_LE; }
"=="        { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_EQ, -1); return TOKEN_RELOP_EQ; }
"!="        { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_NE, -1); return TOKEN_RELOP_NE; }
">"         { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_GT, -1); return TOKEN_RELOP_GT; }
">="        { if (DEBUG_LEXER) debug_print_token(TOKEN_RELOP_GE, -1); return TOKEN_RELOP_GE; }

"+"         { if (DEBUG_LEXER) debug_print_token(TOKEN_PLUS, -1); return TOKEN_PLUS; }
"-"         { if (DEBUG_LEXER) debug_print_token(TOKEN_MINUS, -1); return TOKEN_MINUS; }
"*"         { if (DEBUG_LEXER) debug_print_token(TOKEN_MULT, -1); return TOKEN_MULT; }
"/"         { if (DEBUG_LEXER) debug_print_token(TOKEN_DIV, -1); return TOKEN_DIV; }
"="         { if (DEBUG_LEXER) debug_print_token(TOKEN_ASSIGN, -1); return TOKEN_ASSIGN; }
";"         { if (DEBUG_LEXER) debug_print_token(TOKEN_SEMICOLON, -1); return TOKEN_SEMICOLON; }
","         { if (DEBUG_LEXER) debug_print_token(TOKEN_COMMA, -1); return TOKEN_COMMA; }
"("         { if (DEBUG_LEXER) debug_print_token(TOKEN_LPAREN, -1); return TOKEN_LPAREN; }
")"         { if (DEBUG_LEXER) debug_print_token(TOKEN_RPAREN, -1); return TOKEN_RPAREN; }
"{"         { if (DEBUG_LEXER) debug_print_token(TOKEN_LBRACE, -1); return TOKEN_LBRACE; }
"}"         { if (DEBUG_LEXER) debug_print_token(TOKEN_RBRACE, -1); return TOKEN_RBRACE; }

{ID}        { 
    yylval.symbol_index = install_id(yytext);
    if (DEBUG_LEXER) {
        debug_print_token(TOKEN_ID, yylval.symbol_index);
        debug_print_symbol_table();
    }
    return TOKEN_ID;
}

{NUMBER}    { 
    yylval.symbol_index = install_num(yytext);
    if (DEBUG_LEXER) {
        debug_print_token(TOKEN_NUMBER, yylval.symbol_index);
        debug_print_symbol_table();
    }
    return TOKEN_NUMBER;
}

.           { 
    if (DEBUG_LEXER) printf(ANSI_COLOR_RED "Lexical Error: Unexpected character '%s' at line %d\n" ANSI_COLOR_RESET, yytext, yylineno);
    return TOKEN_ERROR;
}

%%

// Helper function to get token name
const char* get_token_name(int token) {
    switch(token) {
        case TOKEN_FUN: return "FUN";
        case TOKEN_RET: return "RET";
        case TOKEN_IF: return "IF";
        case TOKEN_WHILE: return "WHILE";
        case TOKEN_ENT: return "ENT";
        case TOKEN_FLO: return "FLO";
        case TOKEN_ID: return "ID";
        case TOKEN_NUMBER: return "NUMBER";
        case TOKEN_RELOP_LT: return "RELOP_LT";
        case TOKEN_RELOP_LE: return "RELOP_LE";
        case TOKEN_RELOP_EQ: return "RELOP_EQ";
        case TOKEN_RELOP_NE: return "RELOP_NE";
        case TOKEN_RELOP_GT: return "RELOP_GT";
        case TOKEN_RELOP_GE: return "RELOP_GE";
        case TOKEN_PLUS: return "PLUS";
        case TOKEN_MINUS: return "MINUS";
        case TOKEN_MULT: return "MULT";
        case TOKEN_DIV: return "DIV";
        case TOKEN_ASSIGN: return "ASSIGN";
        case TOKEN_SEMICOLON: return "SEMICOLON";
        case TOKEN_COMMA: return "COMMA";
        case TOKEN_LPAREN: return "LPAREN";
        case TOKEN_RPAREN: return "RPAREN";
        case TOKEN_LBRACE: return "LBRACE";
        case TOKEN_RBRACE: return "RBRACE";
        default: return "UNKNOWN";
    }
}

// Debug function to print token information
void debug_print_token(int token, int symbol_index) {
    printf(ANSI_COLOR_YELLOW "Token: %-15s" ANSI_COLOR_RESET, get_token_name(token));
    printf(" Line: %-4d", yylineno);
    printf(" Text: '%s'", yytext);
    if (symbol_index >= 0) {
        printf(" Symbol Index: %d", symbol_index);
    }
    printf("\n");
}

// Debug function to print symbol table
void debug_print_symbol_table(void) {
    printf(ANSI_COLOR_GREEN "\nSymbol Table Status:\n" ANSI_COLOR_RESET);
    printf("Total Entries: %d\n", symbol_count);
    printf("%-20s %-10s %-20s\n", "Name", "Type", "Value");
    printf("----------------------------------------\n");
    
    for (int i = 0; i < symbol_count; i++) {
        printf("%-20s %-10s ", 
            symbol_table[i].name,
            symbol_table[i].type == SYMTAB_IDENTIFIER ? "ID" : "NUMBER"
        );
        
        if (symbol_table[i].type == SYMTAB_NUMBER) {
            printf("%-20.6g", symbol_table[i].value.number_value);
        } else {
            printf("%-20s", "-");
        }
        printf("\n");
    }
    printf("----------------------------------------\n\n");
}

int install_id(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, ANSI_COLOR_RED "Error: Symbol table full\n" ANSI_COLOR_RESET);
        exit(1);
    }
    
    for (int i = 0; i < symbol_count; i++) {
        if (symbol_table[i].type == SYMTAB_IDENTIFIER && 
            strcmp(symbol_table[i].name, lexeme) == 0) {
            if (DEBUG_LEXER) printf(ANSI_COLOR_BLUE "Found existing identifier: %s at index %d\n" ANSI_COLOR_RESET, lexeme, i);
            return i;
        }
    }
    
    if (DEBUG_LEXER) printf(ANSI_COLOR_GREEN "Installing new identifier: %s at index %d\n" ANSI_COLOR_RESET, lexeme, symbol_count);
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_IDENTIFIER;
    return symbol_count++;
}

int install_num(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, ANSI_COLOR_RED "Error: Symbol table full\n" ANSI_COLOR_RESET);
        exit(1);
    }
    
    if (DEBUG_LEXER) printf(ANSI_COLOR_GREEN "Installing new number: %s at index %d\n" ANSI_COLOR_RESET, lexeme, symbol_count);
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_NUMBER;
    symbol_table[symbol_count].value.number_value = atof(lexeme);
    return symbol_count++;
}