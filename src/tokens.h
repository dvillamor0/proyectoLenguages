#ifndef TOKENS_H
#define TOKENS_H

#include <stdio.h>

#include "parser.tab.h"

extern YYSTYPE yylval;
extern FILE *yyin;
extern int yylineno;  

#define MAX_IDS 1000

extern char *tablaSimbolos[MAX_IDS];
extern int numIDs;

#endif 