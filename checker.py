# checker.py
'''
Analizador Semántico para B-Minor 2025
Este archivo implementa la verificación de tipos y análisis semántico
del lenguaje B-Minor.
'''
from rich import print
from typing import Union, List
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
        
        # Visitar todas las declaraciones
        for decl in program.body:
            checker.visit(decl, env)
        
        return env, checker.errors
    
    def visit(self, node, env: Symtab):
        """Dispatcher principal - orden importa para subclases"""
        
        # Primero verificar tipos más específicos
        if node is None:
            return None
            
        # Declaraciones con inicialización (antes de VarDecl)
        if type(node).__name__ == 'VarDeclInit':
            return self.visit_VarDeclInit(node, env)
        
        # Declaraciones
        if type(node).__name__ == 'VarDecl':
            return self.visit_VarDecl(node, env)
        elif type(node).__name__ == 'FuncDecl':
            return self.visit_FuncDecl(node, env)
        elif type(node).__name__ == 'Param':
            return self.visit_Param(node, env)
        
        # Tipos
        elif type(node).__name__ == 'SimpleType':
            return self.visit_SimpleType(node, env)
        elif type(node).__name__ == 'ArrayType':
            return self.visit_ArrayType(node, env)
        elif type(node).__name__ == 'FuncType':
            return self.visit_FuncType(node, env)
        
        # Sentencias
        elif type(node).__name__ == 'IfStmt':
            return self.visit_IfStmt(node, env)
        elif type(node).__name__ == 'WhileStmt':
            return self.visit_WhileStmt(node, env)
        elif type(node).__name__ == 'DoWhileStmt':
            return self.visit_DoWhileStmt(node, env)
        elif type(node).__name__ == 'ForStmt':
            return self.visit_ForStmt(node, env)
        elif type(node).__name__ == 'ReturnStmt':
            return self.visit_ReturnStmt(node, env)
        elif type(node).__name__ == 'PrintStmt':
            return self.visit_PrintStmt(node, env)
        elif type(node).__name__ == 'Block':
            return self.visit_Block(node, env)
        elif type(node).__name__ == 'Program':
            return self.visit_Program(node, env)
        
        # Expresiones
        elif type(node).__name__ == 'BinOper':
            return self.visit_BinOper(node, env)
        elif type(node).__name__ == 'UnaryOper':
            return self.visit_UnaryOper(node, env)
        elif type(node).__name__ == 'Assign':
            return self.visit_Assign(node, env)
        elif type(node).__name__ == 'Call':
            return self.visit_Call(node, env)
        elif type(node).__name__ == 'ArrayAccess':
            return self.visit_ArrayAccess(node, env)
        elif type(node).__name__ == 'Identifier':
            return self.visit_Identifier(node, env)
        
        # Literales
        elif type(node).__name__ == 'Integer':
            return self.visit_Integer(node, env)
        elif type(node).__name__ == 'Float':
            return self.visit_Float(node, env)
        elif type(node).__name__ == 'Boolean':
            return self.visit_Boolean(node, env)
        elif type(node).__name__ == 'Char':
            return self.visit_Char(node, env)
        elif type(node).__name__ == 'String':
            return self.visit_String(node, env)
        
        else:
            print(f"[yellow]Advertencia: Nodo no manejado: {type(node).__name__}[/yellow]")
            return None
    
    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    def visit_VarDecl(self, n, env: Symtab):
        """Declaración de variable sin inicialización"""
        # Obtener el tipo
        type_obj = self.visit(n.type, env)
        
        # Agregar a la tabla de símbolos
        try:
            n.type_resolved = type_obj
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            self.error(f"La variable '{n.name}' ya fue declarada con un tipo diferente")
        except Symtab.SymbolDefinedError:
            self.error(f"La variable '{n.name}' ya fue declarada")
        
        return type_obj
    
    def visit_VarDeclInit(self, n, env: Symtab):
        """Declaración de variable con inicialización"""
        # Resolver el tipo de la variable
        var_type = self.visit(n.typ, env)
        
        # Verificar la inicialización
        if isinstance(n.init, list):
            # Inicialización de array
            for expr in n.init:
                self.visit(expr, env)
        else:
            # Inicialización simple
            init_type = self.visit(n.init, env)
            if var_type != init_type and init_type is not None:
                self.error(f"Tipo incompatible en inicialización de '{n.name}': esperado '{var_type}', obtenido '{init_type}'")
        
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
        # Resolver el tipo de función
        func_type = self.visit(n.type_func, env)
        
        # Agregar a la tabla de símbolos global
        try:
            n.type_resolved = func_type
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            self.error(f"La función '{n.name}' ya fue declarada con un tipo diferente")
        except Symtab.SymbolDefinedError:
            # En B-Minor se permiten declaraciones múltiples si son compatibles
            pass
        
        # Si tiene cuerpo, crear scope local y verificarlo
        if n.body is not None and len(n.body) > 0:
            prev_func = self.current_function
            self.current_function = n
            
            # Crear tabla de símbolos local
            local_env = Symtab(f"func_{n.name}", env)
            
            # Agregar parámetros al scope local
            for param in n.type_func.params:
                self.visit(param, local_env)
            
            # Verificar el cuerpo
            for stmt in n.body:
                self.visit(stmt, local_env)
            
            self.current_function = prev_func
        
        return func_type
    
    def visit_Param(self, n, env: Symtab):
        """Parámetro de función"""
        param_type = self.visit(n.typ, env)
        
        try:
            n.type_resolved = param_type
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            self.error(f"El parámetro '{n.name}' está duplicado")
        
        return param_type
    
    # =====================================================================
    # Tipos
    # =====================================================================
    
    def visit_SimpleType(self, n, env: Symtab):
        """Tipo simple (integer, float, boolean, char, string, void)"""
        if n.name not in typenames and n.name != 'void':
            self.error(f"Tipo desconocido: '{n.name}'")
            return None
        return n.name
    
    def visit_ArrayType(self, n, env: Symtab):
        """Tipo array"""
        # Verificar el tamaño si existe
        if n.size is not None:
            size_type = self.visit(n.size, env)
            if size_type != 'integer' and size_type is not None:
                self.error(f"El tamaño del array debe ser entero, no '{size_type}'")
        
        # Obtener el tipo del elemento
        elem_type = self.visit(n.elem_type, env)
        
        return f"array[{n.size if n.size else ''}] {elem_type}"
    
    def visit_FuncType(self, n, env: Symtab):
        """Tipo función"""
        ret_type = self.visit(n.ret_type, env)
        param_types = [self.visit(p.typ, env) for p in n.params]
        
        return f"function({','.join(str(p) for p in param_types)}) -> {ret_type}"
    
    # =====================================================================
    # Sentencias
    # =====================================================================
    
    def visit_IfStmt(self, n, env: Symtab):
        """Sentencia if"""
        if n.cond:
            cond_type = self.visit(n.cond, env)
            if cond_type != 'boolean' and cond_type is not None:
                self.error(f"La condición del if debe ser booleana, no '{cond_type}'")
        
        self.visit(n.then_branch, env)
        
        if n.else_branch:
            self.visit(n.else_branch, env)
    
    def visit_WhileStmt(self, n, env: Symtab):
        """Sentencia while"""
        cond_type = self.visit(n.cond, env)
        if cond_type != 'boolean' and cond_type is not None:
            self.error(f"La condición del while debe ser booleana, no '{cond_type}'")
        
        self.visit(n.body, env)
    
    def visit_DoWhileStmt(self, n, env: Symtab):
        """Sentencia do-while"""
        self.visit(n.body, env)
        
        cond_type = self.visit(n.cond, env)
        if cond_type != 'boolean' and cond_type is not None:
            self.error(f"La condición del do-while debe ser booleana, no '{cond_type}'")
    
    def visit_ForStmt(self, n, env: Symtab):
        """Sentencia for"""
        if n.init:
            self.visit(n.init, env)
        
        if n.cond:
            cond_type = self.visit(n.cond, env)
            if cond_type != 'boolean' and cond_type is not None:
                self.error(f"La condición del for debe ser booleana, no '{cond_type}'")
        
        if n.step:
            self.visit(n.step, env)
        
        self.visit(n.body, env)
    
    def visit_ReturnStmt(self, n, env: Symtab):
        """Sentencia return"""
        if self.current_function is None:
            self.error("Return fuera de función")
            return
        
        # Obtener tipo de retorno esperado
        func_ret_type = self.current_function.type_func.ret_type
        expected_type = self.visit(func_ret_type, env) if hasattr(func_ret_type, 'name') or type(func_ret_type).__name__ in ['SimpleType', 'ArrayType'] else func_ret_type
        
        if n.expr:
            expr_type = self.visit(n.expr, env)
            if expr_type != expected_type and expr_type is not None:
                self.error(f"Tipo de retorno incorrecto: esperado '{expected_type}', obtenido '{expr_type}'")
        else:
            if expected_type != 'void':
                self.error(f"La función debe retornar un valor de tipo '{expected_type}'")
    
    def visit_PrintStmt(self, n, env: Symtab):
        """Sentencia print"""
        if isinstance(n.expr, list):
            for expr in n.expr:
                self.visit(expr, env)
        elif n.expr:
            self.visit(n.expr, env)
    
    def visit_Block(self, n, env: Symtab):
        """Bloque de sentencias"""
        # Crear nuevo scope
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
        # Casos especiales de incremento/decremento postfijo
        if n.oper in ['++', '--']:
            left_type = self.visit(n.left, env)
            if left_type != 'integer':
                self.error(f"Operador '{n.oper}' requiere operando entero")
            n.type = 'integer'
            return 'integer'
        
        # Operadores binarios normales
        left_type = self.visit(n.left, env)
        right_type = self.visit(n.right, env) if n.right else None
        
        if right_type is None:
            # Operadores postfijos sin right
            n.type = left_type
            return left_type
        
        result_type = check_binop(n.oper, left_type, right_type)
        
        if result_type is None:
            self.error(f"Operador '{n.oper}' no válido entre '{left_type}' y '{right_type}'")
            return None
        
        n.type = result_type
        return result_type
    
    def visit_UnaryOper(self, n, env: Symtab):
        """Operador unario"""
        expr_type = self.visit(n.expr, env)
        
        result_type = check_unaryop(n.oper, expr_type)
        
        if result_type is None:
            self.error(f"Operador unario '{n.oper}' no válido para tipo '{expr_type}'")
            return None
        
        n.type = result_type
        return result_type
    
    def visit_Assign(self, n, env: Symtab):
        """Asignación"""
        left_type = self.visit(n.left, env)
        right_type = self.visit(n.right, env)
        
        if left_type != right_type and left_type is not None and right_type is not None:
            self.error(f"Tipos incompatibles en asignación: '{left_type}' = '{right_type}'")
        
        return left_type
    
    def visit_Call(self, n, env: Symtab):
        """Llamada a función"""
        # Buscar la función en la tabla de símbolos
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
            self.error(f"Función '{func_name}' espera {len(expected_params)} argumentos, se proporcionaron {len(n.args)}")
        
        # Verificar tipos de argumentos
        for i, (arg, param) in enumerate(zip(n.args, expected_params)):
            arg_type = self.visit(arg, env)
            param_type = self.visit(param.typ, env)
            
            if arg_type != param_type and arg_type is not None:
                self.error(f"Argumento {i+1} de '{func_name}': esperado '{param_type}', obtenido '{arg_type}'")
        
        # Retornar el tipo de retorno de la función
        ret_type = func_decl.type_func.ret_type
        return self.visit(ret_type, env)
    
    def visit_ArrayAccess(self, n, env: Symtab):
        """Acceso a array"""
        array_type = self.visit(n.array, env)
        index_type = self.visit(n.index, env)
        
        if index_type != 'integer' and index_type is not None:
            self.error(f"El índice del array debe ser entero, no '{index_type}'")
        
        # Extraer el tipo del elemento del array
        if array_type and 'array' in str(array_type):
            parts = str(array_type).split()
            if len(parts) >= 2:
                return parts[-1]
        
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
        elif hasattr(var, 'type'):
            if hasattr(var.type, 'name'):
                return var.type.name
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
        return 'char'
    
    def visit_String(self, n, env: Symtab):
        """Literal string"""
        return 'string'


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
            return None
        
        # Análisis semántico
        print("\n" + "="*60)
        print("Iniciando análisis semántico...")
        print("="*60 + "\n")
        
        symtab, errors = Check.check(ast)
        
        # Mostrar resultados
        if errors:
            print(f"\n[red]Se encontraron {len(errors)} errores semánticos[/red]\n")
            return None
        else:
            print("\n[green]✓ Análisis semántico exitoso![/green]\n")
            print("Tabla de símbolos:")
            symtab.print()
            return symtab
            
    except FileNotFoundError:
        print(f"[red]Error:[/red] No se encontró el archivo '{filename}'")
        return None
    except Exception as e:
        print(f"[red]Error inesperado:[/red] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python checker.py archivo.bminor")
        sys.exit(1)
    
    check_program(sys.argv[1])