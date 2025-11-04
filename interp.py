'''
Tree-walking interpreter
Intérprete para B-Minor usando AST-Walking
'''

from collections import ChainMap
from rich import print
import sys

try:
    from bminor_ast import *
except ImportError:
    from model import *

from checker import Check
from bminor_builtins import builtins, consts, CallError


# =====================================================================
# Excepciones para control de flujo
# =====================================================================

class ReturnException(Exception):
    """Excepción para manejar returns en funciones"""
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Excepción para manejar break en loops"""
    pass


class ContinueException(Exception):
    """Excepción para manejar continue en loops"""
    pass


class BminorExit(BaseException):
    """Excepción para salir del programa"""
    pass


# =====================================================================
# Función auxiliar para veracidad en B-Minor
# =====================================================================

def _is_truthy(value):
    """Determina si un valor es verdadero en B-Minor"""
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True


# =====================================================================
# Clase Function - Wrapper para funciones definidas por usuario
# =====================================================================

class Function:
    """
    Envuelve una declaración de función (FuncDecl) para hacerla callable
    Mantiene su propio environment de captura (closures)
    """
    
    def __init__(self, node, env):
        self.node = node  # FuncDecl node
        self.env = env    # Environment donde fue definida
    
    @property
    def arity(self) -> int:
        """Retorna el número de parámetros de la función"""
        if self.node.type_func and self.node.type_func.params:
            return len(self.node.type_func.params)
        return 0
    
    def __call__(self, interp, *args):
        """
        Ejecuta la función con los argumentos dados
        """
        # Crear nuevo environment hijo del environment de definición
        newenv = self.env.new_child()
        
        # Bindear parámetros a argumentos
        if self.node.type_func and self.node.type_func.params:
            for param, arg in zip(self.node.type_func.params, args):
                newenv[param.name] = arg
        
        # Guardar environment actual y cambiar al nuevo
        oldenv = interp.env
        interp.env = newenv
        
        try:
            # Ejecutar el cuerpo de la función
            result = None
            if self.node.body:
                for stmt in self.node.body:
                    result = interp.visit(stmt)
        except ReturnException as e:
            result = e.value
        finally:
            # Restaurar environment anterior
            interp.env = oldenv
        
        return result


# =====================================================================
# Intérprete Principal
# =====================================================================

class Interpreter(Visitor):
    """
    Intérprete AST-Walking para B-Minor
    """
    
    def __init__(self):
        # Environment para ejecución (ChainMap para scopes anidados)
        self.env = ChainMap({})
        # Environment para el checker (separado)
        self.check_env = ChainMap({})
        # Mapa local (para optimizaciones futuras)
        self.localmap = {}
        # Errores encontrados
        self.errors = []
    
    def error(self, position, message):
        """Registra un error de ejecución"""
        error_msg = f"Error en {position}: {message}"
        self.errors.append(error_msg)
        print(f"[red]{error_msg}[/red]")
        raise BminorExit()
    
    # =====================================================================
    # Punto de entrada principal
    # =====================================================================
    
    def interpret(self, node):
        """
        Punto de entrada de alto nivel para interpretar un programa
        primero checker, luego ejecución
        """
        # 1. Cargar constantes built-in
        for name, cval in consts.items():
            self.check_env[name] = cval
            self.env[name] = cval
        
        # 2. Cargar funciones built-in
        for name, func in builtins.items():
            self.check_env[name] = func
            self.env[name] = func
        
        try:
            # 3. Ejecutar análisis semántico (Checker)
            print("[cyan]Ejecutando análisis semántico...[/cyan]")
            symtab, check_errors = Check.check(node)
            
            if check_errors:
                print(f"[red]Se encontraron {len(check_errors)} errores semánticos[/red]")
                for err in check_errors:
                    print(f"  • {err}")
                return None
            
            print("[green]✓[/green] Análisis semántico exitoso\n")
            
            # 4. Ejecutar el programa
            print("[cyan]Ejecutando programa...[/cyan]")
            print("=" * 60)
            result = self.visit(node)
            print("\n" + "=" * 60)
            print(f"[green]✓[/green] Ejecución completada")
            
            return result
            
        except BminorExit:
            return None
        except Exception as e:
            print(f"[red]Error de ejecución:[/red] {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # =====================================================================
    # Dispatcher principal
    # =====================================================================
    
    def visit(self, node):
        """Dispatcher principal usando visitor pattern"""
        if node is None:
            return None
        
        # Manejar literales Python directos
        if isinstance(node, int):
            return node
        elif isinstance(node, float):
            return node
        elif isinstance(node, str):
            return node
        elif isinstance(node, bool):
            return node
        
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Handler por defecto para nodos no implementados"""
        raise Exception(f"No hay visit_{type(node).__name__} implementado")
    
    # =====================================================================
    # Programa y Declaraciones
    # =====================================================================
    
    def visit_Program(self, node):
        """Ejecuta el programa completo"""
        # Primera pasada: declarar funciones y variables globales
        for stmt in node.body:
            if type(stmt).__name__ == 'FuncDecl':
                # Crear Function wrapper y guardarla
                func = Function(stmt, self.env)
                self.env[stmt.name] = func
            elif type(stmt).__name__ in ['VarDecl', 'VarDeclInit']:
                self.visit(stmt)
        
        # Buscar función main y ejecutarla si existe
        if 'main' in self.env:
            main_func = self.env['main']
            if callable(main_func):
                return main_func(self, )  # Llamar sin argumentos
        
        return None
    
    def visit_VarDecl(self, node):
        """Declaración de variable sin inicialización"""
        value = None
        
        # Si tiene valor inicial explícito, usarlo
        if node.value:
            value = self.visit(node.value)
        # Si es un array, inicializarlo con valores por defecto
        elif type(node.type).__name__ == 'ArrayType':
            try:
                size = self.get_array_size(node.type)
                default_value = self.get_default_value(node.type.elem_type)
                value = [default_value for _ in range(size)]
            except Exception as e:
                raise Exception(f"Error al inicializar array '{node.name}': {e}")
        
        self.env[node.name] = value
        return value
    
    def visit_VarDeclInit(self, node):
        """Declaración de variable con inicialización"""
        if isinstance(node.init, list):
            # Inicialización de array
            value = [self.visit(expr) for expr in node.init]
        else:
            value = self.visit(node.init)
        
        self.env[node.name] = value
        return value
    
    def visit_FuncDecl(self, node):
        """Declaración de función (ya procesada en primera pasada)"""
        return None
    
    # =====================================================================
    # Sentencias de Control
    # =====================================================================
    
    def visit_IfStmt(self, node):
        """Sentencia if"""
        cond = self.visit(node.cond) if node.cond else True
        
        if _is_truthy(cond):
            return self.visit(node.then_branch)
        elif node.else_branch:
            return self.visit(node.else_branch)
        
        return None
    
    def visit_WhileStmt(self, node):
        """Sentencia while"""
        result = None
        try:
            while _is_truthy(self.visit(node.cond)):
                try:
                    result = self.visit(node.body)
                except ContinueException:
                    continue
                except ReturnException:
                    raise
        except BreakException:
            pass
        
        return result
    
    def visit_DoWhileStmt(self, node):
        """Sentencia do-while"""
        result = None
        try:
            while True:
                try:
                    result = self.visit(node.body)
                except ContinueException:
                    pass
                
                if not _is_truthy(self.visit(node.cond)):
                    break
        except BreakException:
            pass
        
        return result
    
    def visit_ForStmt(self, node):
        """Sentencia for con scope correcto para declaraciones"""
        # Crear scope para la inicialización del for
        self.env = self.env.new_child()
        
        result = None
        try:
            # Inicialización (en el scope del for)
            if node.init:
                self.visit(node.init)
            
            # Loop
            while True:
                # Condición
                if node.cond:
                    if not _is_truthy(self.visit(node.cond)):
                        break
                
                # Cuerpo - crear nuevo scope para CADA iteración
                # Esto permite que cada iteración tenga sus propias variables
                self.env = self.env.new_child()
                try:
                    result = self.visit(node.body)
                except ContinueException:
                    pass
                except ReturnException:
                    raise
                finally:
                    # Restaurar scope después de cada iteración
                    self.env = self.env.parents
                
                # Incremento (en el scope del for, no del body)
                if node.step:
                    self.visit(node.step)
        
        except BreakException:
            pass
        finally:
            # Restaurar scope del for
            self.env = self.env.parents
        
        return result
    
    def visit_ReturnStmt(self, node):
        """Sentencia return"""
        value = self.visit(node.expr) if node.expr else None
        raise ReturnException(value)
    
    def visit_PrintStmt(self, node):
        """Sentencia print - compatible con tu implementación actual"""
        if isinstance(node.expr, list):
            if len(node.expr) == 0:
                print()
            elif len(node.expr) == 1:
                value = self.visit(node.expr[0])
                if value == '\n':
                    print()
                else:
                    print(value, end='')
            else:
                values = [self.visit(expr) for expr in node.expr]
                for val in values:
                    print(val, end=' ')
                print()
        elif node.expr:
            value = self.visit(node.expr)
            if value == '\n':
                print()
            else:
                print(value, end='')
        else:
            print()
        
        return None
    
    def visit_Block(self, node):
        """Bloque de sentencias"""
        # Crear nuevo scope
        self.env = self.env.new_child()
        
        result = None
        try:
            for stmt in node.body:
                result = self.visit(stmt)
        except ReturnException:
            raise
        finally:
            # Restaurar scope anterior
            self.env = self.env.parents
        
        return result
    
    # =====================================================================
    # Expresiones
    # =====================================================================
    
    def visit_BinOper(self, node):
        """Operador binario"""
        # Casos especiales: incremento/decremento postfijo
        if node.oper in ['++', '--']:
            var_name = node.left.name if hasattr(node.left, 'name') else None
            if not var_name:
                raise Exception(f"Operador {node.oper} requiere una variable")
            
            old_value = self.get_variable(var_name)
            new_value = old_value + 1 if node.oper == '++' else old_value - 1
            self.set_variable(var_name, new_value)
            return old_value
        
        # Operadores binarios normales
        left = self.visit(node.left)
        right = self.visit(node.right) if node.right else None
        
        op = node.oper
        
        # Operadores aritméticos
        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise Exception("División por cero")
            return left / right if isinstance(left, float) or isinstance(right, float) else left // right
        if op == '%':
            return left % right
        if op == '^':
            return left ** right
        
        # Operadores de comparación
        if op == '<':
            return left < right
        if op == '<=':
            return left <= right
        if op == '>':
            return left > right
        if op == '>=':
            return left >= right
        if op == '==':
            return left == right
        if op == '!=':
            return left != right
        
        # Operadores lógicos
        if op == '&&':
            return left and right
        if op == '||':
            return left or right
        
        raise Exception(f"Operador binario no soportado: {node.oper}")
    
    def visit_UnaryOper(self, node):
        """Operador unario"""
        val = self.visit(node.expr)
        
        if node.oper == '+':
            return +val
        elif node.oper == '-':
            return -val
        elif node.oper == '!':
            return not val
        else:
            raise Exception(f"Operador unario no soportado: {node.oper}")
    
    def visit_Assign(self, node):
        """Asignación"""
        value = self.visit(node.right)
        
        # Asignación a variable simple
        if type(node.left).__name__ == 'Identifier':
            self.set_variable(node.left.name, value)
        
        # Asignación a array
        elif type(node.left).__name__ == 'ArrayAccess':
            array_name = node.left.array.name
            index = self.visit(node.left.index)
            array = self.get_variable(array_name)
            
            if not isinstance(array, list):
                raise Exception(f"'{array_name}' no es un array")
            
            if index < 0 or index >= len(array):
                raise Exception(f"Índice {index} fuera de rango para array '{array_name}'")
            
            array[index] = value
        
        else:
            raise Exception(f"Asignación no válida a {type(node.left).__name__}")
        
        return value
    
    def visit_Call(self, node):
        """Llamada a función"""
        func_name = node.func.name if type(node.func).__name__ == 'Identifier' else None
        
        if not func_name:
            raise Exception("Llamada a función inválida")
        
        # Buscar función
        callee = self.get_variable(func_name)
        
        if callee is None:
            raise Exception(f"Función '{func_name}' no definida")
        
        if not callable(callee):
            raise Exception(f"'{func_name}' no es una función")
        
        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.args]
        
        # Verificar aridad (si no es -1 = variable)
        if hasattr(callee, 'arity') and callee.arity != -1:
            if len(args) != callee.arity:
                raise Exception(f"Función '{func_name}' espera {callee.arity} argumentos, "
                              f"se proporcionaron {len(args)}")
        
        # Llamar función
        try:
            return callee(self, *args)
        except CallError as err:
            raise Exception(f"Error en llamada a '{func_name}': {err}")
    
    def visit_ArrayAccess(self, node):
        """Acceso a array"""
        array_name = node.array.name if hasattr(node.array, 'name') else None
        
        if not array_name:
            raise Exception("Acceso a array inválido")
        
        array = self.get_variable(array_name)
        index = self.visit(node.index)
        
        if not isinstance(array, list):
            raise Exception(f"'{array_name}' no es un array")
        
        if index < 0 or index >= len(array):
            raise Exception(f"Índice {index} fuera de rango para array '{array_name}' (tamaño: {len(array)})")
        
        return array[index]
    
    def visit_Identifier(self, node):
        """Identificador"""
        return self.get_variable(node.name)
    
    # =====================================================================
    # Literales
    # =====================================================================
    
    def visit_Integer(self, node):
        return node.value
    
    def visit_Float(self, node):
        return node.value
    
    def visit_Boolean(self, node):
        return node.value
    
    def visit_Char(self, node):
        value = node.value
        # Manejar secuencias de escape
        if value == '\\n' or value == '\n':
            return '\n'
        elif value == '\\t' or value == '\t':
            return '\t'
        elif value == '\\r' or value == '\r':
            return '\r'
        elif value == '\\0' or value == '\0':
            return '\0'
        else:
            return value
    
    def visit_String(self, node):
        return node.value
    
    # =====================================================================
    # Nodos de Tipos (no ejecutables)
    # =====================================================================
    
    def visit_SimpleType(self, node):
        return None
    
    def visit_ArrayType(self, node):
        return None
    
    def visit_FuncType(self, node):
        return None
    
    def visit_Param(self, node):
        return None
    
    # =====================================================================
    # Métodos Auxiliares
    # =====================================================================
    
    def get_variable(self, name):
        """Obtiene el valor de una variable del entorno"""
        for scope in self.env.maps:
            if name in scope:
                return scope[name]
        raise Exception(f"Variable '{name}' no definida")
    
    def set_variable(self, name, value):
        """Asigna valor a una variable - respeta scope léxico"""
        # Primero buscar en scope actual
        if name in self.env.maps[0]:
            self.env.maps[0][name] = value
            return
        
        # Luego buscar en scopes padres
        for scope in self.env.maps[1:]:
            if name in scope:
                scope[name] = value
                return
        
        # Si no existe, crear en scope actual
        self.env[name] = value
    
    def get_array_size(self, array_type):
        """Obtiene el tamaño de un array"""
        if not array_type.size:
            raise Exception("Array sin tamaño especificado")
        
        size_node = array_type.size
        size_type = type(size_node).__name__
        
        if size_type == 'Integer':
            return size_node.value
        if size_type == 'Identifier':
            return self.get_variable(size_node.name)
        if isinstance(size_node, int):
            return size_node
        if hasattr(size_node, 'oper'):
            return self.visit(size_node)
        
        try:
            return self.visit(size_node)
        except Exception as e:
            raise Exception(f"No se pudo determinar el tamaño del array: {e}")
    
    def get_default_value(self, type_node):
        """Obtiene el valor por defecto para un tipo"""
        if type(type_node).__name__ == 'SimpleType':
            if type_node.name == 'integer':
                return 0
            elif type_node.name == 'float':
                return 0.0
            elif type_node.name == 'boolean':
                return False
            elif type_node.name == 'char':
                return '\0'
            elif type_node.name == 'string':
                return ""
        elif type(type_node).__name__ == 'ArrayType':
            size = self.get_array_size(type_node)
            default = self.get_default_value(type_node.elem_type)
            return [default for _ in range(size)]
        
        return None


# =====================================================================
# Función Principal
# =====================================================================

def interpret_file(filename):
    """Interpreta un archivo B-Minor siguiendo el estilo del profesor"""
    from bminor_lexer import BMinorLexer
    from bminor_parser import BMinorParser
    
    lexer = BMinorLexer()
    parser = BMinorParser()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Parsear
        print("[cyan]Parseando...[/cyan]")
        ast = parser.parse(lexer.tokenize(text))
        
        if ast is None:
            print("[red]Error:[/red] No se pudo construir el AST")
            return None
        
        print("[green]✓[/green] Parsing exitoso\n")
        
        # Interpretar (incluye checker automáticamente)
        interp = Interpreter()
        result = interp.interpret(ast)
        
        if result is not None:
            print(f"[cyan]Valor de retorno:[/cyan] {result}")
        
        return result
    
    except FileNotFoundError:
        print(f"[red]Error:[/red] No se encontró el archivo '{filename}'")
        return None
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python interp.py archivo.bminor")
        sys.exit(1)
    
    result = interpret_file(sys.argv[1])
    sys.exit(0 if result is not None else 1)