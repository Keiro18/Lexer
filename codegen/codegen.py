# ==========================================================
# codegen/codegen.py — Generador de IR para B-Minor
# Genera IR "LLVM-like" usando tus clases en ir/
# ==========================================================

from ir.module import Module
from ir.function import Function
from ir.builder import Builder
from ir.value import Constant
from ir.globvar import Global
from ir.instr import Branch, Jump

from bminor_ast import (
    Program,
    FuncDecl,
    VarDecl,
    VarDeclInit,
    Block,
    IfStmt,
    WhileStmt,
    ForStmt,
    ReturnStmt,
    PrintStmt,
    BinOper,
    UnaryOper,
    Integer,
    Float,
    Boolean,
    Identifier,
    Assign,
    ArrayAccess,
    Char,
    String,
    ArrayType,
    Call,
)


class IRGenerator:
    """
    Generador de IR para B-Minor.
    Recorre el AST y produce un módulo IR.
    """

    def __init__(self):
        self.module = Module()
        self.func = None
        self.builder = None

        # Tablas de variables locales
        self.locals = {}
        self.local_types = {}

        # Estado de control de flujo
        self.block_terminated = False

        # Contador para nombres únicos de bloques
        self.block_counter = 0

        # Registrar primitivas de impresión (externs)
        self.module.add_extern("print_int", "void", ["i32"])
        self.module.add_extern("print_float", "void", ["float"])
        self.module.add_extern("print_bool", "void", ["i1"])
        self.module.add_extern("print_char", "void", ["i8"])

    # ======================================================
    # Helpers básicos
    # ======================================================

    def _require_in_function(self, msg: str):
        if self.func is None or self.builder is None:
            raise Exception(msg)

    def _new_block(self, base_name: str):
        """
        Crea un bloque con nombre único basado en base_name,
        para evitar colisiones de labels (for.cond, if.then, etc.).
        """
        name = f"{base_name}.{self.block_counter}"
        self.block_counter += 1
        return self.func.new_block(name)

    def _position_at_end(self, block):
        """Mover builder al final de un bloque y resetear flag de terminador."""
        self.builder.position_at_end(block)
        # No sabemos aquí si el bloque ya tenía terminador en la estructura interna,
        # pero en nuestro diseño sólo se llama _position_at_end en bloques nuevos
        # o recién creados para seguir generando, así que lo dejamos en False.
        self.block_terminated = False

    def _terminate_block(self, term_instr):
        """Insertar un terminador (br/ret) y marcar bloque como cerrado."""
        self.builder.block.append(term_instr)
        self.block_terminated = True

    # ======================================================
    # Helpers de tipos / variables
    # ======================================================

    def _infer_array_elem_type(self, varname: str) -> str:
        """
        A partir de self.local_types o globales, deduce el tipo
        de elemento de un array.
        """
        t = None
        if varname in self.local_types:
            t = self.local_types[varname]
        else:
            g = self.module.get_global(varname)
            if g is not None:
                t = g.type

        if t is None:
            return "i32"

        s = t.strip()

        # "[N x T]"
        if s.startswith("[") and "x" in s:
            s = s[1:-1]       # quitar corchetes
            _, elem = s.split("x", 1)
            return elem.strip()

        # "T*"
        if s.endswith("*"):
            return s[:-1]

        return s

    def _lookup_scalar_ptr_and_type(self, name: str):
        """
        Devuelve (ptr, llvm_type) de una variable escalar (local o global).
        """
        # Local
        if name in self.locals:
            ptr = self.locals[name]
            llvm_type = self.local_types.get(name, "i32")
            return ptr, llvm_type

        # Global
        g = self.module.get_global(name)
        if g:
            from ir.value import GlobalRef
            ptr = GlobalRef(name, g.type)
            return ptr, g.type

        raise Exception(f"Variable '{name}' no encontrada")

    # ======================================================
    # Evaluador de constantes enteras (para tamaños de arrays)
    # ======================================================

    def _eval_const_int(self, expr):
        """
        Evalúa una expresión del AST en tiempo de compilación.
        """
        if isinstance(expr, Integer):
            return expr.value

        if isinstance(expr, Identifier):
            g = self.module.get_global(expr.name)
            if g and isinstance(g.init, Constant):
                return g.init.value
            raise Exception(
                f"Tamaño de arreglo requiere constante entera; '{expr.name}' no es constante"
            )

        if isinstance(expr, BinOper):
            left = self._eval_const_int(expr.left)
            right = self._eval_const_int(expr.right)
            if expr.oper == '+':
                return left + right
            if expr.oper == '-':
                return left - right
            if expr.oper == '*':
                return left * right
            if expr.oper == '/':
                return left // right
            raise Exception(f"Operador no soportado: {expr.oper}")

        raise Exception(f"Tamaño de arreglo estático inválido: {expr}")

    # ======================================================
    # generate()
    # ======================================================

    def generate(self, program: Program) -> Module:
        # 1) Globales
        for decl in program.globals:
            if isinstance(decl, VarDecl):
                self._gen_global_decl(decl)
            elif isinstance(decl, VarDeclInit):
                self._gen_global_init(decl)

        # 2) Funciones
        for f in program.functions:
            self._gen_function(f)

        return self.module

    # ======================================================
    # Globales
    # ======================================================

    def _gen_global_decl(self, node: VarDecl):
        if isinstance(node.type, ArrayType):
            elem = self._map_type(node.type.elem_type)
            size = self._eval_const_int(node.type.size)
            arr_type = f"[{size} x {elem}]"
            g = Global(node.name, arr_type, "zeroinitializer")
            self.module.add_global(g)
            return

        # Escalares
        typ = self._map_type(node.type)
        g = Global(node.name, typ, None)
        self.module.add_global(g)


    def _gen_global_init(self, node: VarDeclInit):
        if isinstance(node.typ, ArrayType):
            elem = self._map_type(node.typ.elem_type)
            size = self._eval_const_int(node.typ.size)
            arr_type = f"[{size} x {elem}]"

            # Inicialización dinámica de array global NO soportada → usar zeroinitializer
            g = Global(node.name, arr_type, "zeroinitializer")
            self.module.add_global(g)
            return

        # --- inicialización de escalar existente ---
        typ = self._map_type(node.typ)
        init = node.init
        ...


    # ======================================================
    # Funciones
    # ======================================================

    def _gen_function(self, node: FuncDecl):
        rettype = self._map_type(node.type_func.ret_type)
        param_types = [self._map_type(p.typ) for p in node.type_func.params]
        param_names = [p.name for p in node.type_func.params]

        func = Function(node.name, rettype, param_types, param_names)
        self.module.add_function(func)

        self.func = func
        self.builder = Builder(func)

        # Reiniciar estado por función
        self.block_terminated = False
        self.locals = {}
        self.local_types = {}
        self.block_counter = 0

        # Bloque de entrada con nombre "entry" (uno por función)
        entry = self.func.new_block("entry")
        self._position_at_end(entry)

        # Parámetros
        for param_ast, ir_param in zip(node.type_func.params, func.params):
            pname = param_ast.name
            llvm_type = ir_param.type
            ptr = self.builder.alloca(llvm_type)
            self.locals[pname] = ptr
            self.local_types[pname] = llvm_type
            self.builder.store(ir_param, ptr)

        # Cuerpo
        for stmt in node.body:
            self._gen_stmt(stmt)

        if rettype == "void" and not self.block_terminated:
            self.builder.ret(None)
            self.block_terminated = True

    # ======================================================
    # Sentencias
    # ======================================================

    def _gen_stmt(self, stmt):
        if self.block_terminated:
            return

        # NO USAR FROM dentro de funciones
        AstBinOper = BinOper

        if isinstance(stmt, VarDecl):
            return self._gen_var_decl(stmt)

        if isinstance(stmt, VarDeclInit):
            return self._gen_var_decl_init(stmt)

        if isinstance(stmt, ReturnStmt):
            return self._gen_return(stmt)

        if isinstance(stmt, PrintStmt):
            return self._gen_print(stmt)

        if isinstance(stmt, Block):
            for s in stmt.body:
                self._gen_stmt(s)
            return

        if isinstance(stmt, IfStmt):
            return self._gen_if(stmt)

        if isinstance(stmt, WhileStmt):
            return self._gen_while(stmt)

        if isinstance(stmt, ForStmt):
            return self._gen_for(stmt)

        if isinstance(stmt, Assign):
            return self._gen_assign(stmt)

        if isinstance(stmt, Call):
            self._gen_call(stmt)
            return

        if isinstance(stmt, AstBinOper) and stmt.oper in ("++", "--"):
            self._gen_incdec(stmt)
            return

        print(f"[Warning] Stmt no soportado: {type(stmt).__name__}")


    # ======================================================
    # Declaraciones locales
    # ======================================================

    def _gen_var_decl(self, node: VarDecl):
        typ = node.type

        if isinstance(typ, ArrayType):
            elem_type = self._map_type(typ.elem_type)
            size = self._eval_const_int(typ.size)
            arr_type = f"[{size} x {elem_type}]"
            ptr = self.builder.alloca(arr_type)
            self.locals[node.name] = ptr
            self.local_types[node.name] = arr_type
            return

        llvm_type = self._map_type(typ)
        ptr = self.builder.alloca(llvm_type)
        self.locals[node.name] = ptr
        self.local_types[node.name] = llvm_type

    def _gen_var_decl_init(self, node: VarDeclInit):
        typ_ast = node.typ

        # Inicialización de arrays
        if isinstance(typ_ast, ArrayType) and isinstance(node.init, list):
            elem_type = self._map_type(typ_ast.elem_type)
            size = self._eval_const_int(typ_ast.size)
            arr_type = f"[{size} x {elem_type}]"
            ptr = self.builder.alloca(arr_type)
            self.locals[node.name] = ptr
            self.local_types[node.name] = arr_type

            from ir.instr import GetElementPtr

            for idx, expr in enumerate(node.init):
                index_val = Constant(idx, "i32")
                elem_ptr = self.func.new_temp(f"{elem_type}*")
                gep = GetElementPtr(ptr, index_val, elem_ptr)
                self.builder.block.append(gep)

                val = self._gen_expr(expr)
                self.builder.store(val, elem_ptr)

            return

        # Inicialización escalar
        llvm_type = self._map_type(typ_ast)
        ptr = self.builder.alloca(llvm_type)
        self.locals[node.name] = ptr
        self.local_types[node.name] = llvm_type

        val = self._gen_expr(node.init)
        self.builder.store(val, ptr)

    # ======================================================
    # Asignación
    # ======================================================

    def _gen_assign(self, node: Assign):
        if isinstance(node.left, Identifier):
            name = node.left.name
            ptr, llvm_type = self._lookup_scalar_ptr_and_type(name)
            val = self._gen_expr(node.right)
            self.builder.store(val, ptr)
            return val

        if isinstance(node.left, ArrayAccess):
            return self._gen_assign_array(node)

        raise Exception("LHS de asignación no soportado")

    # ======================================================
    # Return
    # ======================================================

    def _gen_return(self, node: ReturnStmt):
        if node.expr:
            value = self._gen_expr(node.expr)
            self.builder.ret(value)
        else:
            self.builder.ret(None)

        self.block_terminated = True

    # ======================================================
    # IF
    # ======================================================

    def _gen_if(self, node: IfStmt):
        cond_val = self._gen_expr(node.cond)

        then_block = self._new_block("if.then")
        else_block = self._new_block("if.else") if node.else_branch else None
        end_block = self._new_block("if.end")

        if else_block:
            self._terminate_block(Branch(cond_val, then_block, else_block))
        else:
            self._terminate_block(Branch(cond_val, then_block, end_block))

        # THEN
        self._position_at_end(then_block)
        self._gen_stmt(node.then_branch)
        if not self.block_terminated:
            self._terminate_block(Jump(end_block))

        # ELSE
        if else_block:
            self._position_at_end(else_block)
            self._gen_stmt(node.else_branch)
            if not self.block_terminated:
                self._terminate_block(Jump(end_block))

        # END
        self._position_at_end(end_block)

    def _gen_if_returns(self, node: IfStmt):
        """
        Caso especial:
            if (cond) return ...;
            else return ...;

        Ambas ramas terminan la función, así que NO se crea bloque if.end.
        """
        cond_val = self._gen_expr(node.cond)

        then_block = self._new_block("if.then")
        else_block = self._new_block("if.else")

        # branch condicional a THEN / ELSE
        self._terminate_block(Branch(cond_val, then_block, else_block))

        # THEN: genera el return explícito
        self._position_at_end(then_block)
        self._gen_return(node.then_branch)   # esto hace ret y block_terminated = True

        # ELSE: genera el return explícito
        self._position_at_end(else_block)
        self._gen_return(node.else_branch)   # ret y block_terminated = True

        # Después de esto, el bloque actual de la función queda "terminado",
        # y _gen_stmt ignorará cualquier sentencia posterior.


    # ======================================================
    # WHILE
    # ======================================================

    def _gen_while(self, node: WhileStmt):
        cond_block = self._new_block("while.cond")
        body_block = self._new_block("while.body")
        end_block = self._new_block("while.end")

        # salto inicial a cond
        self._terminate_block(Jump(cond_block))

        # COND
        self._position_at_end(cond_block)
        cond_val = self._gen_expr(node.cond)
        if cond_val.type != "i1":
            raise Exception("La condición del while debe ser booleana (i1)")

        self._terminate_block(Branch(cond_val, body_block, end_block))

        # BODY
        self._position_at_end(body_block)
        self._gen_stmt(node.body)
        if not self.block_terminated:
            self._terminate_block(Jump(cond_block))

        # END
        self._position_at_end(end_block)

    # ======================================================
    # FOR
    # ======================================================

    def _gen_for(self, node: ForStmt):
        """
        for (init; cond; step) stmt
        """

        # init
        if node.init is not None:
            if isinstance(node.init, Assign):
                self._gen_assign(node.init)
            else:
                self._gen_expr(node.init)

        cond_block = self._new_block("for.cond")
        body_block = self._new_block("for.body")
        step_block = self._new_block("for.step")
        end_block = self._new_block("for.end")

        # salto desde el bloque actual a for.cond
        self._terminate_block(Jump(cond_block))

        # COND
        self._position_at_end(cond_block)
        if node.cond is not None:
            cond_val = self._gen_expr(node.cond)
            if cond_val.type != "i1":
                raise Exception("La condición del for debe ser booleana (i1)")
            self._terminate_block(Branch(cond_val, body_block, end_block))
        else:
            self._terminate_block(Jump(body_block))

        # BODY
        self._position_at_end(body_block)
        self._gen_stmt(node.body)
        if not self.block_terminated:
            self._terminate_block(Jump(step_block))

        # STEP
        self._position_at_end(step_block)
        if node.step is not None:
            if isinstance(node.step, Assign):
                self._gen_assign(node.step)
            else:
                self._gen_expr(node.step)
        self._terminate_block(Jump(cond_block))

        # END
        self._position_at_end(end_block)

    # ======================================================
    # PRINT (incluye strings)
    # ======================================================

    def _gen_print(self, node: PrintStmt):
        exprs = node.expr if isinstance(node.expr, list) else [node.expr]

        for expr in exprs:
            # Strings: imprimir char por char
            if isinstance(expr, String):
                for ch in expr.value:
                    cv = Constant(ord(ch), "i8")
                    self.builder.call(
                        self.module.get_function("print_char"),
                        [cv],
                    )
                continue

            val = self._gen_expr(expr)

            if val.type == "i32":
                self.builder.call(self.module.get_function("print_int"), [val])
            elif val.type == "float":
                self.builder.call(self.module.get_function("print_float"), [val])
            elif val.type == "i1":
                self.builder.call(self.module.get_function("print_bool"), [val])
            elif val.type == "i8":
                self.builder.call(self.module.get_function("print_char"), [val])
            else:
                raise Exception(f"print: tipo no soportado: {val.type}")

    # ======================================================
    # Llamadas a funciones
    # ======================================================

    def _gen_call(self, node: Call):
        fname = node.func.name
        fn = self.module.get_function(fname)
        args = [self._gen_expr(a) for a in node.args]
        return self.builder.call(fn, args)

    # ======================================================
    # Arrays
    # ======================================================

    def _gen_array_access(self, node: ArrayAccess):
        name = node.array.name
        index_val = self._gen_expr(node.index)
        elem_type = self._infer_array_elem_type(name)

        arr_ptr = self.locals.get(name)
        arr_type = self.local_types.get(name)

        if arr_ptr is None:
            g = self.module.get_global(name)
            if g:
                from ir.value import GlobalRef
                arr_ptr = GlobalRef(name, g.type)
                arr_type = g.type

        from ir.instr import GetElementPtr

        if arr_type and arr_type.startswith("["):
            elem_ptr = self.func.new_temp(f"{elem_type}*")
            gep = GetElementPtr(arr_ptr, index_val, elem_ptr)
            self.builder.block.append(gep)
            return self.builder.load(elem_ptr, elem_type)

        if arr_type and arr_type.endswith("*"):
            base_ptr = self.builder.load(arr_ptr, arr_type)
            elem_ptr = self.func.new_temp(f"{elem_type}*")
            gep = GetElementPtr(base_ptr, index_val, elem_ptr)
            self.builder.block.append(gep)
            return self.builder.load(elem_ptr, elem_type)

        raise Exception(f"Acceso a array desconocido: {name}")

    def _gen_assign_array(self, node: Assign):
        left = node.left
        name = left.array.name
        index_val = self._gen_expr(left.index)
        elem_type = self._infer_array_elem_type(name)

        arr_ptr = self.locals.get(name)
        arr_type = self.local_types.get(name)

        if arr_ptr is None:
            g = self.module.get_global(name)
            if g:
                from ir.value import GlobalRef
                arr_ptr = GlobalRef(name, g.type)
                arr_type = g.type

        from ir.instr import GetElementPtr

        if arr_type and arr_type.startswith("["):
            dst_ptr = self.func.new_temp(f"{elem_type}*")
            gep = GetElementPtr(arr_ptr, index_val, dst_ptr)
            self.builder.block.append(gep)
            val = self._gen_expr(node.right)
            self.builder.store(val, dst_ptr)
            return val

        if arr_type and arr_type.endswith("*"):
            base_ptr = self.builder.load(arr_ptr, arr_type)
            dst_ptr = self.func.new_temp(f"{elem_type}*")
            gep = GetElementPtr(base_ptr, index_val, dst_ptr)
            self.builder.block.append(gep)
            val = self._gen_expr(node.right)
            self.builder.store(val, dst_ptr)
            return val

        raise Exception(f"Asig. array desconocido: {name}")

    # ======================================================
    # ++ y --
    # ======================================================

    def _gen_incdec(self, node: BinOper):
        if not isinstance(node.left, Identifier):
            raise Exception("++/-- sólo soportado sobre identificadores")

        name = node.left.name
        ptr, llvm_type = self._lookup_scalar_ptr_and_type(name)

        val = self.builder.load(ptr, llvm_type)
        one = Constant(1, llvm_type)

        from ir.instr import BinOp as IRBinOp
        opcode = "add" if node.oper == "++" else "sub"
        result = self.func.new_temp(llvm_type)
        instr = IRBinOp(opcode, val, one, result)
        self.builder.block.append(instr)
        self.builder.store(result, ptr)
        return result

    # ======================================================
    # Expresiones
    # ======================================================

    def _gen_expr(self, node):

        # ================================
        # LITERALES
        # ================================
        if isinstance(node, Integer):
            return Constant(node.value, "i32")

        if isinstance(node, Float):
            return Constant(node.value, "float")

        if isinstance(node, Boolean):
            return Constant(1 if node.value else 0, "i1")

        if isinstance(node, Char):
            return Constant(ord(node.value), "i8")

        # ================================
        # IDENTIFICADORES
        # ================================
        if isinstance(node, Identifier):
            name = node.name

            # LOCAL
            if name in self.locals:
                ptr = self.locals[name]
                llvm_type = self.local_types[name]

                # Arrays locales: decaen a puntero al primer elemento (T*)
                if llvm_type.startswith("["):
                    elem_type = self._infer_array_elem_type(name)
                    from ir.instr import GetElementPtr
                    zero = Constant(0, "i32")
                    elem_ptr = self.func.new_temp(f"{elem_type}*")
                    gep = GetElementPtr(ptr, zero, elem_ptr)
                    self.builder.block.append(gep)
                    return elem_ptr

                # Escalares → load normal
                return self.builder.load(ptr, llvm_type)

            # GLOBAL
            g = self.module.get_global(name)
            if g:
                from ir.value import GlobalRef
                ptr = GlobalRef(name, g.type)

                if g.type.startswith("["):
                    elem_type = self._infer_array_elem_type(name)
                    from ir.instr import GetElementPtr
                    zero = Constant(0, "i32")
                    elem_ptr = self.func.new_temp(f"{elem_type}*")
                    gep = GetElementPtr(ptr, zero, elem_ptr)
                    self.builder.block.append(gep)
                    return elem_ptr

                return self.builder.load(ptr, g.type)

            raise Exception(f"Variable '{name}' no encontrada")

        # ================================
        # ARRAY ACCESS
        # ================================
        if isinstance(node, ArrayAccess):
            return self._gen_array_access(node)

        # ================================
        # OPERADORES BINARIOS
        # ================================
        if isinstance(node, BinOper):
            return self._gen_binop(node)

        # ================================
        # UNARIOS
        # ================================
        if isinstance(node, UnaryOper):
            from ir.instr import BinOp as IRBinOp
            if node.oper == '!':
                val = self._gen_expr(node.expr)
                r = self.func.new_temp("i1")
                instr = IRBinOp("xor", val, Constant(1, "i1"), r)
                self.builder.block.append(instr)
                return r

            if node.oper == '-':
                val = self._gen_expr(node.expr)
                zero = Constant(0, val.type)
                r = self.func.new_temp(val.type)
                instr = IRBinOp("sub", zero, val, r)
                self.builder.block.append(instr)
                return r

        # ================================
        # CALL
        # ================================
        if isinstance(node, Call):
            return self._gen_call(node)

        print(f"[Warning] Expr no soportada: {type(node).__name__}")
        return None

    # ======================================================
    # BINOPS
    # ======================================================

    def _gen_binop(self, node: BinOper):
        op = node.oper

        if op in ("++", "--"):
            return self._gen_incdec(node)

        left = self._gen_expr(node.left)
        right = self._gen_expr(node.right)
        from ir.instr import BinOp as IRBinOp

        is_float = (left.type == "float")

        if op == '+':
            if is_float:
                r = self.func.new_temp("float")
                instr = IRBinOp("fadd", left, right, r)
                self.builder.block.append(instr)
                return r
            return self.builder.add(left, right)

        if op == '-':
            if is_float:
                r = self.func.new_temp("float")
                instr = IRBinOp("fsub", left, right, r)
                self.builder.block.append(instr)
                return r
            r = self.func.new_temp("i32")
            instr = IRBinOp("sub", left, right, r)
            self.builder.block.append(instr)
            return r

        if op == '*':
            if is_float:
                r = self.func.new_temp("float")
                instr = IRBinOp("fmul", left, right, r)
                self.builder.block.append(instr)
                return r
            r = self.func.new_temp("i32")
            instr = IRBinOp("mul", left, right, r)
            self.builder.block.append(instr)
            return r

        if op == '/':
            if is_float:
                r = self.func.new_temp("float")
                instr = IRBinOp("fdiv", left, right, r)
                self.builder.block.append(instr)
                return r
            r = self.func.new_temp("i32")
            instr = IRBinOp("sdiv", left, right, r)
            self.builder.block.append(instr)
            return r

        # 🔹 NUEVO: operador módulo %
        if op == '%':
            if is_float:
                raise Exception("El operador % no está definido para float")
            r = self.func.new_temp("i32")
            instr = IRBinOp("srem", left, right, r)
            self.builder.block.append(instr)
            return r

        # Comparaciones → i1
        if op in ('<', '<=', '>', '>=', '==', '!='):
            r = self.func.new_temp("i1")

            if is_float:
                if op == '<': opcode = "fcmp_olt"
                elif op == '<=': opcode = "fcmp_ole"
                elif op == '>': opcode = "fcmp_ogt"
                elif op == '>=': opcode = "fcmp_oge"
                elif op == '==': opcode = "fcmp_oeq"
                else: opcode = "fcmp_one"
            else:
                if op == '<': opcode = "icmp_slt"
                elif op == '<=': opcode = "icmp_sle"
                elif op == '>': opcode = "icmp_sgt"
                elif op == '>=': opcode = "icmp_sge"
                elif op == '==': opcode = "icmp_eq"
                else: opcode = "icmp_ne"

            instr = IRBinOp(opcode, left, right, r)
            self.builder.block.append(instr)
            return r

        if op == '&&':
            r = self.func.new_temp("i1")
            instr = IRBinOp("and", left, right, r)
            self.builder.block.append(instr)
            return r

        if op == '||':
            r = self.func.new_temp("i1")
            instr = IRBinOp("or", left, right, r)
            self.builder.block.append(instr)
            return r

        print(f"[Warning] BinOp no soportado: {op}")
        return None


    # ======================================================
    # Map types
    # ======================================================

    def _map_type(self, t):
        if t is None:
            return "void"

        if isinstance(t, ArrayType):
            elem = self._map_type(t.elem_type)
            # Parámetros tipo array → T*
            return elem + "*"

        name = t.name
        if name == "integer": return "i32"
        if name == "float": return "float"
        if name == "boolean": return "i1"
        if name == "char": return "i8"
        if name == "void": return "void"

        print(f"[Warning] Tipo no soportado: {name}")
        return "i32"
