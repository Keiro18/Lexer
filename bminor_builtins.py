# builtins.py
"""
Funciones y constantes built-in para B-Minor
"""
import sys


class CallError(Exception):
    """Excepción para errores en llamadas a funciones"""
    pass


class BuiltinFunction:
    """Clase base para funciones built-in"""
    
    def __init__(self, name, arity=-1):
        self.name = name
        self.arity = arity  # -1 = número variable de argumentos
    
    def __call__(self, interp, *args):
        raise NotImplementedError


class PrintFunction(BuiltinFunction):
    """Función print() built-in"""
    
    def __init__(self):
        super().__init__('print', -1)
    
    def __call__(self, interp, *args):
        """Imprime argumentos sin newline automático"""
        for arg in args:
            value = arg
            # Manejar secuencias de escape en strings
            if isinstance(value, str):
                value = value.replace('\\n', '\n')
                value = value.replace('\\t', '\t')
                value = value.replace('\\r', '\r')
            print(value, end='')
        return None


class InputFunction(BuiltinFunction):
    """Función input() built-in para leer entrada"""
    
    def __init__(self):
        super().__init__('input', 0)
    
    def __call__(self, interp, *args):
        """Lee una línea de entrada estándar"""
        if len(args) != 0:
            raise CallError(f"input() no acepta argumentos")
        return input()


class LenFunction(BuiltinFunction):
    """Función len() para obtener longitud de strings o arrays"""
    
    def __init__(self):
        super().__init__('len', 1)
    
    def __call__(self, interp, *args):
        if len(args) != 1:
            raise CallError(f"len() espera 1 argumento, recibió {len(args)}")
        
        obj = args[0]
        if isinstance(obj, (str, list)):
            return len(obj)
        else:
            raise CallError(f"len() no soporta tipo {type(obj).__name__}")


class StrFunction(BuiltinFunction):
    """Función str() para convertir a string"""
    
    def __init__(self):
        super().__init__('str', 1)
    
    def __call__(self, interp, *args):
        if len(args) != 1:
            raise CallError(f"str() espera 1 argumento, recibió {len(args)}")
        return str(args[0])


class IntFunction(BuiltinFunction):
    """Función int() para convertir a entero"""
    
    def __init__(self):
        super().__init__('int', 1)
    
    def __call__(self, interp, *args):
        if len(args) != 1:
            raise CallError(f"int() espera 1 argumento, recibió {len(args)}")
        
        try:
            return int(args[0])
        except (ValueError, TypeError) as e:
            raise CallError(f"No se puede convertir a int: {e}")


class FloatFunction(BuiltinFunction):
    """Función float() para convertir a flotante"""
    
    def __init__(self):
        super().__init__('float', 1)
    
    def __call__(self, interp, *args):
        if len(args) != 1:
            raise CallError(f"float() espera 1 argumento, recibió {len(args)}")
        
        try:
            return float(args[0])
        except (ValueError, TypeError) as e:
            raise CallError(f"No se puede convertir a float: {e}")


class ExitFunction(BuiltinFunction):
    """Función exit() para terminar el programa"""
    
    def __init__(self):
        super().__init__('exit', 1)
    
    def __call__(self, interp, *args):
        if len(args) == 0:
            sys.exit(0)
        elif len(args) == 1:
            code = args[0]
            if isinstance(code, int):
                sys.exit(code)
            else:
                sys.exit(1)
        else:
            raise CallError(f"exit() espera 0 o 1 argumentos, recibió {len(args)}")


# Diccionario de funciones built-in
builtins = {
    'print': PrintFunction(),
    'input': InputFunction(),
    'len': LenFunction(),
    'str': StrFunction(),
    'int': IntFunction(),
    'float': FloatFunction(),
    'exit': ExitFunction(),
}

# Constantes built-in
consts = {
    'true': True,
    'false': False,
    'nil': None,
}