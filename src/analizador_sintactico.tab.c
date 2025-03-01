/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison implementation for Yacc-like parsers in C

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

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output, and Bison version.  */
#define YYBISON 30802

/* Bison version string.  */
#define YYBISON_VERSION "3.8.2"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1




/* First part of user prologue.  */
#line 1 ".\\analizador_sintactico.y"

    // Inclusión de las bibliotecas estándar necesarias para la entrada/salida y manejo de memoria.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    // Inclusión de cabeceras del compilador para el manejo del AST, análisis semántico y generación de código intermedio.
    #include "ast.h"
    #include "analizador_semantico.h"
    #include "intermediate_code.h" 

    // Declaración externa de funciones y variables utilizadas en el proceso de análisis léxico.
    extern int yylex();
    extern FILE* yyin;
    extern int yylineno;
    void yyerror(const char *s);

    // Declaración de la raíz del árbol de sintaxis abstracta.
    Node* ast_root = NULL;

#line 92 "analizador_sintactico.tab.c"

# ifndef YY_CAST
#  ifdef __cplusplus
#   define YY_CAST(Type, Val) static_cast<Type> (Val)
#   define YY_REINTERPRET_CAST(Type, Val) reinterpret_cast<Type> (Val)
#  else
#   define YY_CAST(Type, Val) ((Type) (Val))
#   define YY_REINTERPRET_CAST(Type, Val) ((Type) (Val))
#  endif
# endif
# ifndef YY_NULLPTR
#  if defined __cplusplus
#   if 201103L <= __cplusplus
#    define YY_NULLPTR nullptr
#   else
#    define YY_NULLPTR 0
#   endif
#  else
#   define YY_NULLPTR ((void*)0)
#  endif
# endif

#include "analizador_sintactico.tab.h"
/* Symbol kind.  */
enum yysymbol_kind_t
{
  YYSYMBOL_YYEMPTY = -2,
  YYSYMBOL_YYEOF = 0,                      /* "end of file"  */
  YYSYMBOL_YYerror = 1,                    /* error  */
  YYSYMBOL_YYUNDEF = 2,                    /* "invalid token"  */
  YYSYMBOL_TOKEN_ID = 3,                   /* TOKEN_ID  */
  YYSYMBOL_TOKEN_NUMBER = 4,               /* TOKEN_NUMBER  */
  YYSYMBOL_TOKEN_FUN = 5,                  /* TOKEN_FUN  */
  YYSYMBOL_TOKEN_RET = 6,                  /* TOKEN_RET  */
  YYSYMBOL_TOKEN_IF = 7,                   /* TOKEN_IF  */
  YYSYMBOL_TOKEN_WHILE = 8,                /* TOKEN_WHILE  */
  YYSYMBOL_TOKEN_ENT = 9,                  /* TOKEN_ENT  */
  YYSYMBOL_TOKEN_FLO = 10,                 /* TOKEN_FLO  */
  YYSYMBOL_TOKEN_RELOP_LT = 11,            /* TOKEN_RELOP_LT  */
  YYSYMBOL_TOKEN_RELOP_LE = 12,            /* TOKEN_RELOP_LE  */
  YYSYMBOL_TOKEN_RELOP_EQ = 13,            /* TOKEN_RELOP_EQ  */
  YYSYMBOL_TOKEN_RELOP_NE = 14,            /* TOKEN_RELOP_NE  */
  YYSYMBOL_TOKEN_RELOP_GT = 15,            /* TOKEN_RELOP_GT  */
  YYSYMBOL_TOKEN_RELOP_GE = 16,            /* TOKEN_RELOP_GE  */
  YYSYMBOL_TOKEN_PLUS = 17,                /* TOKEN_PLUS  */
  YYSYMBOL_TOKEN_MINUS = 18,               /* TOKEN_MINUS  */
  YYSYMBOL_TOKEN_MULT = 19,                /* TOKEN_MULT  */
  YYSYMBOL_TOKEN_DIV = 20,                 /* TOKEN_DIV  */
  YYSYMBOL_TOKEN_ASSIGN = 21,              /* TOKEN_ASSIGN  */
  YYSYMBOL_TOKEN_SEMICOLON = 22,           /* TOKEN_SEMICOLON  */
  YYSYMBOL_TOKEN_COMMA = 23,               /* TOKEN_COMMA  */
  YYSYMBOL_TOKEN_LPAREN = 24,              /* TOKEN_LPAREN  */
  YYSYMBOL_TOKEN_RPAREN = 25,              /* TOKEN_RPAREN  */
  YYSYMBOL_TOKEN_LBRACE = 26,              /* TOKEN_LBRACE  */
  YYSYMBOL_TOKEN_RBRACE = 27,              /* TOKEN_RBRACE  */
  YYSYMBOL_YYACCEPT = 28,                  /* $accept  */
  YYSYMBOL_program = 29,                   /* program  */
  YYSYMBOL_function_list = 30,             /* function_list  */
  YYSYMBOL_function = 31,                  /* function  */
  YYSYMBOL_param_list = 32,                /* param_list  */
  YYSYMBOL_param = 33,                     /* param  */
  YYSYMBOL_type = 34,                      /* type  */
  YYSYMBOL_block = 35,                     /* block  */
  YYSYMBOL_statement_list = 36,            /* statement_list  */
  YYSYMBOL_statement = 37,                 /* statement  */
  YYSYMBOL_declaration_stmt = 38,          /* declaration_stmt  */
  YYSYMBOL_assignment_stmt = 39,           /* assignment_stmt  */
  YYSYMBOL_if_stmt = 40,                   /* if_stmt  */
  YYSYMBOL_while_stmt = 41,                /* while_stmt  */
  YYSYMBOL_return_stmt = 42,               /* return_stmt  */
  YYSYMBOL_condition = 43,                 /* condition  */
  YYSYMBOL_relop = 44,                     /* relop  */
  YYSYMBOL_expr = 45,                      /* expr  */
  YYSYMBOL_arg_list = 46                   /* arg_list  */
};
typedef enum yysymbol_kind_t yysymbol_kind_t;




#ifdef short
# undef short
#endif

/* On compilers that do not define __PTRDIFF_MAX__ etc., make sure
   <limits.h> and (if available) <stdint.h> are included
   so that the code can choose integer types of a good width.  */

