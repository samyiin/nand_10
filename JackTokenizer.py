"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    An Xxx .jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of space characters, 
    newline characters, and comments, which are ignored. There are three 
    possible comment formats: /* comment until closing */ , /** API comment 
    until closing */ , and // comment until the line’s end.

    ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’);
    xxx: regular typeface is used for names of language constructs 
    (‘non-terminals’);
    (): parentheses are used for grouping of language constructs;
    x | y: indicates that either x or y can appear;
    x?: indicates that x appears 0 or 1 times;
    x*: indicates that x appears 0 or more times.

    ** Lexical elements **
    The Jack language includes five types of terminal elements (tokens).
    1. keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
    'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false' 
    | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return'
    2. symbol:  '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
    '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    3. integerConstant: A decimal number in the range 0-32767.
    4. StringConstant: '"' A sequence of Unicode characters not including 
    double quote or newline '"'
    5. identifier: A sequence of letters, digits, and underscore ('_') not 
    starting with a digit.


    ** Program structure **
    A Jack program is a collection of classes, each appearing in a separate 
    file. The compilation unit is a class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    class: 'class' className '{' classVarDec* subroutineDec* '}'
    classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    type: 'int' | 'char' | 'boolean' | className
    subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    subroutineName '(' parameterList ')' subroutineBody
    parameterList: ((type varName) (',' type varName)*)?
    subroutineBody: '{' varDec* statements '}'
    varDec: 'var' type varName (',' varName)* ';'
    className: identifier
    subroutineName: identifier
    varName: identifier


    ** Statements **
    statements: statement*
    statement: letStatement | ifStatement | whileStatement | doStatement |
    returnStatement
    letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
    statements '}')?
    whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    doStatement: 'do' subroutineCall ';'
    returnStatement: 'return' expression? ';'


    ** Expressions **
    expression: term (op term)*
    term: integerConstant | stringConstant | keywordConstant | varName | 
    varName '['expression']' | subroutineCall | '(' expression ')' | unaryOp 
    term
    subroutineCall: subroutineName '(' expressionList ')' | (className | 
    varName) '.' subroutineName '(' expressionList ')'
    expressionList: (expression (',' expression)* )?
    op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    unaryOp: '-' | '~' | '^' | '#'
    keywordConstant: 'true' | 'false' | 'null' | 'this'
    """
    KEYWORDS = [
        'class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return' ]
    SYMBOL = ['{','}' , '(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        self.input_lines = input_stream.read().splitlines()
        self.tokens= []
        for line in self.input_lines:
            new_line = self.remove_comments(line)
            if len(new_line) == 0:
                pass
            else:
                sup_line =  self.split_line(new_line)
                sup_line = self.clear_line(sup_line)
                for word in sup_line:
                    if self.there_is_symbol(word):
                        if len(word) == 1:
                            self.tokens.append(word)
                        else:
                            split_word = self.split_word(word)
                            for i in split_word:
                                self.tokens.append(i)
                    else:
                        self.tokens.append(word)
        print(self.tokens)
        self.current_token_index = 0
        self.current_token = self.tokens[0]
        self.out_put = []




    def split_line(self,line):
        split_line = []
        flag_string = False
        flag_end = False
        if '"' in line:
            word = ''
            for l in line:
                # print(l)
                if l == '"':

                    if flag_string is True:
                        flag_end = True
                        word += l
                    split_line.append(word)
                    word = ''
                    flag_string = True
                if l == ' ' and flag_string is False:
                    split_line.append(word)
                    word = ''
                else:
                    word += l
                    if l == '"' and flag_end:
                        flag_string = False
                        flag_end = False
                        word=''
            split_line.append(word)

            if split_line[0][:1] == '\t':
                split_line[0] = split_line[0][1:]

            return split_line
        else:
            return line.split()




    def split_word(self,sentens):
        split_words = []
        word = ''
        for i in sentens:
            if i in self.SYMBOL:
                if word != '':
                    split_words.append(word)
                split_words.append(i)
                word = ''
            else:
                word += i
        if word!='':
            split_words.append(word)
        return split_words
    def there_is_symbol(self,word):

        for sym in self.SYMBOL:
            if sym in word:
                return True
        else:
            return False

    def remove_comments(self, line):
        new_line = ''
        if len(line) == 1:
            return line
        for i in range(len(line)-1):
            if line[i]+line[i+1] == '//' or line[i]+line[i+1] == '/*':
                break
            new_line += line[i]
        if new_line != '':
            new_line+= line[-1]

        return new_line
    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        if self.current_token_index >= len(self.tokens):
            return False
        return True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if self.has_more_tokens():
            self.current_token_index+=1
            if self.current_token_index < len(self.tokens):
                self.current_token = self.tokens[self.current_token_index]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.current_token in self.KEYWORDS:
            return 'keyword'

        elif self.current_token in self.SYMBOL:
            return "symbol"

        elif self.current_token.isnumeric() :
            if 0 <= int(self.current_token) <= 32767:
                return 'integerConstant'


        elif '"' in self.current_token:

            return 'stringConstant'
        else:
             return 'identifier'


    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        if self.token_type() == 'keyword':
            return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        if self.token_type() == 'symbol':
            return  self.current_token


    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """

        # Your code goes here!
        if self.token_type() == 'identifier':
            return self.current_token


    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        if self.token_type() == 'integerConstant':
            return int(self.current_token)


    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        if self.token_type() == 'stringConstant':
            return self.current_token

    def clear_line(self, sup_line):
        new_line = []
        for l in sup_line:
            if l!='':
                new_line.append(l)
        return new_line


if __name__ =='__main__':
    input_file = open('Main.jack', 'r')
    j=JackTokenizer(input_file)
    while j.has_more_tokens():
        print('<'+j.token_type()+'> '+j.current_token+' </'+j.token_type()+'>')
        j.advance()
