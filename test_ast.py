from model import Program, Decl, Type, Integer, ASTPrinter

# AST manual
ast = Program(body=[
    Decl(name="x", type=Type("int"), value=Integer(5))
])

print("=== AST en texto ===")
print(ast.pretty())

print("\n=== Grafo AST ===")
dot = ASTPrinter.render(ast)
dot.render("ast_output", format="png", cleanup=True)
print("Imagen generada: ast_output.png")