#ifndef __PTRDIFF_MAX__
# include <limits.h> /* INFRINGES ON USER NAME SPACE */
# if defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stdint.h> /* INFRINGES ON USER NAME SPACE */
#  define YY_STDINT_H
# endif
#endif

/* Narrow types that promote to a signed type and that can represent a
   signed or unsigned integer of at least N bits.  In tables they can
   save space and decrease cache pressure.  Promoting to a signed type
   helps avoid bugs in integer arithmetic.  */

#ifdef __INT_LEAST8_MAX__
typedef __INT_LEAST8_TYPE__ yytype_int8;
#elif defined YY_STDINT_H
typedef int_least8_t yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef __INT_LEAST16_MAX__
typedef __INT_LEAST16_TYPE__ yytype_int16;
#elif defined YY_STDINT_H
typedef int_least16_t yytype_int16;
#else
typedef short yytype_int16;
#endif

/* Work around bug in HP-UX 11.23, which defines these macros
   incorrectly for preprocessor constants.  This workaround can likely
   be removed in 2023, as HPE has promised support for HP-UX 11.23
   (aka HP-UX 11i v2) only through the end of 2022; see Table 2 of
   <https://h20195.www2.hpe.com/V2/getpdf.aspx/4AA4-7673ENW.pdf>.  */
#ifdef __hpux
# undef UINT_LEAST8_MAX
# undef UINT_LEAST16_MAX
# define UINT_LEAST8_MAX 255
# define UINT_LEAST16_MAX 65535
#endif

#if defined __UINT_LEAST8_MAX__ && __UINT_LEAST8_MAX__ <= __INT_MAX__
typedef __UINT_LEAST8_TYPE__ yytype_uint8;
#elif (!defined __UINT_LEAST8_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST8_MAX <= INT_MAX)
typedef uint_least8_t yytype_uint8;
#elif !defined __UINT_LEAST8_MAX__ && UCHAR_MAX <= INT_MAX
typedef unsigned char yytype_uint8;
#else
typedef short yytype_uint8;
#endif

#if defined __UINT_LEAST16_MAX__ && __UINT_LEAST16_MAX__ <= __INT_MAX__
typedef __UINT_LEAST16_TYPE__ yytype_uint16;
#elif (!defined __UINT_LEAST16_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST16_MAX <= INT_MAX)
typedef uint_least16_t yytype_uint16;
#elif !defined __UINT_LEAST16_MAX__ && USHRT_MAX <= INT_MAX
typedef unsigned short yytype_uint16;
#else
typedef int yytype_uint16;
#endif

#ifndef YYPTRDIFF_T
# if defined __PTRDIFF_TYPE__ && defined __PTRDIFF_MAX__
#  define YYPTRDIFF_T __PTRDIFF_TYPE__
#  define YYPTRDIFF_MAXIMUM __PTRDIFF_MAX__
# elif defined PTRDIFF_MAX
#  ifndef ptrdiff_t
#   include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  endif
#  define YYPTRDIFF_T ptrdiff_t
#  define YYPTRDIFF_MAXIMUM PTRDIFF_MAX
# else
#  define YYPTRDIFF_T long
#  define YYPTRDIFF_MAXIMUM LONG_MAX
# endif
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned
# endif
#endif

#define YYSIZE_MAXIMUM                                  \
  YY_CAST (YYPTRDIFF_T,                                 \
           (YYPTRDIFF_MAXIMUM < YY_CAST (YYSIZE_T, -1)  \
            ? YYPTRDIFF_MAXIMUM                         \
            : YY_CAST (YYSIZE_T, -1)))

#define YYSIZEOF(X) YY_CAST (YYPTRDIFF_T, sizeof (X))


/* Stored state numbers (used for stacks). */
typedef yytype_int8 yy_state_t;

/* State numbers in computations.  */
typedef int yy_state_fast_t;

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif


#ifndef YY_ATTRIBUTE_PURE
# if defined __GNUC__ && 2 < __GNUC__ + (96 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_PURE __attribute__ ((__pure__))
# else
#  define YY_ATTRIBUTE_PURE
# endif
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# if defined __GNUC__ && 2 < __GNUC__ + (7 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_UNUSED __attribute__ ((__unused__))
# else
#  define YY_ATTRIBUTE_UNUSED
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YY_USE(E) ((void) (E))
#else
# define YY_USE(E) /* empty */
#endif

/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
#if defined __GNUC__ && ! defined __ICC && 406 <= __GNUC__ * 100 + __GNUC_MINOR__
# if __GNUC__ * 100 + __GNUC_MINOR__ < 407
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")
# else
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")              \
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# endif
# define YY_IGNORE_MAYBE_UNINITIALIZED_END      \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif

#if defined __cplusplus && defined __GNUC__ && ! defined __ICC && 6 <= __GNUC__
# define YY_IGNORE_USELESS_CAST_BEGIN                          \
    _Pragma ("GCC diagnostic push")                            \
    _Pragma ("GCC diagnostic ignored \"-Wuseless-cast\"")
# define YY_IGNORE_USELESS_CAST_END            \
    _Pragma ("GCC diagnostic pop")
#endif
#ifndef YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_END
#endif


#define YY_ASSERT(E) ((void) (0 && (E)))

#if 1

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* 1 */

#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yy_state_t yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (YYSIZEOF (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (YYSIZEOF (yy_state_t) + YYSIZEOF (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYPTRDIFF_T yynewbytes;                                         \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * YYSIZEOF (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / YYSIZEOF (*yyptr);                        \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, YY_CAST (YYSIZE_T, (Count)) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYPTRDIFF_T yyi;                      \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  6
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   84

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  28
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  19
/* YYNRULES -- Number of rules.  */
#define YYNRULES  42
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  78

/* YYMAXUTOK -- Last valid token kind.  */
#define YYMAXUTOK   282


/* YYTRANSLATE(TOKEN-NUM) -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, with out-of-bounds checking.  */
#define YYTRANSLATE(YYX)                                \
  (0 <= (YYX) && (YYX) <= YYMAXUTOK                     \
   ? YY_CAST (yysymbol_kind_t, yytranslate[YYX])        \
   : YYSYMBOL_YYUNDEF)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex.  */
static const yytype_int8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27
};

