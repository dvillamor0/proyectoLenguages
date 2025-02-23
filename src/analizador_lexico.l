%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "analizador_sintactico.tab.h"

#define MAX_SYMBOLS 1000

#define SYMTAB_IDENTIFIER 1
#define SYMTAB_NUMBER 2

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

{WHITESPACE}    { /* Skip whitespace */ }
{COMMENT}       { /* Skip comments */ }

"Fun"       { return TOKEN_FUN; }
"Ret"       { return TOKEN_RET; }
"If"        { return TOKEN_IF; }
"While"     { return TOKEN_WHILE; }
"Ent"       { return TOKEN_ENT; }
"Flo"       { return TOKEN_FLO; }

"<"         { return TOKEN_RELOP_LT; }
"<="        { return TOKEN_RELOP_LE; }
"=="        { return TOKEN_RELOP_EQ; }  
"!="        { return TOKEN_RELOP_NE; }
">"         { return TOKEN_RELOP_GT; }
">="        { return TOKEN_RELOP_GE; }

"+"         { return TOKEN_PLUS; }
"-"         { return TOKEN_MINUS; }
"*"         { return TOKEN_MULT; }
"/"         { return TOKEN_DIV; }
"="         { return TOKEN_ASSIGN; }   
";"         { return TOKEN_SEMICOLON; }
","         { return TOKEN_COMMA; }
"("         { return TOKEN_LPAREN; }
")"         { return TOKEN_RPAREN; }
"{"         { return TOKEN_LBRACE; }
"}"         { return TOKEN_RBRACE; }

{ID}        { yylval.symbol_index = install_id(yytext); return TOKEN_ID; }
{NUMBER}    { yylval.symbol_index = install_num(yytext); return TOKEN_NUMBER; }

.           { printf("Lexical Error: Unexpected character %s\n", yytext); }

%%

int install_id(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    for (int i = 0; i < symbol_count; i++) {
        if (symbol_table[i].type == SYMTAB_IDENTIFIER && 
            strcmp(symbol_table[i].name, lexeme) == 0) {
            return i;
        }
    }
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_IDENTIFIER;
    return symbol_count++;
}

int install_num(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_NUMBER;
    symbol_table[symbol_count].value.number_value = atof(lexeme);
    return symbol_count++;
}

