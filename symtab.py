# symtab.py
from rich.table import Table
from rich.console import Console
from rich import print

from model import Node


class Symtab:
    '''
    Una tabla de símbolos.  Este es un objeto simple que sólo
    mantiene una hashtable (dict) de nombres de simbolos y los
    nodos de declaracion o definición de funciones a los que se
    refieren.
    Hay una tabla de simbolos separada para cada elemento de
    código que tiene su propio contexto (por ejemplo cada función,
    tendrá su propia tabla de simbolos). Como resultado,
    las tablas de simbolos se pueden anidar si los elementos de
    código están anidados y las búsquedas de las tablas de
    simbolos se repetirán hacia arriba a través de los padres
    para representar las reglas de alcance léxico.
    '''

    class SymbolDefinedError(Exception):
        '''
        Se genera una excepción cuando el código intenta agregar
        un simbol a una tabla donde el simbol ya se ha definido.
        Tenga en cuenta que 'definido' se usa aquí en el sentido
        del lenguaje C, es decir, 'se ha asignado espacio para el
        simbol', en lugar de una declaración.
        '''
        pass

    class SymbolConflictError(Exception):
        '''
        Se produce una excepción cuando el código intenta agregar
        un símbolo a una tabla donde el símbolo ya existe y su tipo
        difiere del existente previamente.
        '''
        pass

    def __init__(self, name, parent=None):
        '''
        Crea una tabla de símbolos vacía con la tabla de
        simbolos padre dada.
        '''
        self.name = name
        self.entries = {}
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = []

    def __getitem__(self, name):
        return self.entries[name]

    def __setitem__(self, name, value):
        self.entries[name] = value

    def __delitem__(self, name):
        del self.entries[name]

    def __contains__(self, name):
        if name in self.entries:
            return self.entries[name]
        return False

    def add(self, name, value):
        '''
        Agrega un simbol con el valor dado a la tabla de simbolos.
        El valor suele ser un nodo AST que representa la declaración
        o definición de una función, variable (por ejemplo, Declaración
        o FuncDeclaration)
        '''
        if name in self.entries:
            # Verificar si tienen el mismo tipo
            existing_type = getattr(self.entries[name], 'type_resolved', None) or \
                            getattr(self.entries[name], 'type', None)
            new_type = getattr(value, 'type_resolved', None) or \
                       getattr(value, 'type', None)

            if existing_type != new_type:
                raise Symtab.SymbolConflictError()
            else:
                raise Symtab.SymbolDefinedError()
        self.entries[name] = value

    def get(self, name):
        '''
        Recupera el símbolo con el nombre dado de la tabla de
        simbol, recorriendo hacia arriba a través de las tablas
        de simbol principales si no se encuentra en la actual.
        '''
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        return None

    def print(self, indent=0):
        '''
        Imprime la tabla de símbolos con formato mejorado
        '''
        # Solo crear tabla si hay entradas (no mostrar scopes vacíos)
        if self.entries:
            table = Table(title=f"Symbol Table: '{self.name}'",
                          show_header=True,
                          header_style="bold magenta")
            table.add_column('Nombre', style='cyan', width=15)
            table.add_column('Tipo', style='yellow', width=20)
            table.add_column('Categoría', style='green', width=15)
            table.add_column('Info', style='bright_black', width=30)

            for k, v in self.entries.items():
                node_type = type(v).__name__

                # Obtener tipo resuelto
                resolved_type = "N/A"
                if hasattr(v, 'type_resolved'):
                    resolved_type = str(v.type_resolved)
                elif hasattr(v, 'typ') and hasattr(v.typ, 'name'):
                    resolved_type = v.typ.name
                elif hasattr(v, 'type'):
                    if hasattr(v.type, 'name'):
                        resolved_type = v.type.name
                    else:
                        resolved_type = str(v.type)

                # Información adicional
                info = ""
                if node_type == 'FuncDecl':
                    if hasattr(v, 'type_func') and v.type_func:
                        num_params = len(v.type_func.params) if v.type_func.params else 0
                        has_body = "✓" if (v.body and len(v.body) > 0) else "✗"
                        info = f"{num_params} params, body:{has_body}"
                elif node_type == 'VarDecl':
                    has_init = "✓" if v.value else "✗"
                    info = f"init:{has_init}"
                elif node_type == 'VarDeclInit':
                    is_array = "✓" if isinstance(getattr(v, 'init', None), list) else "✗"
                    info = f"array:{is_array}"
                elif node_type == 'Param':
                    info = "parámetro de función"

                # Limitar longitud del tipo para mejor visualización
                if len(resolved_type) > 20:
                    resolved_type = resolved_type[:17] + "..."

                table.add_row(k, resolved_type, node_type, info)

            # Imprimir con indentación
            if indent > 0:
                print("  " * indent, end="")
            print(table, '\n')

        # Imprimir tablas hijas con indentación
        for child in self.children:
            child.print(indent + 1)