#if YYDEBUG
/* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_int16 yyrline[] =
{
       0,    56,    56,    68,    69,    84,    99,   100,   101,   116,
     129,   130,   139,   149,   150,   169,   170,   171,   172,   173,
     182,   197,   212,   222,   232,   241,   253,   254,   255,   256,
     257,   258,   267,   271,   275,   281,   285,   289,   293,   297,
     307,   308,   309
};
#endif

/** Accessing symbol of state STATE.  */
#define YY_ACCESSING_SYMBOL(State) YY_CAST (yysymbol_kind_t, yystos[State])

#if 1
/* The user-facing name of the symbol whose (internal) number is
   YYSYMBOL.  No bounds checking.  */
static const char *yysymbol_name (yysymbol_kind_t yysymbol) YY_ATTRIBUTE_UNUSED;

/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "\"end of file\"", "error", "\"invalid token\"", "TOKEN_ID",
  "TOKEN_NUMBER", "TOKEN_FUN", "TOKEN_RET", "TOKEN_IF", "TOKEN_WHILE",
  "TOKEN_ENT", "TOKEN_FLO", "TOKEN_RELOP_LT", "TOKEN_RELOP_LE",
  "TOKEN_RELOP_EQ", "TOKEN_RELOP_NE", "TOKEN_RELOP_GT", "TOKEN_RELOP_GE",
  "TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_MULT", "TOKEN_DIV", "TOKEN_ASSIGN",
  "TOKEN_SEMICOLON", "TOKEN_COMMA", "TOKEN_LPAREN", "TOKEN_RPAREN",
  "TOKEN_LBRACE", "TOKEN_RBRACE", "$accept", "program", "function_list",
  "function", "param_list", "param", "type", "block", "statement_list",
  "statement", "declaration_stmt", "assignment_stmt", "if_stmt",
  "while_stmt", "return_stmt", "condition", "relop", "expr", "arg_list", YY_NULLPTR
};

static const char *
yysymbol_name (yysymbol_kind_t yysymbol)
{
  return yytname[yysymbol];
}
#endif

#define YYPACT_NINF (-52)

#define yypact_value_is_default(Yyn) \
  ((Yyn) == YYPACT_NINF)

#define YYTABLE_NINF (-1)

#define yytable_value_is_error(Yyn) \
  0

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
static const yytype_int8 yypact[] =
{
      11,    -2,    29,    11,   -52,     7,   -52,   -52,    -6,   -52,
     -52,    -8,   -52,    41,    -6,     6,   -52,   -52,   -52,   -52,
      -1,    24,     9,    40,    46,   -52,    44,   -52,   -52,   -52,
     -52,   -52,   -52,     9,    52,   -52,     9,    37,     9,     9,
      27,    43,     9,    33,     9,     9,     9,     9,   -52,    53,
      23,    54,     9,   -52,    55,    -4,   -52,     8,     8,   -52,
     -52,     6,   -52,   -52,   -52,   -52,   -52,   -52,     9,     6,
      49,     9,   -52,   -52,    55,   -52,   -52,    55
};

/* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
   Performed when YYTABLE does not specify something else to do.  Zero
   means the default is an error.  */
static const yytype_int8 yydefact[] =
{
       0,     0,     0,     2,     3,     0,     1,     4,     6,    10,
      11,     0,     7,     0,     0,     0,     9,     8,    13,     5,
       0,     0,     0,     0,     0,    12,     0,    14,    15,    16,
      17,    18,    19,     0,    32,    33,     0,     0,     0,     0,
       0,     0,    40,     0,     0,     0,     0,     0,    24,     0,
       0,     0,     0,    21,    41,     0,    39,    35,    36,    37,
      38,     0,    26,    27,    28,    29,    30,    31,     0,     0,
       0,     0,    34,    22,    25,    23,    20,    42
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int8 yypgoto[] =
{
     -52,   -52,   -52,    74,   -52,    66,    61,   -51,   -52,   -52,
     -52,   -52,   -52,   -52,   -52,    45,   -52,   -22,   -52
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
       0,     2,     3,     4,    11,    12,    13,    19,    20,    27,
      28,    29,    30,    31,    32,    49,    68,    50,    55
};

/* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule whose
   number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int8 yytable[] =
{
      37,     5,    21,     9,    10,    22,    23,    24,     9,    10,
      73,    41,    34,    35,    43,    14,     1,    15,    75,    71,
      54,    72,    57,    58,    59,    60,    25,    46,    47,     6,
      70,     8,    18,    36,    62,    63,    64,    65,    66,    67,
      44,    45,    46,    47,    16,    33,    74,    40,    52,    77,
      44,    45,    46,    47,    44,    45,    46,    47,    56,    48,
      44,    45,    46,    47,    38,    53,    44,    45,    46,    47,
      39,    76,    44,    45,    46,    47,    42,     7,    61,    69,
      17,    26,     0,     0,    51
};

static const yytype_int8 yycheck[] =
{
      22,     3,     3,     9,    10,     6,     7,     8,     9,    10,
      61,    33,     3,     4,    36,    23,     5,    25,    69,    23,
      42,    25,    44,    45,    46,    47,    27,    19,    20,     0,
      52,    24,    26,    24,    11,    12,    13,    14,    15,    16,
      17,    18,    19,    20,     3,    21,    68,     3,    21,    71,
      17,    18,    19,    20,    17,    18,    19,    20,    25,    22,
      17,    18,    19,    20,    24,    22,    17,    18,    19,    20,
      24,    22,    17,    18,    19,    20,    24,     3,    25,    25,
      14,    20,    -1,    -1,    39
};

/* YYSTOS[STATE-NUM] -- The symbol kind of the accessing symbol of
   state STATE-NUM.  */
static const yytype_int8 yystos[] =
{
       0,     5,    29,    30,    31,     3,     0,    31,    24,     9,
      10,    32,    33,    34,    23,    25,     3,    33,    26,    35,
      36,     3,     6,     7,     8,    27,    34,    37,    38,    39,
      40,    41,    42,    21,     3,     4,    24,    45,    24,    24,
       3,    45,    24,    45,    17,    18,    19,    20,    22,    43,
      45,    43,    21,    22,    45,    46,    25,    45,    45,    45,
      45,    25,    11,    12,    13,    14,    15,    16,    44,    25,
      45,    23,    25,    35,    45,    35,    22,    45
};

/* YYR1[RULE-NUM] -- Symbol kind of the left-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr1[] =
{
       0,    28,    29,    30,    30,    31,    32,    32,    32,    33,
      34,    34,    35,    36,    36,    37,    37,    37,    37,    37,
      38,    39,    40,    41,    42,    43,    44,    44,    44,    44,
      44,    44,    45,    45,    45,    45,    45,    45,    45,    45,
      46,    46,    46
};

/* YYR2[RULE-NUM] -- Number of symbols on the right-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr2[] =
{
       0,     2,     1,     1,     2,     6,     0,     1,     3,     2,
       1,     1,     3,     0,     2,     1,     1,     1,     1,     1,
       5,     4,     5,     5,     3,     3,     1,     1,     1,     1,
       1,     1,     1,     1,     4,     3,     3,     3,     3,     3,
       0,     1,     3
};


enum { YYENOMEM = -2 };

#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = YYEMPTY)

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab
#define YYNOMEM         goto yyexhaustedlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                    \
  do                                                              \
    if (yychar == YYEMPTY)                                        \
      {                                                           \
        yychar = (Token);                                         \
        yylval = (Value);                                         \
        YYPOPSTACK (yylen);                                       \
        yystate = *yyssp;                                         \
        goto yybackup;                                            \
      }                                                           \
    else                                                          \
      {                                                           \
        yyerror (YY_("syntax error: cannot back up")); \
        YYERROR;                                                  \
      }                                                           \
  while (0)

/* Backward compatibility with an undocumented macro.
   Use YYerror or YYUNDEF. */
#define YYERRCODE YYUNDEF


/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)




# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Kind, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*-----------------------------------.
| Print this symbol's value on YYO.  |
`-----------------------------------*/

static void
yy_symbol_value_print (FILE *yyo,
                       yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  FILE *yyoutput = yyo;
  YY_USE (yyoutput);
  if (!yyvaluep)
    return;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/*---------------------------.
| Print this symbol on YYO.  |
`---------------------------*/

static void
yy_symbol_print (FILE *yyo,
                 yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyo, "%s %s (",
             yykind < YYNTOKENS ? "token" : "nterm", yysymbol_name (yykind));

  yy_symbol_value_print (yyo, yykind, yyvaluep);
  YYFPRINTF (yyo, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yy_state_t *yybottom, yy_state_t *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yy_state_t *yyssp, YYSTYPE *yyvsp,
                 int yyrule)
{
  int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %d):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       YY_ACCESSING_SYMBOL (+yyssp[yyi + 1 - yynrhs]),
                       &yyvsp[(yyi + 1) - (yynrhs)]);
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args) ((void) 0)
# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif


/* Context of a parse error.  */
typedef struct
{
  yy_state_t *yyssp;
  yysymbol_kind_t yytoken;
} yypcontext_t;

/* Put in YYARG at most YYARGN of the expected tokens given the
   current YYCTX, and return the number of tokens stored in YYARG.  If
   YYARG is null, return the number of expected tokens (guaranteed to
   be less than YYNTOKENS).  Return YYENOMEM on memory exhaustion.
   Return 0 if there are more than YYARGN expected tokens, yet fill
   YYARG up to YYARGN. */
static int
yypcontext_expected_tokens (const yypcontext_t *yyctx,
                            yysymbol_kind_t yyarg[], int yyargn)
{
  /* Actual size of YYARG. */
  int yycount = 0;
  int yyn = yypact[+*yyctx->yyssp];
  if (!yypact_value_is_default (yyn))
    {
      /* Start YYX at -YYN if negative to avoid negative indexes in
         YYCHECK.  In other words, skip the first -YYN actions for
         this state because they are default actions.  */
      int yyxbegin = yyn < 0 ? -yyn : 0;
      /* Stay within bounds of both yycheck and yytname.  */
      int yychecklim = YYLAST - yyn + 1;
      int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
      int yyx;
      for (yyx = yyxbegin; yyx < yyxend; ++yyx)
        if (yycheck[yyx + yyn] == yyx && yyx != YYSYMBOL_YYerror
            && !yytable_value_is_error (yytable[yyx + yyn]))
          {
            if (!yyarg)
              ++yycount;
            else if (yycount == yyargn)
              return 0;
            else
              yyarg[yycount++] = YY_CAST (yysymbol_kind_t, yyx);
          }
    }
  if (yyarg && yycount == 0 && 0 < yyargn)
    yyarg[0] = YYSYMBOL_YYEMPTY;
  return yycount;
}




#ifndef yystrlen
# if defined __GLIBC__ && defined _STRING_H
#  define yystrlen(S) (YY_CAST (YYPTRDIFF_T, strlen (S)))
# else
/* Return the length of YYSTR.  */
static YYPTRDIFF_T
yystrlen (const char *yystr)
{
  YYPTRDIFF_T yylen;
  for (yylen = 0; yystr[yylen]; yylen++)
    continue;
  return yylen;
}
# endif
#endif

#ifndef yystpcpy
# if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#  define yystpcpy stpcpy
# else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
yystpcpy (char *yydest, const char *yysrc)
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
# endif
#endif

#ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYPTRDIFF_T
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      YYPTRDIFF_T yyn = 0;
      char const *yyp = yystr;
      for (;;)
        switch (*++yyp)
          {
          case '\'':
          case ',':
            goto do_not_strip_quotes;

          case '\\':
            if (*++yyp != '\\')
              goto do_not_strip_quotes;
            else
              goto append;

          append:
          default:
            if (yyres)
              yyres[yyn] = *yyp;
            yyn++;
            break;

          case '"':
            if (yyres)
              yyres[yyn] = '\0';
            return yyn;
          }
    do_not_strip_quotes: ;
    }

  if (yyres)
    return yystpcpy (yyres, yystr) - yyres;
  else
    return yystrlen (yystr);
}
#endif


