"""
RLangC Tokenization Module
Handles source code scanning with unique finite automaton approach
"""

class TokenKind:
    """Enumeration of token categories using unique naming"""
    # Primitive values
    NUM_INT, NUM_FLOAT, TEXT, BOOL_T, BOOL_F, NULL = range(6)
    
    # Keywords for declarations
    FUNC_DEF, VAR_LET, VAR_CONST = range(6, 9)
    
    # Control keywords
    COND_IF, COND_ELSE, COND_ELIF, LOOP_WHILE, LOOP_FOR, ITER_IN = range(9, 15)
    RET, SKIP, HALT, STRUCT_CLASS, MOD_IMPORT, MOD_FROM, MOD_AS, NOOP = range(15, 23)
    
    # Identifiers
    NAME = 23
    
    # Punctuation
    PUNCT_COLON, PUNCT_RARROW, PUNCT_COMMA, PUNCT_DOT, PUNCT_SEMI = range(24, 29)
    
    # Grouping
    GROUP_LPAREN, GROUP_RPAREN, GROUP_LBRACE, GROUP_RBRACE = range(29, 33)
    GROUP_LSQUARE, GROUP_RSQUARE = range(33, 35)
    
    # Arithmetic
    ARITH_ADD, ARITH_SUB, ARITH_MUL, ARITH_DIV, ARITH_MOD = range(35, 40)
    ARITH_POW, ARITH_FLOORDIV = range(40, 42)
    
    # Comparison
    CMP_EQ, CMP_NEQ, CMP_LT, CMP_LTE, CMP_GT, CMP_GTE = range(42, 48)
    
    # Logic
    LOGIC_AND, LOGIC_OR, LOGIC_NOT = range(48, 51)
    
    # Bitwise
    BIT_AND, BIT_OR, BIT_XOR, BIT_NOT, BIT_SHL, BIT_SHR = range(51, 57)
    
    # Assignment
    ASSIGN, ASSIGN_ADD, ASSIGN_SUB, ASSIGN_MUL, ASSIGN_DIV = range(57, 62)
    
    # Special
    NEWLINE, INDENT, DEDENT, END = range(62, 66)

    @staticmethod
    def name_of(kind):
        """Get string name for debugging"""
        names = {
            TokenKind.NUM_INT: "NUM_INT", TokenKind.NUM_FLOAT: "NUM_FLOAT",
            TokenKind.TEXT: "TEXT", TokenKind.BOOL_T: "BOOL_T",
            TokenKind.BOOL_F: "BOOL_F", TokenKind.NULL: "NULL",
            TokenKind.FUNC_DEF: "FUNC_DEF", TokenKind.VAR_LET: "VAR_LET",
            TokenKind.VAR_CONST: "VAR_CONST", TokenKind.NAME: "NAME",
            TokenKind.END: "END", TokenKind.NEWLINE: "NEWLINE"
        }
        return names.get(kind, f"Kind{kind}")


class CodeToken:
    """Represents a scanned token with position tracking"""
    __slots__ = ['kind', 'text', 'val', 'row', 'col']
    
    def __init__(self, kind, text, val, row, col):
        self.kind = kind
        self.text = text
        self.val = val
        self.row = row
        self.col = col
    
    def __repr__(self):
        return f"<{TokenKind.name_of(self.kind)} '{self.text}' @{self.row}:{self.col}>"


