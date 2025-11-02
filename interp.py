"""
Intérprete para B-Minor usando AST-Walking
Ejecuta directamente el árbol de sintaxis abstracta
"""

from collections import ChainMap
from rich import print
import sys

try:
    from bminor_ast import *
except ImportError:
    from model import *


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


class Interpreter:
    def __init__(self):
        # Entorno global y scopes anidados usando ChainMap
        self.env = ChainMap({})
        # Stack de funciones para scope de funciones
        self.call_stack = []
        # Funciones built-in
        self._setup_builtins()

    def _setup_builtins(self):
        """Configura funciones built-in"""
        # Por ahora, print se maneja especialmente
        pass

    def visit(self, node):
        """Dispatcher principal"""
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
        raise Exception(f"No hay visit_{type(node).__name__} implementado")

    # =====================================================================
    # Programa y Declaraciones
    # =====================================================================

    def visit_Program(self, node):
        """Ejecuta el programa completo"""
        # Primera pasada: declarar variables globales y funciones
        for stmt in node.body:
            if type(stmt).__name__ == 'FuncDecl':
                self.env[stmt.name] = stmt
            elif type(stmt).__name__ in ['VarDecl', 'VarDeclInit']:
                self.visit(stmt)

        # Buscar función main y ejecutarla si existe
        if 'main' in self.env:
            main_func = self.env['main']
            return self.call_function(main_func, [])

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
        """Declaración de función (ya guardada en primera pasada)"""
        return None

    # =====================================================================
    # Sentencias de Control
    # =====================================================================

    def visit_IfStmt(self, node):
        """Sentencia if"""
        cond = self.visit(node.cond) if node.cond else True

        if cond:
            return self.visit(node.then_branch)
        elif node.else_branch:
            return self.visit(node.else_branch)

        return None

    def visit_WhileStmt(self, node):
        """Sentencia while"""
        result = None
        try:
            while self.visit(node.cond):
                try:
                    result = self.visit(node.body)
                except ContinueException:
                    continue
                except ReturnException:
                    # Propagar return hacia arriba
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

                if not self.visit(node.cond):
                    break
        except BreakException:
            pass

        return result

    def visit_ForStmt(self, node):
        """Sentencia for"""
        # Crear nuevo scope para el for
        self.env = self.env.new_child()

        result = None
        try:
            # Inicialización
            if node.init:
                self.visit(node.init)

            # Loop
            while True:
                # Condición
                if node.cond:
                    if not self.visit(node.cond):
                        break

                # Cuerpo
                try:
                    result = self.visit(node.body)
                except ContinueException:
                    pass

                # Incremento
                if node.step:
                    self.visit(node.step)

        except BreakException:
            pass
        finally:
            # Restaurar scope
            self.env = self.env.parents

        return result

    def visit_ReturnStmt(self, node):
        """Sentencia return"""
        value = self.visit(node.expr) if node.expr else None
        raise ReturnException(value)

    def visit_PrintStmt(self, node):
        """Sentencia print"""
        if isinstance(node.expr, list):
            # Múltiples expresiones
            values = [self.visit(expr) for expr in node.expr]
            for val in values:
                print(val, end=' ')
            print()
        elif node.expr:
            value = self.visit(node.expr)
            print(value, end='')  # Sin newline automático
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
            # Propagar el return hacia arriba
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

            # Obtener valor actual
            old_value = self.get_variable(var_name)

            # Calcular nuevo valor
            if node.oper == '++':
                new_value = old_value + 1
            else:  # '--'
                new_value = old_value - 1

            # Actualizar variable
            self.set_variable(var_name, new_value)

            # Retornar valor antiguo (postfijo)
            return old_value

        # Operadores binarios normales - evaluar operandos
        left = self.visit(node.left)
        right = self.visit(node.right) if node.right else None

        # Tabla de operadores para mayor velocidad
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
        func = self.get_variable(func_name)

        if func is None:
            raise Exception(f"Función '{func_name}' no definida")

        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.args]

        # Llamar función
        return self.call_function(func, args)

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
        """Literal entero"""
        return node.value

    def visit_Float(self, node):
        """Literal flotante"""
        return node.value

    def visit_Boolean(self, node):
        """Literal booleano"""
        return node.value

    def visit_Char(self, node):
        """Literal carácter"""
        return node.value

    def visit_String(self, node):
        """Literal string"""
        return node.value

    # =====================================================================
    # Nodos de Tipos (no ejecutables)
    # =====================================================================

    def visit_SimpleType(self, node):
        """Tipo simple (no ejecutable)"""
        return None

    def visit_ArrayType(self, node):
        """Tipo array (no ejecutable)"""
        return None

    def visit_FuncType(self, node):
        """Tipo función (no ejecutable)"""
        return None

    def visit_Param(self, node):
        """Parámetro (no ejecutable)"""
        return None

    # =====================================================================
    # Métodos Auxiliares
    # =====================================================================

    def get_variable(self, name):
        """Obtiene el valor de una variable del entorno"""
        # Buscar en todos los scopes
        for scope in self.env.maps:
            if name in scope:
                return scope[name]

        raise Exception(f"Variable '{name}' no definida")

    def set_variable(self, name, value):
        """Asigna valor a una variable - CORREGIDO"""
        # PRIMERO: Buscar en scope actual (primer map del ChainMap)
        if name in self.env.maps[0]:
            self.env.maps[0][name] = value
            return
        
        # SEGUNDO: Buscar en scopes padres (del más cercano al más lejano)
        for scope in self.env.maps[1:]:
            if name in scope:
                scope[name] = value
                return

        # TERCERO: Si no existe en ningún scope, crear en scope actual
        self.env[name] = value

    def call_function(self, func_node, args):
        """Llama a una función con argumentos"""
        if type(func_node).__name__ != 'FuncDecl':
            raise Exception(f"No es una función: {func_node}")

        # Verificar número de argumentos
        params = func_node.type_func.params if func_node.type_func else []

        if len(args) != len(params):
            raise Exception(
                f"Función '{func_node.name}' espera {len(params)} argumentos, "
                f"se proporcionaron {len(args)}"
            )

        # Crear nuevo scope para la función
        self.env = self.env.new_child()

        try:
            # Bindear parámetros a argumentos
            for param, arg in zip(params, args):
                self.env[param.name] = arg

            # Ejecutar cuerpo de la función
            result = None
            if func_node.body:
                for stmt in func_node.body:
                    result = self.visit(stmt)

            return result

        except ReturnException as e:
            return e.value

        finally:
            # Restaurar scope anterior
            self.env = self.env.parents

    def get_array_size(self, array_type):
        """Obtiene el tamaño de un array"""
        if not array_type.size:
            raise Exception("Array sin tamaño especificado")

        size_node = array_type.size
        size_type = type(size_node).__name__

        # Si el tamaño es un nodo Integer
        if size_type == 'Integer':
            return size_node.value

        # Si el tamaño es un Identifier (variable)
        if size_type == 'Identifier':
            return self.get_variable(size_node.name)

        # Si es un literal Python directo
        if isinstance(size_node, int):
            return size_node

        # Si es una expresión compleja (como N*N), evaluarla
        if hasattr(size_node, 'oper'):
            return self.visit(size_node)

        # Intentar evaluar como expresión
        try:
            return self.visit(size_node)
        except Exception as e:
            raise Exception(f"No se pudo determinar el tamaño del array: {size_node} (error: {e})")

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

        # Para arrays anidados
        elif type(type_node).__name__ == 'ArrayType':
            size = self.get_array_size(type_node)
            default = self.get_default_value(type_node.elem_type)
            return [default for _ in range(size)]

        return None


# =====================================================================
# Función Principal
# =====================================================================

def interpret_file(filename):
    """Interpreta un archivo B-Minor"""
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

        # Interpretar
        print("[cyan]Ejecutando programa...[/cyan]")
        print("=" * 60)

        interp = Interpreter()
        result = interp.visit(ast)

        print("\n" + "=" * 60)
        print(f"[green]✓[/green] Ejecución completada")

        if result is not None:
            print(f"[cyan]Valor de retorno:[/cyan] {result}")

        return result

    except FileNotFoundError:
        print(f"[red]Error:[/red] No se encontró el archivo '{filename}'")
        return None
    except Exception as e:
        print(f"[red]Error de ejecución:[/red] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python interp.py archivo.bminor")
        sys.exit(1)

    result = interpret_file(sys.argv[1])
    sys.exit(0 if result is not None else 1)