static int
yy_syntax_error_arguments (const yypcontext_t *yyctx,
                           yysymbol_kind_t yyarg[], int yyargn)
{
  /* Actual size of YYARG. */
  int yycount = 0;
  /* There are many possibilities here to consider:
     - If this state is a consistent state with a default action, then
       the only way this function was invoked is if the default action
       is an error action.  In that case, don't check for expected
       tokens because there are none.
     - The only way there can be no lookahead present (in yychar) is if
       this state is a consistent state with a default action.  Thus,
       detecting the absence of a lookahead is sufficient to determine
       that there is no unexpected or expected token to report.  In that
       case, just report a simple "syntax error".
     - Don't assume there isn't a lookahead just because this state is a
       consistent state with a default action.  There might have been a
       previous inconsistent state, consistent state with a non-default
       action, or user semantic action that manipulated yychar.
     - Of course, the expected token list depends on states to have
       correct lookahead information, and it depends on the parser not
       to perform extra reductions after fetching a lookahead from the
       scanner and before detecting a syntax error.  Thus, state merging
       (from LALR or IELR) and default reductions corrupt the expected
       token list.  However, the list is correct for canonical LR with
       one exception: it will still contain any token that will not be
       accepted due to an error action in a later state.
  */
  if (yyctx->yytoken != YYSYMBOL_YYEMPTY)
    {
      int yyn;
      if (yyarg)
        yyarg[yycount] = yyctx->yytoken;
      ++yycount;
      yyn = yypcontext_expected_tokens (yyctx,
                                        yyarg ? yyarg + 1 : yyarg, yyargn - 1);
      if (yyn == YYENOMEM)
        return YYENOMEM;
      else
        yycount += yyn;
    }
  return yycount;
}

/* Copy into *YYMSG, which is of size *YYMSG_ALLOC, an error message
   about the unexpected token YYTOKEN for the state stack whose top is
   YYSSP.

   Return 0 if *YYMSG was successfully written.  Return -1 if *YYMSG is
   not large enough to hold the message.  In that case, also set
   *YYMSG_ALLOC to the required number of bytes.  Return YYENOMEM if the
   required number of bytes is too large to store.  */
static int
yysyntax_error (YYPTRDIFF_T *yymsg_alloc, char **yymsg,
                const yypcontext_t *yyctx)
{
  enum { YYARGS_MAX = 5 };
  /* Internationalized format string. */
  const char *yyformat = YY_NULLPTR;
  /* Arguments of yyformat: reported tokens (one for the "unexpected",
     one per "expected"). */
  yysymbol_kind_t yyarg[YYARGS_MAX];
  /* Cumulated lengths of YYARG.  */
  YYPTRDIFF_T yysize = 0;

  /* Actual size of YYARG. */
  int yycount = yy_syntax_error_arguments (yyctx, yyarg, YYARGS_MAX);
  if (yycount == YYENOMEM)
    return YYENOMEM;

  switch (yycount)
    {
#define YYCASE_(N, S)                       \
      case N:                               \
        yyformat = S;                       \
        break
    default: /* Avoid compiler warnings. */
      YYCASE_(0, YY_("syntax error"));
      YYCASE_(1, YY_("syntax error, unexpected %s"));
      YYCASE_(2, YY_("syntax error, unexpected %s, expecting %s"));
      YYCASE_(3, YY_("syntax error, unexpected %s, expecting %s or %s"));
      YYCASE_(4, YY_("syntax error, unexpected %s, expecting %s or %s or %s"));
      YYCASE_(5, YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s"));
#undef YYCASE_
    }

  /* Compute error message size.  Don't count the "%s"s, but reserve
     room for the terminator.  */
  yysize = yystrlen (yyformat) - 2 * yycount + 1;
  {
    int yyi;
    for (yyi = 0; yyi < yycount; ++yyi)
      {
        YYPTRDIFF_T yysize1
          = yysize + yytnamerr (YY_NULLPTR, yytname[yyarg[yyi]]);
        if (yysize <= yysize1 && yysize1 <= YYSTACK_ALLOC_MAXIMUM)
          yysize = yysize1;
        else
          return YYENOMEM;
      }
  }

  if (*yymsg_alloc < yysize)
    {
      *yymsg_alloc = 2 * yysize;
      if (! (yysize <= *yymsg_alloc
             && *yymsg_alloc <= YYSTACK_ALLOC_MAXIMUM))
        *yymsg_alloc = YYSTACK_ALLOC_MAXIMUM;
      return -1;
    }

  /* Avoid sprintf, as that infringes on the user's name space.
     Don't have undefined behavior even if the translation
     produced a string with the wrong number of "%s"s.  */
  {
    char *yyp = *yymsg;
    int yyi = 0;
    while ((*yyp = *yyformat) != '\0')
      if (*yyp == '%' && yyformat[1] == 's' && yyi < yycount)
        {
          yyp += yytnamerr (yyp, yytname[yyarg[yyi++]]);
          yyformat += 2;
        }
      else
        {
          ++yyp;
          ++yyformat;
        }
  }
  return 0;
}


/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg,
            yysymbol_kind_t yykind, YYSTYPE *yyvaluep)
{
  YY_USE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yykind, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/* Lookahead token kind.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;




/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    yy_state_fast_t yystate = 0;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus = 0;

    /* Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* Their size.  */
    YYPTRDIFF_T yystacksize = YYINITDEPTH;

    /* The state stack: array, bottom, top.  */
    yy_state_t yyssa[YYINITDEPTH];
    yy_state_t *yyss = yyssa;
    yy_state_t *yyssp = yyss;

    /* The semantic value stack: array, bottom, top.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs = yyvsa;
    YYSTYPE *yyvsp = yyvs;

  int yyn;
  /* The return value of yyparse.  */
  int yyresult;
  /* Lookahead symbol kind.  */
  yysymbol_kind_t yytoken = YYSYMBOL_YYEMPTY;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;

  /* Buffer for error messages, and its allocated size.  */
  char yymsgbuf[128];
  char *yymsg = yymsgbuf;
  YYPTRDIFF_T yymsg_alloc = sizeof yymsgbuf;

#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yychar = YYEMPTY; /* Cause a token to be read.  */

  goto yysetstate;


/*------------------------------------------------------------.
| yynewstate -- push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;


/*--------------------------------------------------------------------.
| yysetstate -- set current state (the top of the stack) to yystate.  |
`--------------------------------------------------------------------*/
yysetstate:
  YYDPRINTF ((stderr, "Entering state %d\n", yystate));
  YY_ASSERT (0 <= yystate && yystate < YYNSTATES);
  YY_IGNORE_USELESS_CAST_BEGIN
  *yyssp = YY_CAST (yy_state_t, yystate);
  YY_IGNORE_USELESS_CAST_END
  YY_STACK_PRINT (yyss, yyssp);

  if (yyss + yystacksize - 1 <= yyssp)
#if !defined yyoverflow && !defined YYSTACK_RELOCATE
    YYNOMEM;
#else
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYPTRDIFF_T yysize = yyssp - yyss + 1;

# if defined yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        yy_state_t *yyss1 = yyss;
        YYSTYPE *yyvs1 = yyvs;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * YYSIZEOF (*yyssp),
                    &yyvs1, yysize * YYSIZEOF (*yyvsp),
                    &yystacksize);
        yyss = yyss1;
        yyvs = yyvs1;
      }
