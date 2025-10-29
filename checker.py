# checker.py
'''
Analizador Semántico para B-Minor 2025
Este archivo implementa la verificación de tipos y análisis semántico
del lenguaje B-Minor.
'''
from rich import print
from typing import Union, List, Optional
from model import *
from symtab import Symtab
from typesys import typenames, check_binop, check_unaryop, CheckError


class SemanticError(Exception):
    """Excepción para errores semánticos"""
    pass


class Check:
    def __init__(self):
        self.errors = []
        self.current_function = None  # Para validar returns
        self.in_loop = False  # Para validar break/continue si los implementas

    def error(self, msg, node=None):
        """Registra un error semántico"""
        self.errors.append(msg)
        print(f"[red]Error semántico:[/red] {msg}")

    @classmethod
    def check(cls, program: Program):
        """
        Punto de entrada principal para el análisis semántico
        Retorna la tabla de símbolos global y la lista de errores
        """
        checker = cls()
        env = Symtab('global')

        # Primera pasada: Declarar todas las funciones y variables globales
        for decl in program.body:
            if type(decl).__name__ == 'FuncDecl':
                checker.declare_function(decl, env)
            elif type(decl).__name__ in ['VarDecl', 'VarDeclInit']:
                checker.visit(decl, env)

        # Segunda pasada: Verificar cuerpos de funciones
        for decl in program.body:
            if type(decl).__name__ == 'FuncDecl' and decl.body:
                checker.check_function_body(decl, env)

        return env, checker.errors

    def declare_function(self, n, env: Symtab):
        """Declara una función sin verificar su cuerpo"""
        func_type = self.visit(n.type_func, env)

        try:
            n.type_resolved = func_type
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            self.error(f"La función '{n.name}' ya fue declarada con un tipo diferente")
        except Symtab.SymbolDefinedError:
            # Verificar que las declaraciones sean compatibles
            existing = env.get(n.name)
            if existing and type(existing).__name__ == 'FuncDecl':
                if not self.types_match(func_type, existing.type_resolved):
                    self.error(f"Declaración inconsistente de función '{n.name}'")

    def check_function_body(self, n, env: Symtab):
        """Verifica el cuerpo de una función"""
        if not n.body:
            return

        prev_func = self.current_function
        self.current_function = n

        # Crear tabla de símbolos local
        local_env = Symtab(f"func_{n.name}", env)

        # Agregar parámetros al scope local
        if n.type_func and n.type_func.params:
            for param in n.type_func.params:
                self.visit(param, local_env)

        # Verificar el cuerpo
        for stmt in n.body:
            self.visit(stmt, local_env)

        self.current_function = prev_func

    def types_match(self, type1, type2):
        """Compara si dos tipos son equivalentes"""
        if type1 == type2:
            return True

        # Normalizar tipos string a comparar
        str1 = str(type1) if type1 else ""
        str2 = str(type2) if type2 else ""

        # Caso especial: arrays con y sin tamaño son compatibles
        # array[] tipo == array[N] tipo
        if 'array' in str1 and 'array' in str2:
            # Extraer el tipo base del array
            elem_type1 = self.extract_array_element_type(str1)
            elem_type2 = self.extract_array_element_type(str2)

            # Los tipos base deben coincidir
            if elem_type1 == elem_type2:
                return True

        return str1 == str2

    def visit(self, node, env: Symtab):
        """Dispatcher principal usando el nombre de la clase"""
        if node is None:
            return None

        # Manejar literales de Python directamente (int, float, str, bool)
        if isinstance(node, int):
            return 'integer'
        elif isinstance(node, float):
            return 'float'
        elif isinstance(node, str):
            return 'string'
        elif isinstance(node, bool):
            return 'boolean'

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, None)

        if method:
            return method(node, env)
        else:
            print(f"[yellow]Advertencia: Nodo no manejado: {type(node).__name__}[/yellow]")
            return None

    # =====================================================================
    # Declaraciones
    # =====================================================================

    def visit_VarDecl(self, n, env: Symtab):
        """Declaración de variable sin inicialización"""
        type_obj = self.visit(n.type, env)

        if type_obj and 'void' in str(type_obj):
            self.error(f"Variable '{n.name}' no puede ser de tipo void")
            return None

        try:
            n.type_resolved = type_obj
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            self.error(f"La variable '{n.name}' ya fue declarada con un tipo diferente")
        except Symtab.SymbolDefinedError:
            self.error(f"La variable '{n.name}' ya fue declarada")

        # Verificar valor inicial si existe
        if n.value:
            value_type = self.visit(n.value, env)
            if value_type and type_obj and not self.types_match(type_obj, value_type):
                self.error(f"Tipo incompatible en inicialización de '{n.name}': "
                           f"esperado '{type_obj}', obtenido '{value_type}'")

        return type_obj

    def visit_VarDeclInit(self, n, env: Symtab):
        """Declaración de variable con inicialización"""
        var_type = self.visit(n.typ, env)

        if var_type and 'void' in str(var_type):
            self.error(f"Variable '{n.name}' no puede ser de tipo void")
            return None

        # Verificar la inicialización
        if isinstance(n.init, list):
            # Inicialización de array
            if not var_type or 'array' not in str(var_type):
                self.error(f"Lista de inicialización usada para no-array '{n.name}'")
            else:
                # Verificar cada elemento
                elem_type = self.extract_array_element_type(var_type)
                for i, expr in enumerate(n.init):
                    init_type = self.visit(expr, env)
                    if init_type and elem_type and not self.types_match(elem_type, init_type):
                        self.error(f"Elemento {i} en inicialización de '{n.name}': "
                                   f"esperado '{elem_type}', obtenido '{init_type}'")
        else:
            # Inicialización simple
            init_type = self.visit(n.init, env)
            if init_type and var_type and not self.types_match(var_type, init_type):
                self.error(f"Tipo incompatible en inicialización de '{n.name}': "
                           f"esperado '{var_type}', obtenido '{init_type}'")

        # Agregar a la tabla de símbolos
        try:
            n.type_resolved = var_type
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            self.error(f"La variable '{n.name}' ya fue declarada con un tipo diferente")
        except Symtab.SymbolDefinedError:
            self.error(f"La variable '{n.name}' ya fue declarada")

        return var_type

    def visit_FuncDecl(self, n, env: Symtab):
        """Declaración/definición de función"""
        # Si ya fue declarada en la primera pasada, usar ese tipo
        existing = env.get(n.name)
        if existing and hasattr(existing, 'type_resolved'):
            return existing.type_resolved

        # Si no, resolverlo ahora
        func_type = self.visit(n.type_func, env)
        n.type_resolved = func_type
        return func_type

    def visit_Param(self, n, env: Symtab):
        """Parámetro de función"""
        param_type = self.visit(n.typ, env)

        if param_type and 'void' in str(param_type):
            self.error(f"El parámetro '{n.name}' no puede ser de tipo void")

        try:
            n.type_resolved = param_type
            # Asegurar que el nombre esté disponible en el nodo
            if not hasattr(n, 'name'):
                n.name = getattr(n, 'name', 'unknown')
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            self.error(f"El parámetro '{n.name}' está duplicado")

        return param_type

    # =====================================================================
    # Tipos
    # =====================================================================

    def visit_SimpleType(self, n, env: Symtab):
        """Tipo simple"""
        if n.name not in typenames and n.name != 'void':
            self.error(f"Tipo desconocido: '{n.name}'")
            return None
        return n.name

    def visit_ArrayType(self, n, env: Symtab):
        """Tipo array"""
        if n.size is not None:
            # El tamaño puede ser una expresión o un identificador
            size_type = self.visit(n.size, env)

            # Verificar que el tipo sea entero (o que sea un identificador de tipo entero)
            if size_type and size_type != 'integer':
                self.error(f"El tamaño del array debe ser entero, no '{size_type}'")

        elem_type = self.visit(n.elem_type, env)

        # Crear representación del tipo array
        size_str = ""
        if n.size:
            # Si es un literal Integer
            if hasattr(n.size, 'value'):
                size_str = str(n.size.value)
            # Si es un identificador
            elif hasattr(n.size, 'name'):
                size_str = n.size.name
            # Si es un literal Python directo
            elif isinstance(n.size, int):
                size_str = str(n.size)
            # Cualquier otra expresión
            else:
                size_str = "expr"

        return f"array[{size_str}] {elem_type}"

    def visit_FuncType(self, n, env: Symtab):
        """Tipo función"""
        ret_type = self.visit(n.ret_type, env)

        param_types = []
        for p in n.params:
            ptype = self.visit(p.typ, env)
            param_types.append(ptype)

        # Crear representación del tipo función
        params_str = ','.join(str(p) for p in param_types)
        return f"function({params_str}) -> {ret_type}"

    # =====================================================================
    # Sentencias
    # =====================================================================

    def visit_IfStmt(self, n, env: Symtab):
        """Sentencia if"""
        if n.cond:
            cond_type = self.visit(n.cond, env)
            if cond_type and cond_type != 'boolean':
                self.error(f"La condición del if debe ser booleana, no '{cond_type}'")

        self.visit(n.then_branch, env)

        if n.else_branch:
            self.visit(n.else_branch, env)

    def visit_WhileStmt(self, n, env: Symtab):
        """Sentencia while"""
        cond_type = self.visit(n.cond, env)
        if cond_type and cond_type != 'boolean':
            self.error(f"La condición del while debe ser booleana, no '{cond_type}'")

        prev_loop = self.in_loop
        self.in_loop = True
        self.visit(n.body, env)
        self.in_loop = prev_loop

    def visit_DoWhileStmt(self, n, env: Symtab):
        """Sentencia do-while"""
        prev_loop = self.in_loop
        self.in_loop = True
        self.visit(n.body, env)
        self.in_loop = prev_loop

        cond_type = self.visit(n.cond, env)
        if cond_type and cond_type != 'boolean':
            self.error(f"La condición del do-while debe ser booleana, no '{cond_type}'")

    def visit_ForStmt(self, n, env: Symtab):
        """Sentencia for"""
        # Crear nuevo scope solo si hay inicialización con declaración
        should_create_scope = False
        if n.init and type(n.init).__name__ in ['VarDecl', 'VarDeclInit']:
            should_create_scope = True

        if should_create_scope:
            for_env = Symtab(f"for_{id(n)}", env)
            if n.init:
                self.visit(n.init, for_env)
        else:
            for_env = env
            if n.init:
                self.visit(n.init, for_env)

        if n.cond:
            cond_type = self.visit(n.cond, for_env)
            if cond_type and cond_type != 'boolean':
                self.error(f"La condición del for debe ser booleana, no '{cond_type}'")

        if n.step:
            self.visit(n.step, for_env)

        prev_loop = self.in_loop
        self.in_loop = True
        self.visit(n.body, for_env)
        self.in_loop = prev_loop

    def visit_ReturnStmt(self, n, env: Symtab):
        """Sentencia return"""
        if self.current_function is None:
            self.error("Return fuera de función")
            return

        # Obtener tipo de retorno esperado
        func_ret_type = self.current_function.type_func.ret_type
        expected_type = self.visit(func_ret_type, env)

        if n.expr:
            expr_type = self.visit(n.expr, env)
            if expr_type and expected_type:
                if not self.types_match(expected_type, expr_type):
                    self.error(f"Tipo de retorno incorrecto en '{self.current_function.name}': "
                               f"esperado '{expected_type}', obtenido '{expr_type}'")
        else:
            # Return vacío
            if expected_type != 'void':
                self.error(f"La función '{self.current_function.name}' debe retornar "
                           f"un valor de tipo '{expected_type}'")

    def visit_PrintStmt(self, n, env: Symtab):
        """Sentencia print"""
        if isinstance(n.expr, list):
            for expr in n.expr:
                expr_type = self.visit(expr, env)
                # Print acepta cualquier tipo básico
        elif n.expr:
            self.visit(n.expr, env)

    def visit_Block(self, n, env: Symtab):
        """Bloque de sentencias"""
        block_env = Symtab(f"block_{id(n)}", env)

        for stmt in n.body:
            self.visit(stmt, block_env)

    def visit_Program(self, n, env: Symtab):
        """Programa completo"""
        for decl in n.body:
            self.visit(decl, env)

    # =====================================================================
    # Expresiones
    # =====================================================================

    def visit_BinOper(self, n, env: Symtab):
        """Operador binario"""
        # Casos especiales: incremento/decremento postfijo
        if n.oper in ['++', '--']:
            left_type = self.visit(n.left, env)
            if left_type != 'integer':
                self.error(f"Operador '{n.oper}' requiere operando entero, no '{left_type}'")
            n.type = 'integer'
            return 'integer'

        # Operadores binarios normales
        left_type = self.visit(n.left, env)
        right_type = self.visit(n.right, env) if n.right else None

        if right_type is None:
            n.type = left_type
            return left_type

        # Verificar operación válida
        if left_type and right_type:
            result_type = check_binop(n.oper, left_type, right_type)

            if result_type is None:
                self.error(f"Operador '{n.oper}' no válido entre '{left_type}' y '{right_type}'")
                return None

            n.type = result_type
            return result_type

        return None

    def visit_UnaryOper(self, n, env: Symtab):
        """Operador unario"""
        expr_type = self.visit(n.expr, env)

        if expr_type:
            result_type = check_unaryop(n.oper, expr_type)

            if result_type is None:
                self.error(f"Operador unario '{n.oper}' no válido para tipo '{expr_type}'")
                return None

            n.type = result_type
            return result_type

        return None

    def visit_Assign(self, n, env: Symtab):
        """Asignación"""
        left_type = self.visit(n.left, env)
        right_type = self.visit(n.right, env)

        if left_type and right_type:
            if not self.types_match(left_type, right_type):
                self.error(f"Tipos incompatibles en asignación: '{left_type}' = '{right_type}'")

        return left_type

    def visit_Call(self, n, env: Symtab):
        """Llamada a función"""
        func_name = n.func.name if type(n.func).__name__ == 'Identifier' else str(n.func)
        func_decl = env.get(func_name)

        if func_decl is None:
            self.error(f"Función '{func_name}' no definida")
            return None

        if type(func_decl).__name__ != 'FuncDecl':
            self.error(f"'{func_name}' no es una función")
            return None

        # Verificar número de argumentos
        expected_params = func_decl.type_func.params
        if len(n.args) != len(expected_params):
            self.error(f"Función '{func_name}' espera {len(expected_params)} argumentos, "
                       f"se proporcionaron {len(n.args)}")
            return None

        # Verificar tipos de argumentos
        for i, (arg, param) in enumerate(zip(n.args, expected_params)):
            arg_type = self.visit(arg, env)
            param_type = self.visit(param.typ, env)

            if arg_type and param_type:
                if not self.types_match(arg_type, param_type):
                    self.error(f"Argumento {i + 1} de '{func_name}': "
                               f"esperado '{param_type}', obtenido '{arg_type}'")

        # Retornar el tipo de retorno de la función
        ret_type = func_decl.type_func.ret_type
        return self.visit(ret_type, env)

    def visit_ArrayAccess(self, n, env: Symtab):
        """Acceso a array"""
        array_type = self.visit(n.array, env)
        index_type = self.visit(n.index, env)

        if index_type and index_type != 'integer':
            self.error(f"El índice del array debe ser entero, no '{index_type}'")

        if array_type:
            elem_type = self.extract_array_element_type(array_type)
            return elem_type

        return None

    def visit_Identifier(self, n, env: Symtab):
        """Identificador"""
        var = env.get(n.name)

        if var is None:
            self.error(f"Variable '{n.name}' no definida")
            return None

        # Obtener el tipo de la variable
        if hasattr(var, 'type_resolved'):
            return var.type_resolved
        elif hasattr(var, 'typ') and hasattr(var.typ, 'name'):
            return var.typ.name
        elif hasattr(var, 'type'):
            return self.visit(var.type, env)

        return None

    # =====================================================================
    # Literales
    # =====================================================================

    def visit_Integer(self, n, env: Symtab):
        """Literal entero"""
        n.type = 'integer'
        return 'integer'

    def visit_Float(self, n, env: Symtab):
        """Literal flotante"""
        n.type = 'float'
        return 'float'

    def visit_Boolean(self, n, env: Symtab):
        """Literal booleano"""
        n.type = 'boolean'
        return 'boolean'

    def visit_Char(self, n, env: Symtab):
        """Literal carácter"""
        n.type = 'char'
        return 'char'

    def visit_String(self, n, env: Symtab):
        """Literal string"""
        n.type = 'string'
        return 'string'

    # =====================================================================
    # Métodos auxiliares
    # =====================================================================

    def extract_array_element_type(self, array_type):
        """Extrae el tipo de elemento de un tipo array"""
        if not array_type:
            return None

        type_str = str(array_type)
        if 'array' not in type_str:
            return None

        # Formato: "array[N] tipo" o "array[] tipo"
        # Buscar la última ocurrencia de ] para manejar arrays multidimensionales
        # Ejemplo: "array[5] array[3] integer" -> "array[3] integer"

        # Dividir por espacios y tomar todo después del primer "array[...]"
        parts = type_str.split(None, 1)  # Dividir en máximo 2 partes
        if len(parts) >= 2:
            # parts[0] = "array[N]" o "array[]"
            # parts[1] = resto del tipo
            return parts[1]

        return None


