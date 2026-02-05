"""
RLangC Syntax Tree Construction
Uses recursive descent with operator precedence climbing
"""

# Abstract syntax representation classes
class TreeNode:
    """Base for all syntax tree nodes"""
    def __init__(self):
        self.location = (0, 0)

# Expression nodes
class NumNode(TreeNode):
    def __init__(self, value, is_float=False):
        super().__init__()
        self.value = value
        self.is_float = is_float

class TextNode(TreeNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

class BoolNode(TreeNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

class NullNode(TreeNode):
    def __init__(self):
        super().__init__()

class VarRefNode(TreeNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

class BinOpNode(TreeNode):
    def __init__(self, op, lhs, rhs):
        super().__init__()
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class UnOpNode(TreeNode):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

class InvokeNode(TreeNode):
    def __init__(self, target, args):
        super().__init__()
        self.target = target
        self.args = args

class SubscriptNode(TreeNode):
    def __init__(self, obj, idx):
        super().__init__()
        self.obj = obj
        self.idx = idx

class AttrNode(TreeNode):
    def __init__(self, obj, attr):
        super().__init__()
        self.obj = obj
        self.attr = attr

class ArrayNode(TreeNode):
    def __init__(self, items):
        super().__init__()
        self.items = items

# Type annotation
class TypeSpec(TreeNode):
    def __init__(self, name, optional=False):
        super().__init__()
        self.name = name
        self.optional = optional

# Statement nodes
class StmtNode(TreeNode):
    pass

class ExprStmt(StmtNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

class VarDeclNode(StmtNode):
    def __init__(self, name, type_spec, init_val, immutable):
        super().__init__()
        self.name = name
        self.type_spec = type_spec
        self.init_val = init_val
        self.immutable = immutable

class FuncParam:
    def __init__(self, name, type_spec, default):
        self.name = name
        self.type_spec = type_spec
        self.default = default

class FuncDeclNode(StmtNode):
    def __init__(self, name, params, ret_type, body):
        super().__init__()
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body

class RetNode(StmtNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

class CondNode(StmtNode):
    def __init__(self, branches, fallback):
        super().__init__()
        self.branches = branches  # [(condition, body), ...]
        self.fallback = fallback

class LoopNode(StmtNode):
    def __init__(self, cond, body):
        super().__init__()
        self.cond = cond
        self.body = body

class IterNode(StmtNode):
    def __init__(self, var, iterable, body):
        super().__init__()
        self.var = var
        self.iterable = iterable
        self.body = body

class SkipNode(StmtNode):
    pass

class HaltNode(StmtNode):
    pass

class NoopNode(StmtNode):
    pass

class AssignNode(StmtNode):
    def __init__(self, target, op, value):
        super().__init__()
        self.target = target
        self.op = op
        self.value = value

class BlockNode(TreeNode):
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts

class ClassDeclNode(StmtNode):
    def __init__(self, name, body):
        super().__init__()
        self.name = name
        self.body = body

class ModuleImportNode(StmtNode):
    def __init__(self, mod_name, items, alias):
        super().__init__()
        self.mod_name = mod_name
        self.items = items
        self.alias = alias

class ProgramNode(TreeNode):
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts


from .scanner import TokenKind

class SyntaxBuilder:
    """Builds syntax tree from tokens using recursive descent"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.cursor = 0
    
    def current(self):
        return self.tokens[self.cursor] if self.cursor < len(self.tokens) else None
    
    def lookahead(self, offset=1):
        pos = self.cursor + offset
        return self.tokens[pos] if pos < len(self.tokens) else None
    
    def move_forward(self):
        tok = self.current()
        if tok and tok.kind != TokenKind.END:
            self.cursor += 1
        return tok
    
    def require(self, expected_kind):
        tok = self.current()
        if not tok or tok.kind != expected_kind:
            raise SyntaxError(f"Expected {TokenKind.name_of(expected_kind)}, got {tok}")
        return self.move_forward()
    
    def check(self, *kinds):
        tok = self.current()
        return tok and tok.kind in kinds
    
    def discard_newlines(self):
        while self.check(TokenKind.NEWLINE):
            self.move_forward()
    
    def build_tree(self):
        """Entry point for parsing"""
        stmts = []
        self.discard_newlines()
        
        while self.current() and self.current().kind != TokenKind.END:
            stmt = self.parse_stmt()
            if stmt:
                stmts.append(stmt)
            self.discard_newlines()
        
        return ProgramNode(stmts)
    
    def parse_stmt(self):
        """Parse a statement"""
        self.discard_newlines()
        tok = self.current()
        
        if not tok or tok.kind == TokenKind.END:
            return None
        
        if tok.kind == TokenKind.FUNC_DEF:
            return self.parse_func_decl()
        if tok.kind in (TokenKind.VAR_LET, TokenKind.VAR_CONST):
            return self.parse_var_decl()
        if tok.kind == TokenKind.COND_IF:
            return self.parse_cond()
        if tok.kind == TokenKind.LOOP_WHILE:
            return self.parse_loop()
        if tok.kind == TokenKind.LOOP_FOR:
            return self.parse_iter()
        if tok.kind == TokenKind.RET:
            return self.parse_ret()
        if tok.kind == TokenKind.SKIP:
            self.move_forward()
            self.discard_newlines()
            return SkipNode()
        if tok.kind == TokenKind.HALT:
            self.move_forward()
            self.discard_newlines()
            return HaltNode()
        if tok.kind == TokenKind.NOOP:
            self.move_forward()
            self.discard_newlines()
            return NoopNode()
        if tok.kind == TokenKind.STRUCT_CLASS:
            return self.parse_class()
        if tok.kind in (TokenKind.MOD_IMPORT, TokenKind.MOD_FROM):
            return self.parse_import()
        
        # Try expression or assignment
        expr = self.parse_expr()
        
        if self.check(TokenKind.ASSIGN, TokenKind.ASSIGN_ADD, TokenKind.ASSIGN_SUB,
                     TokenKind.ASSIGN_MUL, TokenKind.ASSIGN_DIV):
            op_tok = self.move_forward()
            val = self.parse_expr()
            self.discard_newlines()
            return AssignNode(expr, op_tok.text, val)
        
        self.discard_newlines()
        return ExprStmt(expr)
    
    def parse_func_decl(self):
        """Parse function declaration"""
        self.require(TokenKind.FUNC_DEF)
        name_tok = self.require(TokenKind.NAME)
        
        self.require(TokenKind.GROUP_LPAREN)
        params = self.parse_func_params()
        self.require(TokenKind.GROUP_RPAREN)
        
        ret_type = None
        if self.check(TokenKind.PUNCT_RARROW):
            self.move_forward()
            ret_type = self.parse_type_spec()
        
        self.require(TokenKind.PUNCT_COLON)
        self.discard_newlines()
        
        body = self.parse_block()
        return FuncDeclNode(name_tok.val, params, ret_type, body)
    
    def parse_func_params(self):
        """Parse function parameters"""
        params = []
        
        if self.check(TokenKind.GROUP_RPAREN):
            return params
        
        while True:
            name_tok = self.require(TokenKind.NAME)
            
            type_spec = None
            if self.check(TokenKind.PUNCT_COLON):
                self.move_forward()
                type_spec = self.parse_type_spec()
            
            default = None
            if self.check(TokenKind.ASSIGN):
                self.move_forward()
                default = self.parse_expr()
            
            params.append(FuncParam(name_tok.val, type_spec, default))
            
            if not self.check(TokenKind.PUNCT_COMMA):
                break
            self.move_forward()
        
        return params
    
    def parse_type_spec(self):
        """Parse type annotation"""
        name_tok = self.require(TokenKind.NAME)
        return TypeSpec(name_tok.val)
    
    def parse_var_decl(self):
        """Parse variable declaration"""
        is_const = self.current().kind == TokenKind.VAR_CONST
        self.move_forward()
        
        name_tok = self.require(TokenKind.NAME)
        
        type_spec = None
        if self.check(TokenKind.PUNCT_COLON):
            self.move_forward()
            type_spec = self.parse_type_spec()
        
        init_val = None
        if self.check(TokenKind.ASSIGN):
            self.move_forward()
            init_val = self.parse_expr()
        
        self.discard_newlines()
        return VarDeclNode(name_tok.val, type_spec, init_val, is_const)
    
    def parse_cond(self):
        """Parse if/elif/else"""
        self.require(TokenKind.COND_IF)
        first_cond = self.parse_expr()
        self.require(TokenKind.PUNCT_COLON)
        self.discard_newlines()
        first_body = self.parse_block()
        
        branches = [(first_cond, first_body)]
        
        while self.check(TokenKind.COND_ELIF):
            self.move_forward()
            cond = self.parse_expr()
            self.require(TokenKind.PUNCT_COLON)
            self.discard_newlines()
            body = self.parse_block()
            branches.append((cond, body))
        
        fallback = None
        if self.check(TokenKind.COND_ELSE):
            self.move_forward()
            self.require(TokenKind.PUNCT_COLON)
            self.discard_newlines()
            fallback = self.parse_block()
        
        return CondNode(branches, fallback)
    
    def parse_loop(self):
        """Parse while loop"""
        self.require(TokenKind.LOOP_WHILE)
        cond = self.parse_expr()
        self.require(TokenKind.PUNCT_COLON)
        self.discard_newlines()
        body = self.parse_block()
        return LoopNode(cond, body)
    
    def parse_iter(self):
        """Parse for loop"""
        self.require(TokenKind.LOOP_FOR)
        var_tok = self.require(TokenKind.NAME)
        self.require(TokenKind.ITER_IN)
        iterable = self.parse_expr()
        self.require(TokenKind.PUNCT_COLON)
        self.discard_newlines()
        body = self.parse_block()
        return IterNode(var_tok.val, iterable, body)
    
    def parse_ret(self):
        """Parse return statement"""
        self.require(TokenKind.RET)
        
        val = None
        if not self.check(TokenKind.NEWLINE, TokenKind.END):
            val = self.parse_expr()
        
        self.discard_newlines()
        return RetNode(val)
    
    def parse_class(self):
        """Parse class"""
        self.require(TokenKind.STRUCT_CLASS)
        name_tok = self.require(TokenKind.NAME)
        self.require(TokenKind.PUNCT_COLON)
        self.discard_newlines()
        body = self.parse_block()
        return ClassDeclNode(name_tok.val, body)
    
    def parse_import(self):
        """Parse import"""
        if self.check(TokenKind.MOD_FROM):
            self.move_forward()
            mod_tok = self.require(TokenKind.NAME)
            self.require(TokenKind.MOD_IMPORT)
            
            items = []
            while True:
                item_tok = self.require(TokenKind.NAME)
                items.append(item_tok.val)
                if not self.check(TokenKind.PUNCT_COMMA):
                    break
                self.move_forward()
            
            alias = None
            if self.check(TokenKind.MOD_AS):
                self.move_forward()
                alias_tok = self.require(TokenKind.NAME)
                alias = alias_tok.val
            
            self.discard_newlines()
            return ModuleImportNode(mod_tok.val, items, alias)
        else:
            self.require(TokenKind.MOD_IMPORT)
            mod_tok = self.require(TokenKind.NAME)
            
            alias = None
            if self.check(TokenKind.MOD_AS):
                self.move_forward()
                alias_tok = self.require(TokenKind.NAME)
                alias = alias_tok.val
            
            self.discard_newlines()
            return ModuleImportNode(mod_tok.val, None, alias)
    
    def parse_block(self):
        """Parse block (indented or braced)"""
        stmts = []
        
        if self.check(TokenKind.GROUP_LBRACE):
            self.move_forward()
            self.discard_newlines()
            
            while not self.check(TokenKind.GROUP_RBRACE, TokenKind.END):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt)
                self.discard_newlines()
            
            self.require(TokenKind.GROUP_RBRACE)
            self.discard_newlines()
        else:
            self.require(TokenKind.INDENT)
            
            while not self.check(TokenKind.DEDENT, TokenKind.END):
                stmt = self.parse_stmt()
                if stmt:
                    stmts.append(stmt)
                self.discard_newlines()
            
            if self.check(TokenKind.DEDENT):
                self.move_forward()
        
        return BlockNode(stmts)
    
    def parse_expr(self):
        """Parse expression with precedence climbing"""
        return self.parse_precedence(0)
    
    def parse_precedence(self, min_prec):
        """Operator precedence climbing algorithm"""
        left = self.parse_unary()
        
        while True:
            tok = self.current()
            if not tok:
                break
            
            prec = self.get_precedence(tok.kind)
            if prec < min_prec:
                break
            
            op_tok = self.move_forward()
            right = self.parse_precedence(prec + 1)
            left = BinOpNode(op_tok.text, left, right)
        
        return left
    
    def get_precedence(self, kind):
        """Get operator precedence"""
        precedence_map = {
            TokenKind.LOGIC_OR: 1,
            TokenKind.LOGIC_AND: 2,
            TokenKind.CMP_EQ: 3, TokenKind.CMP_NEQ: 3,
            TokenKind.CMP_LT: 3, TokenKind.CMP_LTE: 3,
            TokenKind.CMP_GT: 3, TokenKind.CMP_GTE: 3,
            TokenKind.BIT_OR: 4,
            TokenKind.BIT_XOR: 5,
            TokenKind.BIT_AND: 6,
            TokenKind.BIT_SHL: 7, TokenKind.BIT_SHR: 7,
            TokenKind.ARITH_ADD: 8, TokenKind.ARITH_SUB: 8,
            TokenKind.ARITH_MUL: 9, TokenKind.ARITH_DIV: 9,
            TokenKind.ARITH_MOD: 9, TokenKind.ARITH_FLOORDIV: 9,
            TokenKind.ARITH_POW: 10,
        }
        return precedence_map.get(kind, -1)
    
    def parse_unary(self):
        """Parse unary expression"""
        if self.check(TokenKind.LOGIC_NOT, TokenKind.ARITH_SUB, 
                     TokenKind.ARITH_ADD, TokenKind.BIT_NOT):
            op_tok = self.move_forward()
            operand = self.parse_unary()
            return UnOpNode(op_tok.text, operand)
        
        return self.parse_postfix()
    
    def parse_postfix(self):
        """Parse postfix operations (calls, subscripts, attributes)"""
        expr = self.parse_atomic()
        
        while True:
            if self.check(TokenKind.GROUP_LPAREN):
                self.move_forward()
                args = self.parse_call_args()
                self.require(TokenKind.GROUP_RPAREN)
                expr = InvokeNode(expr, args)
            elif self.check(TokenKind.GROUP_LSQUARE):
                self.move_forward()
                idx = self.parse_expr()
                self.require(TokenKind.GROUP_RSQUARE)
                expr = SubscriptNode(expr, idx)
            elif self.check(TokenKind.PUNCT_DOT):
                self.move_forward()
                attr_tok = self.require(TokenKind.NAME)
                expr = AttrNode(expr, attr_tok.val)
            else:
                break
        
        return expr
    
    def parse_call_args(self):
        """Parse call arguments"""
        args = []
        
        if self.check(TokenKind.GROUP_RPAREN):
            return args
        
        while True:
            args.append(self.parse_expr())
            if not self.check(TokenKind.PUNCT_COMMA):
                break
            self.move_forward()
        
        return args
    
    def parse_atomic(self):
        """Parse atomic expression"""
        tok = self.current()
        
        if not tok:
            raise SyntaxError("Unexpected end")
        
        if tok.kind == TokenKind.NUM_INT:
            self.move_forward()
            return NumNode(tok.val, False)
        
        if tok.kind == TokenKind.NUM_FLOAT:
            self.move_forward()
            return NumNode(tok.val, True)
        
        if tok.kind == TokenKind.TEXT:
            self.move_forward()
            return TextNode(tok.val)
        
        if tok.kind == TokenKind.BOOL_T:
            self.move_forward()
            return BoolNode(True)
        
        if tok.kind == TokenKind.BOOL_F:
            self.move_forward()
            return BoolNode(False)
        
        if tok.kind == TokenKind.NULL:
            self.move_forward()
            return NullNode()
        
        if tok.kind == TokenKind.NAME:
            self.move_forward()
            return VarRefNode(tok.val)
        
        if tok.kind == TokenKind.GROUP_LPAREN:
            self.move_forward()
            expr = self.parse_expr()
            self.require(TokenKind.GROUP_RPAREN)
            return expr
        
        if tok.kind == TokenKind.GROUP_LSQUARE:
            return self.parse_array()
        
        raise SyntaxError(f"Unexpected token: {tok}")
    
    def parse_array(self):
        """Parse array literal"""
        self.require(TokenKind.GROUP_LSQUARE)
        items = []
        
        if not self.check(TokenKind.GROUP_RSQUARE):
            while True:
                items.append(self.parse_expr())
                if not self.check(TokenKind.PUNCT_COMMA):
                    break
                self.move_forward()
        
        self.require(TokenKind.GROUP_RSQUARE)
        return ArrayNode(items)