# else /* defined YYSTACK_RELOCATE */
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        YYNOMEM;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yy_state_t *yyss1 = yyss;
        union yyalloc *yyptr =
          YY_CAST (union yyalloc *,
                   YYSTACK_ALLOC (YY_CAST (YYSIZE_T, YYSTACK_BYTES (yystacksize))));
        if (! yyptr)
          YYNOMEM;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YY_IGNORE_USELESS_CAST_BEGIN
      YYDPRINTF ((stderr, "Stack size increased to %ld\n",
                  YY_CAST (long, yystacksize)));
      YY_IGNORE_USELESS_CAST_END

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }
#endif /* !defined yyoverflow && !defined YYSTACK_RELOCATE */


  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:
  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either empty, or end-of-input, or a valid lookahead.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token\n"));
      yychar = yylex ();
    }

  if (yychar <= YYEOF)
    {
      yychar = YYEOF;
      yytoken = YYSYMBOL_YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else if (yychar == YYerror)
    {
      /* The scanner already issued an error message, process directly
         to error recovery.  But do not keep the error token as
         lookahead, it is too special and may lead us to an endless
         loop in error recovery. */
      yychar = YYUNDEF;
      yytoken = YYSYMBOL_YYerror;
      goto yyerrlab1;
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);
  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  /* Discard the shifted token.  */
  yychar = YYEMPTY;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
  case 2: /* program: function_list  */
#line 56 ".\\analizador_sintactico.y"
                       { 
        (yyval.node) = create_node(NODE_PROGRAM, (yyvsp[0].node), NULL);
        ast_root = (yyval.node);  // Asigna la raíz del AST para su posterior procesamiento.
    }
#line 1446 "analizador_sintactico.tab.c"
    break;

  case 3: /* function_list: function  */
#line 68 ".\\analizador_sintactico.y"
                                      { (yyval.node) = (yyvsp[0].node); }
#line 1452 "analizador_sintactico.tab.c"
    break;

  case 4: /* function_list: function_list function  */
#line 69 ".\\analizador_sintactico.y"
                                      { 
                                        (yyval.node) = (yyvsp[-1].node);
                                        // Se recorre la lista hasta el último nodo y se enlaza la nueva función.
                                        Node *last = (yyvsp[-1].node);
                                        while(last->next) last = last->next;
                                        last->next = (yyvsp[0].node);
                                     }
#line 1464 "analizador_sintactico.tab.c"
    break;

  case 5: /* function: TOKEN_FUN TOKEN_ID TOKEN_LPAREN param_list TOKEN_RPAREN block  */
#line 85 ".\\analizador_sintactico.y"
                                     { 
                                        Node *func = create_node(NODE_FUNCTION, (yyvsp[-2].node), (yyvsp[0].node));
                                        func->symbol_index = (yyvsp[-4].symbol_index);  // Asigna el índice del identificador de la función.
                                        (yyval.node) = func;
                                     }
#line 1474 "analizador_sintactico.tab.c"
    break;

  case 6: /* param_list: %empty  */
#line 99 ".\\analizador_sintactico.y"
                                      { (yyval.node) = NULL; }
#line 1480 "analizador_sintactico.tab.c"
    break;

  case 7: /* param_list: param  */
#line 100 ".\\analizador_sintactico.y"
                                      { (yyval.node) = (yyvsp[0].node); }
#line 1486 "analizador_sintactico.tab.c"
    break;

  case 8: /* param_list: param_list TOKEN_COMMA param  */
#line 101 ".\\analizador_sintactico.y"
                                      {
                                        (yyval.node) = (yyvsp[-2].node);
                                        // Se recorre la lista de parámetros y se enlaza el nuevo parámetro.
                                        Node *last = (yyvsp[-2].node);
                                        while(last->next) last = last->next;
                                        last->next = (yyvsp[0].node);
                                     }
#line 1498 "analizador_sintactico.tab.c"
    break;

  case 9: /* param: type TOKEN_ID  */
#line 116 ".\\analizador_sintactico.y"
                                      {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = (yyvsp[0].symbol_index);  // Asigna el índice del identificador del parámetro.
                                        (yyval.node) = id;
                                     }
#line 1508 "analizador_sintactico.tab.c"
    break;

  case 12: /* block: TOKEN_LBRACE statement_list TOKEN_RBRACE  */
#line 140 ".\\analizador_sintactico.y"
                                     { (yyval.node) = create_node(NODE_BLOCK, (yyvsp[-1].node), NULL); }
#line 1514 "analizador_sintactico.tab.c"
    break;

  case 13: /* statement_list: %empty  */
#line 149 ".\\analizador_sintactico.y"
                                      { (yyval.node) = NULL; }
#line 1520 "analizador_sintactico.tab.c"
    break;

  case 14: /* statement_list: statement_list statement  */
#line 150 ".\\analizador_sintactico.y"
                                      {
                                        if ((yyvsp[-1].node) == NULL) {
                                            (yyval.node) = (yyvsp[0].node);
                                        } else {
                                            (yyval.node) = (yyvsp[-1].node);
                                            // Se recorre la lista de sentencias y se enlaza la nueva sentencia.
                                            Node *last = (yyvsp[-1].node);
                                            while(last->next) last = last->next;
                                            last->next = (yyvsp[0].node);
                                        }
                                     }
#line 1536 "analizador_sintactico.tab.c"
    break;

  case 20: /* declaration_stmt: type TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON  */
#line 183 ".\\analizador_sintactico.y"
                                     {
                                        // Se crea un nodo identificador y se asocia a la declaración.
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = (yyvsp[-3].symbol_index);
                                        (yyval.node) = create_node(NODE_DECLARATION, id, (yyvsp[-1].node));
                                     }
#line 1547 "analizador_sintactico.tab.c"
    break;

  case 21: /* assignment_stmt: TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON  */
#line 198 ".\\analizador_sintactico.y"
                                     {
                                        // Se crea un nodo identificador para la variable a la que se asigna el valor.
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = (yyvsp[-3].symbol_index);
                                        (yyval.node) = create_node(NODE_ASSIGNMENT, id, (yyvsp[-1].node));
                                     }
#line 1558 "analizador_sintactico.tab.c"
    break;

  case 22: /* if_stmt: TOKEN_IF TOKEN_LPAREN condition TOKEN_RPAREN block  */
#line 213 ".\\analizador_sintactico.y"
                                     { (yyval.node) = create_node(NODE_IF, (yyvsp[-2].node), (yyvsp[0].node)); }
#line 1564 "analizador_sintactico.tab.c"
    break;

  case 23: /* while_stmt: TOKEN_WHILE TOKEN_LPAREN condition TOKEN_RPAREN block  */
#line 223 ".\\analizador_sintactico.y"
                                     { (yyval.node) = create_node(NODE_WHILE, (yyvsp[-2].node), (yyvsp[0].node)); }
#line 1570 "analizador_sintactico.tab.c"
    break;

  case 24: /* return_stmt: TOKEN_RET expr TOKEN_SEMICOLON  */
#line 232 ".\\analizador_sintactico.y"
                                      { (yyval.node) = create_node(NODE_RETURN, (yyvsp[-1].node), NULL); }
#line 1576 "analizador_sintactico.tab.c"
    break;

  case 25: /* condition: expr relop expr  */
#line 241 ".\\analizador_sintactico.y"
                                     { 
                                        (yyval.node) = create_node(NODE_BINARY_OP, (yyvsp[-2].node), (yyvsp[0].node));
                                        (yyval.node)->symbol_index = (yyvsp[-1].symbol_index);  // El índice del operador relacional.
                                     }
#line 1585 "analizador_sintactico.tab.c"
    break;

  case 26: /* relop: TOKEN_RELOP_LT  */
#line 253 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_LT; }
#line 1591 "analizador_sintactico.tab.c"
    break;

  case 27: /* relop: TOKEN_RELOP_LE  */
#line 254 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_LE; }
#line 1597 "analizador_sintactico.tab.c"
    break;

  case 28: /* relop: TOKEN_RELOP_EQ  */
#line 255 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_EQ; }
#line 1603 "analizador_sintactico.tab.c"
    break;

  case 29: /* relop: TOKEN_RELOP_NE  */
#line 256 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_NE; }
#line 1609 "analizador_sintactico.tab.c"
    break;

  case 30: /* relop: TOKEN_RELOP_GT  */
#line 257 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_GT; }
#line 1615 "analizador_sintactico.tab.c"
    break;

  case 31: /* relop: TOKEN_RELOP_GE  */
#line 258 ".\\analizador_sintactico.y"
                                     { (yyval.symbol_index) = TOKEN_RELOP_GE; }
#line 1621 "analizador_sintactico.tab.c"
    break;

  case 32: /* expr: TOKEN_ID  */
#line 267 ".\\analizador_sintactico.y"
                                      {
                                        (yyval.node) = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        (yyval.node)->symbol_index = (yyvsp[0].symbol_index);
                                     }
#line 1630 "analizador_sintactico.tab.c"
    break;

  case 33: /* expr: TOKEN_NUMBER  */
#line 271 ".\\analizador_sintactico.y"
                                      {
                                        (yyval.node) = create_node(NODE_NUMBER, NULL, NULL);
                                        (yyval.node)->symbol_index = (yyvsp[0].symbol_index);
                                     }
#line 1639 "analizador_sintactico.tab.c"
    break;

  case 34: /* expr: TOKEN_ID TOKEN_LPAREN arg_list TOKEN_RPAREN  */
#line 276 ".\\analizador_sintactico.y"
                                     {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = (yyvsp[-3].symbol_index);
                                        (yyval.node) = create_node(NODE_FUNCTION_CALL, id, (yyvsp[-1].node));
                                     }
#line 1649 "analizador_sintactico.tab.c"
    break;

  case 35: /* expr: expr TOKEN_PLUS expr  */
#line 281 ".\\analizador_sintactico.y"
                                     { 
                                        (yyval.node) = create_node(NODE_BINARY_OP, (yyvsp[-2].node), (yyvsp[0].node)); 
                                        (yyval.node)->symbol_index = TOKEN_PLUS;
                                     }
#line 1658 "analizador_sintactico.tab.c"
    break;

  case 36: /* expr: expr TOKEN_MINUS expr  */
#line 285 ".\\analizador_sintactico.y"
                                     { 
                                        (yyval.node) = create_node(NODE_BINARY_OP, (yyvsp[-2].node), (yyvsp[0].node));
                                        (yyval.node)->symbol_index = TOKEN_MINUS;
                                     }
#line 1667 "analizador_sintactico.tab.c"
    break;

  case 37: /* expr: expr TOKEN_MULT expr  */
#line 289 ".\\analizador_sintactico.y"
                                     { 
                                        (yyval.node) = create_node(NODE_BINARY_OP, (yyvsp[-2].node), (yyvsp[0].node));
                                        (yyval.node)->symbol_index = TOKEN_MULT;
                                     }
#line 1676 "analizador_sintactico.tab.c"
    break;

  case 38: /* expr: expr TOKEN_DIV expr  */
#line 293 ".\\analizador_sintactico.y"
                                     { 
                                        (yyval.node) = create_node(NODE_BINARY_OP, (yyvsp[-2].node), (yyvsp[0].node));
                                        (yyval.node)->symbol_index = TOKEN_DIV;
                                     }
#line 1685 "analizador_sintactico.tab.c"
    break;

  case 39: /* expr: TOKEN_LPAREN expr TOKEN_RPAREN  */
#line 297 ".\\analizador_sintactico.y"
                                     { (yyval.node) = (yyvsp[-1].node); }
#line 1691 "analizador_sintactico.tab.c"
    break;

  case 40: /* arg_list: %empty  */
#line 307 ".\\analizador_sintactico.y"
                                      { (yyval.node) = NULL; }
#line 1697 "analizador_sintactico.tab.c"
    break;

  case 41: /* arg_list: expr  */
#line 308 ".\\analizador_sintactico.y"
                                      { (yyval.node) = (yyvsp[0].node); }
#line 1703 "analizador_sintactico.tab.c"
    break;

  case 42: /* arg_list: arg_list TOKEN_COMMA expr  */
#line 309 ".\\analizador_sintactico.y"
                                      {
                                        (yyval.node) = (yyvsp[-2].node);
                                        // Se enlaza el nuevo argumento al final de la lista.
                                        Node *last = (yyvsp[-2].node);
                                        while(last->next) last = last->next;
                                        last->next = (yyvsp[0].node);
                                     }
#line 1715 "analizador_sintactico.tab.c"
    break;


#line 1719 "analizador_sintactico.tab.c"

      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", YY_CAST (yysymbol_kind_t, yyr1[yyn]), &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */
  {
    const int yylhs = yyr1[yyn] - YYNTOKENS;
    const int yyi = yypgoto[yylhs] + *yyssp;
    yystate = (0 <= yyi && yyi <= YYLAST && yycheck[yyi] == *yyssp
               ? yytable[yyi]
               : yydefgoto[yylhs]);
  }

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == YYEMPTY ? YYSYMBOL_YYEMPTY : YYTRANSLATE (yychar);
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
      {
        yypcontext_t yyctx
          = {yyssp, yytoken};
        char const *yymsgp = YY_("syntax error");
        int yysyntax_error_status;
        yysyntax_error_status = yysyntax_error (&yymsg_alloc, &yymsg, &yyctx);
        if (yysyntax_error_status == 0)
          yymsgp = yymsg;
        else if (yysyntax_error_status == -1)
          {
            if (yymsg != yymsgbuf)
              YYSTACK_FREE (yymsg);
            yymsg = YY_CAST (char *,
                             YYSTACK_ALLOC (YY_CAST (YYSIZE_T, yymsg_alloc)));
            if (yymsg)
              {
                yysyntax_error_status
                  = yysyntax_error (&yymsg_alloc, &yymsg, &yyctx);
                yymsgp = yymsg;
              }
            else
              {
                yymsg = yymsgbuf;
                yymsg_alloc = sizeof yymsgbuf;
                yysyntax_error_status = YYENOMEM;
              }
          }
        yyerror (yymsgp);
        if (yysyntax_error_status == YYENOMEM)
          YYNOMEM;
      }
    }

  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= YYEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == YYEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = YYEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:
  /* Pacify compilers when the user code never invokes YYERROR and the
     label yyerrorlab therefore never appears in user code.  */
  if (0)
    YYERROR;
  ++yynerrs;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  /* Pop stack until we find a state that shifts the error token.  */
  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYSYMBOL_YYerror;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYSYMBOL_YYerror)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  YY_ACCESSING_SYMBOL (yystate), yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", YY_ACCESSING_SYMBOL (yyn), yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturnlab;