class SourceScanner:
    """Scans source code into tokens using custom state machine"""
    
    RESERVED_WORDS = {
        'def': TokenKind.FUNC_DEF,
        'let': TokenKind.VAR_LET,
        'const': TokenKind.VAR_CONST,
        'if': TokenKind.COND_IF,
        'else': TokenKind.COND_ELSE,
        'elif': TokenKind.COND_ELIF,
        'while': TokenKind.LOOP_WHILE,
        'for': TokenKind.LOOP_FOR,
        'in': TokenKind.ITER_IN,
        'return': TokenKind.RET,
        'break': TokenKind.SKIP,
        'continue': TokenKind.HALT,
        'class': TokenKind.STRUCT_CLASS,
        'import': TokenKind.MOD_IMPORT,
        'from': TokenKind.MOD_FROM,
        'as': TokenKind.MOD_AS,
        'pass': TokenKind.NOOP,
        'true': TokenKind.BOOL_T,
        'false': TokenKind.BOOL_F,
        'none': TokenKind.NULL,
        'and': TokenKind.LOGIC_AND,
        'or': TokenKind.LOGIC_OR,
        'not': TokenKind.LOGIC_NOT,
    }
    
    def __init__(self, code):
        self.code = code
        self.idx = 0
        self.row = 1
        self.col = 1
        self.output = []
        self.indent_levels = [0]
    
    def peek_ahead(self, offset=0):
        """Look at character without consuming"""
        pos = self.idx + offset
        return self.code[pos] if pos < len(self.code) else None
    
    def consume_char(self):
        """Advance and return current character"""
        if self.idx >= len(self.code):
            return None
        ch = self.code[self.idx]
        self.idx += 1
        if ch == '\n':
            self.row += 1
            self.col = 1
        else:
            self.col += 1
        return ch
    
    def scan_numeric(self):
        """Scan integer or float number"""
        start_row, start_col = self.row, self.col
        buffer = ''
        has_decimal = False
        
        while self.peek_ahead() and (self.peek_ahead().isdigit() or self.peek_ahead() == '.'):
            ch = self.peek_ahead()
            if ch == '.':
                if has_decimal:
                    break
                has_decimal = True
            buffer += self.consume_char()
        
        if has_decimal:
            return CodeToken(TokenKind.NUM_FLOAT, buffer, float(buffer), start_row, start_col)
        return CodeToken(TokenKind.NUM_INT, buffer, int(buffer), start_row, start_col)
    
    def scan_text_literal(self, quote):
        """Scan string with escape handling"""
        start_row, start_col = self.row, self.col
        self.consume_char()  # consume opening quote
        buffer = ''
        
        while self.peek_ahead() and self.peek_ahead() != quote:
            ch = self.consume_char()
            if ch == '\\':
                next_ch = self.consume_char()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', quote: quote}
                buffer += escape_map.get(next_ch, next_ch)
            else:
                buffer += ch
        
        if self.peek_ahead() == quote:
            self.consume_char()  # consume closing quote
        
        return CodeToken(TokenKind.TEXT, buffer, buffer, start_row, start_col)
    
    def scan_identifier(self):
        """Scan identifier or keyword"""
        start_row, start_col = self.row, self.col
        buffer = ''
        
        while self.peek_ahead() and (self.peek_ahead().isalnum() or self.peek_ahead() == '_'):
            buffer += self.consume_char()
        
        kind = self.RESERVED_WORDS.get(buffer, TokenKind.NAME)
        
        # Handle special values for literals
        if kind == TokenKind.BOOL_T:
            val = True
        elif kind == TokenKind.BOOL_F:
            val = False
        elif kind == TokenKind.NULL:
            val = None
        else:
            val = buffer
        
        return CodeToken(kind, buffer, val, start_row, start_col)
    
    def handle_line_indent(self, spaces):
        """Process indentation changes"""
        current = self.indent_levels[-1]
        
        if spaces > current:
            self.indent_levels.append(spaces)
            self.output.append(CodeToken(TokenKind.INDENT, '', None, self.row, 1))
        else:
            while len(self.indent_levels) > 1 and self.indent_levels[-1] > spaces:
                self.indent_levels.pop()
                self.output.append(CodeToken(TokenKind.DEDENT, '', None, self.row, 1))
    
    def tokenize(self):
        """Main scanning loop"""
        line_start = True
        
        while self.idx < len(self.code):
            # Handle indentation at line beginning
            if line_start:
                space_count = 0
                while self.peek_ahead() in ' \t':
                    if self.consume_char() == ' ':
                        space_count += 1
                    else:
                        space_count += 4
                
                # Skip blank lines and comments
                if self.peek_ahead() in ('\n', '#', None):
                    if self.peek_ahead() == '#':
                        while self.peek_ahead() and self.peek_ahead() != '\n':
                            self.consume_char()
                    if self.peek_ahead() == '\n':
                        self.consume_char()
                    continue
                
                self.handle_line_indent(space_count)
                line_start = False
            
            ch = self.peek_ahead()
            if not ch:
                break
            
            # Whitespace (not at line start)
            if ch in ' \t':
                self.consume_char()
                continue
            
            # Newlines
            if ch == '\n':
                self.output.append(CodeToken(TokenKind.NEWLINE, '\n', '\n', self.row, self.col))
                self.consume_char()
                line_start = True
                continue
            
            # Comments
            if ch == '#':
                while self.peek_ahead() and self.peek_ahead() != '\n':
                    self.consume_char()
                continue
            
            # Numbers
            if ch.isdigit():
                self.output.append(self.scan_numeric())
                continue
            
            # Strings
            if ch in ('"', "'"):
                self.output.append(self.scan_text_literal(ch))
                continue
            
            # Identifiers
            if ch.isalpha() or ch == '_':
                self.output.append(self.scan_identifier())
                continue
            
            # Multi-character operators
            start_row, start_col = self.row, self.col
            
            two_char_ops = {
                '==': TokenKind.CMP_EQ, '!=': TokenKind.CMP_NEQ,
                '<=': TokenKind.CMP_LTE, '>=': TokenKind.CMP_GTE,
                '<<': TokenKind.BIT_SHL, '>>': TokenKind.BIT_SHR,
                '**': TokenKind.ARITH_POW, '//': TokenKind.ARITH_FLOORDIV,
                '->': TokenKind.PUNCT_RARROW,
                '+=': TokenKind.ASSIGN_ADD, '-=': TokenKind.ASSIGN_SUB,
                '*=': TokenKind.ASSIGN_MUL, '/=': TokenKind.ASSIGN_DIV,
            }
            
            two_ch = ch + (self.peek_ahead(1) or '')
            if two_ch in two_char_ops:
                self.consume_char()
                self.consume_char()
                self.output.append(CodeToken(two_char_ops[two_ch], two_ch, two_ch, start_row, start_col))
                continue
            
            # Single-character tokens
            single_ops = {
                '+': TokenKind.ARITH_ADD, '-': TokenKind.ARITH_SUB,
                '*': TokenKind.ARITH_MUL, '/': TokenKind.ARITH_DIV,
                '%': TokenKind.ARITH_MOD, '<': TokenKind.CMP_LT,
                '>': TokenKind.CMP_GT, '=': TokenKind.ASSIGN,
                '&': TokenKind.BIT_AND, '|': TokenKind.BIT_OR,
                '^': TokenKind.BIT_XOR, '~': TokenKind.BIT_NOT,
                '(': TokenKind.GROUP_LPAREN, ')': TokenKind.GROUP_RPAREN,
                '{': TokenKind.GROUP_LBRACE, '}': TokenKind.GROUP_RBRACE,
                '[': TokenKind.GROUP_LSQUARE, ']': TokenKind.GROUP_RSQUARE,
                ',': TokenKind.PUNCT_COMMA, '.': TokenKind.PUNCT_DOT,
                ':': TokenKind.PUNCT_COLON, ';': TokenKind.PUNCT_SEMI,
            }
            
            if ch in single_ops:
                self.consume_char()
                self.output.append(CodeToken(single_ops[ch], ch, ch, start_row, start_col))
                continue
            
            raise SyntaxError(f"Unknown character '{ch}' at {self.row}:{self.col}")
        
        # Close remaining indentation
        while len(self.indent_levels) > 1:
            self.indent_levels.pop()
            self.output.append(CodeToken(TokenKind.DEDENT, '', None, self.row, self.col))
        
        self.output.append(CodeToken(TokenKind.END, '', None, self.row, self.col))
        return self.output
