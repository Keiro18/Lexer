# lexer_error.py
# Manejo centralizado de errores léxicos

def lexer_error(lineno, value, message=None):
    """
    Muestra un error léxico estandarizado.
    """
    if message is None:
        message = f"Carácter no válido: {repr(value[0])}"
    print(f"[Error Léxico] Línea {lineno}: {message}")
