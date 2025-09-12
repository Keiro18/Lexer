import unittest
from parser import parse, ast_to_dict

class TestParser(unittest.TestCase):

    def test_while_stmt(self):
        code = "while (x < 10) x = x + 1;"
        ast = parse(code)
        ast_dict = ast_to_dict(ast)
        # Validamos que el nodo raíz sea Program y que haya un WhileStmt
        self.assertEqual(ast_dict['decls'][0]['__class__'], 'WhileStmt')

    def test_do_while_stmt(self):
        code = "do { x = x + 1; } while (x < 10);"
        ast = parse(code)
        ast_dict = ast_to_dict(ast)
        self.assertEqual(ast_dict['decls'][0]['__class__'], 'DoWhileStmt')

    def test_pre_inc(self):
        code = "++x;"
        ast = parse(code)
        ast_dict = ast_to_dict(ast)
        self.assertEqual(ast_dict['decls'][0]['__class__'], 'PreInc')

    def test_pre_dec(self):
        code = "--y;"
        ast = parse(code)
        ast_dict = ast_to_dict(ast)
        self.assertEqual(ast_dict['decls'][0]['__class__'], 'PreDec')

    def test_nested(self):
        code = """
        while (x < 5) {
            ++x;
            do { y = y - 1; } while (y > 0);
        }
        """
        ast = parse(code)
        ast_dict = ast_to_dict(ast)
        self.assertEqual(ast_dict['decls'][0]['__class__'], 'WhileStmt')


if __name__ == "__main__":
    unittest.main()