# =====================================================================
# Función principal para pruebas
# =====================================================================
def check_program(filename):
    """
    Realiza análisis semántico de un archivo B-Minor
    """
    from bminor_lexer import BMinorLexer
    from bminor_parser import BMinorParser

    lexer = BMinorLexer()
    parser = BMinorParser()

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()

        # Parsear
        ast = parser.parse(lexer.tokenize(text))

        if ast is None:
            print("[red]Error:[/red] No se pudo construir el AST")
            return None, []

        # Análisis semántico
        print("\n" + "=" * 60)
        print("Iniciando análisis semántico...")
        print("=" * 60 + "\n")

        symtab, errors = Check.check(ast)

        # Mostrar resultados
        if errors:
            print(f"\n[red]✗ Se encontraron {len(errors)} errores semánticos[/red]\n")
            return symtab, errors
        else:
            print("\n[green]✓ Análisis semántico exitoso![/green]\n")
            print("Tabla de símbolos:")
            symtab.print()
            return symtab, []

    except FileNotFoundError:
        print(f"[red]Error:[/red] No se encontró el archivo '{filename}'")
        return None, []
    except Exception as e:
        print(f"[red]Error inesperado:[/red] {e}")
        import traceback
        traceback.print_exc()
        return None, []


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Uso: python checker.py archivo.bminor")
        sys.exit(1)

    symtab, errors = check_program(sys.argv[1])

    if errors:
        sys.exit(1)
    else:
        sys.exit(0)