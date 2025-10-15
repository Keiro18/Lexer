# symtab.py
from rich.table   import Table
from rich.console import Console
from rich         import print

from model        import Node

class Symtab:
	'''
	Una tabla de símbolos.  Este es un objeto simple que sólo
	mantiene una hashtable (dict) de nombres de simbolos y los
	nodos de declaracion o definición de funciones a los que se
	refieren.
	Hay una tabla de simbolos separada para cada elemento de
	código que tiene su propio contexto (por ejemplo cada función,
	tendra su propia tabla de simbolos). Como resultado,
	las tablas de simbolos se pueden anidar si los elementos de
	código estan anidados y las búsquedas de las tablas de
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
		Crea una tabla de símbolos vacia con la tabla de
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
			if hasattr(self.entries[name], 'type') and hasattr(value, 'type'):
				if self.entries[name].type != value.type:
					raise Symtab.SymbolConflictError()
			raise Symtab.SymbolDefinedError()
		self.entries[name] = value
		
	def get(self, name):
		'''
		Recupera el símbolo con el nombre dado de la tabla de
		simbol, recorriendo hacia arriba a traves de las tablas
		de simbol principales si no se encuentra en la actual.
		'''
		if name in self.entries:
			return self.entries[name]
		elif self.parent:
			return self.parent.get(name)
		return None
		
	def print(self):
		table = Table(title = f"Symbol Table: '{self.name}'")
		table.add_column('key', style='cyan')
		table.add_column('value', style='bright_green')
		
		for k, v in self.entries.items():
			# Obtener el nombre de la clase y el nombre del símbolo
			class_name = type(v).__name__
			
			# Formatear según el tipo de nodo
			if hasattr(v, 'name'):
				value_str = f"{class_name}({v.name})"
			else:
				value_str = f"{class_name}()"
			
			table.add_row(k, value_str)
		
		print(table, '\n')
		
		# Imprimir tablas hijas (scopes anidados) pero omitir bloques vacíos
		for child in self.children:
			# Solo imprimir si tiene entradas o no es un bloque
			if child.entries or not child.name.startswith('block_'):
				child.print()