/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturnlab;


/*-----------------------------------------------------------.
| yyexhaustedlab -- YYNOMEM (memory exhaustion) comes here.  |
`-----------------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  goto yyreturnlab;


/*----------------------------------------------------------.
| yyreturnlab -- parsing is finished, clean up and return.  |
`----------------------------------------------------------*/
yyreturnlab:
  if (yychar != YYEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  YY_ACCESSING_SYMBOL (+*yyssp), yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
  if (yymsg != yymsgbuf)
    YYSTACK_FREE (yymsg);
  return yyresult;
}

#line 318 ".\\analizador_sintactico.y"


/*
 * Función: yyerror
 * ----------------
 * Función de manejo de errores de parseo.
 * Imprime un mensaje de error junto con el número de línea donde ocurrió.
 */
void yyerror(const char *s) {
    fprintf(stderr, "Error: %s at line %d\n", s, yylineno);
}

/*
 * Función: main
 * -------------
 * Función principal del compilador.
 * Se encarga de inicializar el proceso de compilación, abrir el archivo de entrada,
 * ejecutar el análisis sintáctico, el análisis semántico y la generación de código intermedio.
 */
int main(int argc, char **argv) {
    // Mensaje de inicio del compilador.
    printf("Debug: Iniciando compilador\n");
    
    // Verificar que se haya proporcionado al menos un archivo de entrada.
    if (argc < 2) {
        fprintf(stderr, "Debug: No se proporciono archivo de entrada\n");
        fprintf(stderr, "Uso: %s <archivo_de_entrada>\n", argv[0]);
        return 1;
    }

    // Intentar abrir el archivo de entrada y notificar el estado.
    printf("Debug: Intentando abrir archivo: %s\n", argv[1]);
    if (!(yyin = fopen(argv[1], "r"))) {
        fprintf(stderr, "Debug: Error al abrir archivo de entrada\n");
        perror(argv[1]);
        return 1;
    }
    printf("Debug: Archivo de entrada abierto exitosamente\n");

    // Iniciar el proceso de analisis sintactico.
    printf("Debug: Iniciando analisis sintactico\n");
    int parse_result = yyparse();
    printf("Debug: Resultado del analisis = %d (0 indica exito)\n", parse_result);
    
    // Si el analisis sintactico es exitoso, proceder con el analisis semantico y la generacion de codigo intermedio.
    if (parse_result == 0) {
        if (ast_root) {
            printf("Debug: AST creado exitosamente\n");
            printf("Debug: Iniciando analisis semantico\n");
            init_semantic_analysis(ast_root);
            printf("Debug: Analisis semantico completado\n");
            
            printf("Debug: Generando codigo intermedio\n");
            char output_file[256];
            strncpy(output_file, argv[2], sizeof(output_file) - 1);
            output_file[sizeof(output_file) - 1] = '\0';
            char *dot = strrchr(output_file, '.');
            if (dot) {
                strcpy(dot, ".tac");
            } else {
                strcat(output_file, ".tac");
            }
            generate_intermediate_code(ast_root, output_file);
            printf("Debug: Generacion de codigo intermedio completada\n");
        } else {
            fprintf(stderr, "Debug: La raiz del AST es NULL a pesar de un analisis exitoso\n");
            return 1;
        }
    } else {
        fprintf(stderr, "Debug: Analisis sintactico fallido\n");
        return 1;
    }
    
    // Mensaje final indicando que la compilacion se completo exitosamente.
    printf("Debug: Compilacion completada exitosamente\n");
    return 0;
}

