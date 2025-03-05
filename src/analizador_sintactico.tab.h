/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_ANALIZADOR_SINTACTICO_TAB_H_INCLUDED
# define YY_YY_ANALIZADOR_SINTACTICO_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    TOKEN_ID = 258,                /* TOKEN_ID  */
    TOKEN_NUMBER = 259,            /* TOKEN_NUMBER  */
    TOKEN_FUN = 260,               /* TOKEN_FUN  */
    TOKEN_RET = 261,               /* TOKEN_RET  */
    TOKEN_IF = 262,                /* TOKEN_IF  */
    TOKEN_WHILE = 263,             /* TOKEN_WHILE  */
    TOKEN_ENT = 264,               /* TOKEN_ENT  */
    TOKEN_FLO = 265,               /* TOKEN_FLO  */
    TOKEN_NAT = 266,               /* TOKEN_NAT  */
    TOKEN_ARREGLO = 267,           /* TOKEN_ARREGLO  */
    TOKEN_RELOP_LT = 268,          /* TOKEN_RELOP_LT  */
    TOKEN_RELOP_LE = 269,          /* TOKEN_RELOP_LE  */
    TOKEN_RELOP_EQ = 270,          /* TOKEN_RELOP_EQ  */
    TOKEN_RELOP_NE = 271,          /* TOKEN_RELOP_NE  */
    TOKEN_RELOP_GT = 272,          /* TOKEN_RELOP_GT  */
    TOKEN_RELOP_GE = 273,          /* TOKEN_RELOP_GE  */
    TOKEN_PLUS = 274,              /* TOKEN_PLUS  */
    TOKEN_MINUS = 275,             /* TOKEN_MINUS  */
    TOKEN_MULT = 276,              /* TOKEN_MULT  */
    TOKEN_DIV = 277,               /* TOKEN_DIV  */
    TOKEN_ASSIGN = 278,            /* TOKEN_ASSIGN  */
    TOKEN_SEMICOLON = 279,         /* TOKEN_SEMICOLON  */
    TOKEN_COMMA = 280,             /* TOKEN_COMMA  */
    TOKEN_LPAREN = 281,            /* TOKEN_LPAREN  */
    TOKEN_RPAREN = 282,            /* TOKEN_RPAREN  */
    TOKEN_LBRACE = 283,            /* TOKEN_LBRACE  */
    TOKEN_RBRACE = 284,            /* TOKEN_RBRACE  */
    TOKEN_LBRACK = 285,            /* TOKEN_LBRACK  */
    TOKEN_RBRACK = 286             /* TOKEN_RBRACK  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 56 ".\\analizador_sintactico.y"

    int symbol_index;         // Índice en la tabla de símbolos para identificadores y valores
    struct Node *node;        // Puntero a nodo del AST para construcciones sintácticas

#line 100 "analizador_sintactico.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_ANALIZADOR_SINTACTICO_TAB_H_INCLUDED  */
