"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer

KEYWORD = "keyword"
IDENTIFIER = "identifier"
SYMBOL = "symbol"
INT_CONSTANT = "integerConstant"
STR_CONST = "stringConstant"
INDENTATION = "  "

CLASS_VAR_DEC = "class_var_dec"
SUBROUTINE_DECLARATION = "subroutine_dec"
VAR_DEC = "var_dec"
STATEMENT = "statement"

TERM_INT = "integerConstant"
TERM_STR = "stringConstant"
TERM_KEYWORD = "keywordConstant"
TERM_VARNAME = "varName"
TERM_VARACCESS = "varName[expression]"
TERM_SUBROUTINE = "subroutineCall"
TERM_EXPRESSION = "(expression)"
TERM_UNARY_TERM = "unaryOp term"
WRONG = "wrong"

# compile statement and compile expression need look ahead, so no need advance after call, we will call advance inside
# maybe all function no need advance after call, we can put inside, --> optimise
# all call line can be replaced with compile line --> optimise

# used when need to decide the type to next structure
def structure_type(keyword):
    if keyword in {"static", "field"}:
        return CLASS_VAR_DEC
    if keyword in {"constructor", "function", "method"}:
        return SUBROUTINE_DECLARATION
    if keyword in {"var"}:
        return VAR_DEC
    if keyword in {"let", "if", "while", "do", "return", "else"}:
        return STATEMENT
    else:
        return WRONG


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream
        self.nested_number = 0
        pass

    def advance(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
        else:
            print("no more tokens")

    # integrated write line function
    # from compile_var_dec and below it uses compile_line instead of write line, if time permits I will change the above
    def compile_line(self):
        self.write_indentation()
        label = self.get_token_string_type()[1]
        name = self.get_token_string_type()[0]
        self.output.write("<{}> {} </{}>\n".format(label, name, label))

    def write_tag(self, tag_name, start):
        self.write_indentation()
        if start:
            self.output.write("<{}>\n".format(tag_name))
        else:
            self.output.write("</{}>\n".format(tag_name))

    def write_indentation(self):
        self.output.write("{}".format(self.nested_number * INDENTATION))

    def is_binary_operation(self):
        operations = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        return self.tokenizer.token_type() == SYMBOL and self.tokenizer.symbol() in operations

    # return string, type
    def get_token_string_type(self):
        if self.tokenizer.token_type() == KEYWORD:
            return self.tokenizer.keyword(), KEYWORD
        if self.tokenizer.token_type() == SYMBOL:
            return self.tokenizer.symbol(), SYMBOL
        if self.tokenizer.token_type() == IDENTIFIER:
            return self.tokenizer.identifier(),IDENTIFIER
        if self.tokenizer.token_type() == INT_CONSTANT:
            return self.tokenizer.int_val(),INT_CONSTANT
        if self.tokenizer.token_type() == STR_CONST:
            return self.tokenizer.string_val(), STR_CONST

    def write_empty_tag(self, tag_name):
        self.write_tag(tag_name, True)
        self.write_tag(tag_name, False)

    # we will not check correctness every time we write line
    # if input correct and our function correct, then there shall be no problem
    # nested number should be added before enter recursive function, responsibility of outside function
    # but in general no need to call it outside, because the <tag> is at the same level of indentation as others

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write_tag("class", True)
        # assume input is correct, then line will be in form:
        # class CLASSNAME { CLASSVARDEC* SUBROUTINEDEC* }
        self.nested_number += 1
        self.advance()
        self.compile_line()
        self.advance()
        self.compile_line()
        self.advance()
        self.compile_line()
        self.advance()

        while self.tokenizer.has_more_tokens():
            if structure_type(self.tokenizer.keyword()) == CLASS_VAR_DEC:
                self.compile_class_var_dec()
            if structure_type(self.tokenizer.keyword()) == SUBROUTINE_DECLARATION:
                self.compile_subroutine()
            # assume no exceptions
            self.advance()
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("class", False)
        pass

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # already at the first line of this block, aka the keyword
        self.write_tag("classVarDec", True)
        self.nested_number += 1
        # write keyword
        self.compile_line()
        self.advance()
        # write type
        self.compile_line()
        self.advance()
        # write varName
        self.compile_line()
        self.advance()
        # if input correct, the token tpe should be symbol, either "," or ";"
        while self.tokenizer.symbol() == ",":
            self.compile_line()
            self.advance()
            # if input is correct, followed by the "," should be a variable name
            self.compile_line()
            self.advance()
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("classVarDec", False)

        pass

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # already at the first line of this block, aka the keyword
        self.write_tag("subroutineDec", True)
        self.nested_number += 1

        self.compile_line()
        self.advance()
        # write return type, could be keyword or identifier
        if self.tokenizer.token_type() == KEYWORD:
            self.compile_line()
        if self.tokenizer.token_type() == IDENTIFIER:
            self.compile_line()
        self.advance()
        # write function name (subroutine name)
        self.compile_line()
        self.advance()
        # if input correct, here should be "("
        self.compile_line()
        self.advance()
        if self.get_token_string_type()[0] == ")":
            self.write_empty_tag("parameterList")
        # write parameter list
        else:
            self.compile_parameter_list()
        # write ")"
        self.compile_line()
        self.advance()
        # write subroutine body
        self.compile_subroutine_body()
        self.nested_number -= 1
        self.write_tag("subroutineDec", False)
        pass

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # already at the first line of parameter list, aka the first argument's type (if exist)
        # if no parameter, then the current line is ")"
        # if input correct, then if token type is symbol, it must be ")"
        self.write_tag("parameterList", True)
        self.nested_number += 1
        # write arg[0] type, if input correct, this must be a key word (int, bool, etc)
        self.compile_line()
        self.advance()
        # write variable name, if input correct, here must be an identifier, input name
        self.compile_line()
        self.advance()
        # if input correct, here must be a symbol, either "," or ")"
        while self.tokenizer.symbol() == ",":
            # write ","
            self.compile_line()
            self.advance()
            # write arg[i] type, if input correct, this must be a key word (int, bool, etc)
            self.compile_line()
            self.advance()
            # write variable name, if input correct, here must be an identifier, input name
            self.compile_line()
            self.advance()
        self.nested_number -= 1
        self.write_tag("parameterList", False)

        pass

    def compile_subroutine_body(self) -> None:
        # if input correct, current line is "{"
        self.write_tag("subroutineBody", True)
        self.nested_number += 1
        self.compile_line()
        self.advance()
        # write var_dec if exist any
        while structure_type(self.tokenizer.keyword()) == VAR_DEC:
            self.compile_var_dec()
            self.advance()
        # if input correct, keyword is either "var" or statements' keyword
        # if my function is correct, now the keyword must b statement
        if structure_type(self.tokenizer.keyword()) == STATEMENT:
            self.compile_statements()
        # if input correct, here should simply be "{', no need for tokenizer.symbol
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("subroutineBody", False)
        pass

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_tag("varDec", True)
        self.nested_number += 1
        # if input correct, tokenizer.keyword == var
        self.compile_line()
        self.advance()
        # write type
        self.compile_line()
        self.advance()
        # write varName
        self.compile_line()
        self.advance()
        # now if input correct, it must be a symbol, "," or ";"
        while self.tokenizer.symbol() == ",":
            # write symbol ","
            self.compile_line()
            self.advance()
            # write varName
            self.compile_line()
            self.advance()
        # it must be ";"
        # write ";"
        self.compile_line()

        self.nested_number -= 1
        self.write_tag("varDec", False)

        pass

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # so for in the caller's level, after every call of compile_statment, no need to call advance()
        # my implementation might include the case {}
        self.write_tag("statements", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement

        while structure_type(self.get_token_string_type()[0]) == STATEMENT:
            if self.tokenizer.keyword() == "let":
                self.compile_let()
            if self.tokenizer.keyword() == "if":
                self.compile_if()
            if self.tokenizer.keyword() == "while":
                self.compile_while()
            if self.tokenizer.keyword() == "do":
                self.compile_do()
            if self.tokenizer.keyword() == "return":
                self.compile_return()

        self.advance()
        # because of my advance logic, else statement will be handled specially
        # assume input correct, no need to check if the else is followed by an if
        if self.tokenizer.token_type() == KEYWORD and self.tokenizer.keyword() == "else":
            self.compile_else()
            return
        self.nested_number -= 1
        self.write_tag("statements", False)
        pass

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_tag("doStatement", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
        # write "do"
        self.compile_line()
        self.advance()
        # now the line should be the first word of a subroutine call
        # note! compile_subroutine is for subroutine declaration, not for subroutine call
        self.compile_subroutine_call()
        self.advance()
        # write ";"
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("doStatement", False)
        pass

    def compile_subroutine_call(self) -> None:
        # current line is subroutine's name or (className|varName)
        self.compile_line()
        self.advance()
        # now use subroutine call a to take care or the rest?
        # subroutine call a will look ahead so subroutine call will also look ahead
        if self.get_token_string_type()[0] == "(":
            self.handle_subroutine_call_a()
        elif self.get_token_string_type()[0] == ".":
            self.handle_subroutine_call_b()




    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        # letStatement

        self.write_tag("letStatement", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
        # write "let"
        self.compile_line()
        self.advance()
        # write varName
        self.compile_line()
        self.advance()
        # here the token type must be a symbol, either "[" or "="
        if self.tokenizer.token_type() == "[":
            # write "["
            self.compile_line()
            self.advance()
            # write expression
            self.compile_expression()
            # write "]"
            self.compile_line()
            self.advance()
        # write "="
        self.compile_line()
        self.advance()
        # write expression
        self.compile_expression()
        # write ";"
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("letStatement", False)
        pass

    def compile_while(self) -> None:
        """Compiles a while statement."""

        self.write_tag("whileStatement", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
        # write "while"
        self.compile_line()
        self.advance()
        # write "("
        self.compile_line()
        self.advance()
        # write expression
        self.compile_expression()
        # write ")"
        self.compile_line()
        self.advance()
        # write "{"
        self.compile_line()
        self.advance()
        # write statements
        self.compile_statements()
        # write "}"
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("whileStatement", False)
        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write_tag("returnStatement", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
        # write return
        self.compile_line()
        self.advance()
        # if there is expression, then tokenType is keyword, else it's symbol
        # if it's not synbol, then it's keyword
        if self.tokenizer.token_type() != SYMBOL:
            self.compile_expression()
        # write ";"
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("returnStatement", False)
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # there might be a else followed by if, but if we advance to next line, we will mess up all the advance logic
        # so the else statement will be handeled in the call compile_statments level (2 levels above)
        # if there's an else, it must be followed an if
        self.write_tag("ifStatement", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
        # write "if"
        self.compile_line()
        self.advance()
        # write "("
        self.compile_line()
        self.advance()
        # write expression
        self.compile_expression()
        # write ")"
        self.compile_line()
        self.advance()
        # write "{"
        self.compile_line()
        self.advance()
        # write statements
        self.compile_statements()
        # write "}"
        self.compile_line()
        self.nested_number -= 1
        self.write_tag("ifStatement", False)
        pass

    def compile_else(self):
        # if there's an else, then now we are at the line of else
        # write "else"
        self.compile_line()
        self.advance()
        # write "{"
        self.compile_line()
        self.advance()
        # write statements
        self.compile_statements()
        # write "}"
        self.compile_line()
        self.advance()

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write_tag("expression", True)
        self.nested_number += 1
        # now we atr the first line of term
        self.compile_term()
        # handle term will look ahead
        # if this input correct, if there's (op term), then we keep compile
        # if there is something else, it is no longer expression anymore
        # the term is not possible to be unary
        while self.is_binary_operation():
            # print "op"
            self.compile_line()
            self.advance()
            # compile term
            self.compile_term()

        # after the compile expression, the current line is at the first line of next syntactic block
        self.nested_number -= 1
        self.write_tag("expression", False)

        pass

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write_tag("term", True)
        self.nested_number += 1
        # now we are at the first line of term
        # look ahead
        first_var = self.get_token_string_type()[0]
        first_var_type = self.get_token_string_type()[1]
        self.compile_line()
        self.advance()
        # now points at the second line
        second_var = self.get_token_string_type()[0]
        # at end of call, the current line is at the  
        # now classify
        if first_var_type == INT_CONSTANT:
            self.handle_int_const()
        elif first_var_type == STR_CONST:
            self.handle_str_const()
        # if it's a keyword, then the type is keyword constant?
        elif first_var_type == KEYWORD:
            self.handle_keyword_const()
        elif first_var_type == IDENTIFIER:
            if second_var == "[":
                self.handle_var_expression()
            elif second_var == "(":
                self.handle_subroutine_call_a()
            elif second_var == ".":
                self.handle_subroutine_call_b()
            # if input correct, else must be term
            else:
                self.handle_var()
        elif first_var_type == SYMBOL:
            if first_var == "(":
                self.handle_expression()
            # else it must be an unaryOperation
            else:
                self.handle_op_term()

        # after the compile expression, the current line is at the first line of next syntactic block
        self.nested_number -= 1
        self.write_tag("term", False)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_tag("expressionList", True)
        self.nested_number += 1
        # currently at the first line of expression
        # if there's no expression, this method should not be called
        self.compile_expression()
        while self.get_token_string_type()[0] == ",":
            self.compile_line()
            self.advance()
            self.compile_expression()
        self.nested_number -= 1
        self.write_tag("expressionList", False)
        pass

    def handle_int_const(self):
        pass

    def handle_str_const(self):
        pass

    def handle_keyword_const(self):
        pass

    def handle_var_expression(self):
        # current line is at "["
        self.compile_line()
        self.advance()
        self.compile_expression()
        # compile expression looked ahead
        # current line is "]"
        self.compile_line()
        self.advance()
        pass

    # handle one kind of (partial) subroutine call
    def handle_subroutine_call_a(self):
        # already written the subroutine name
        # now write "("
        self.compile_line()
        self.advance()
        # if next line is ")", then the expression list is empty
        # else it's an expression list
        if self.get_token_string_type()[0] != ")":
            self.compile_expression_list()
        else:
            self.write_empty()
        # compile expression list will look ahead
        # write ")"
        self.compile_line()
        self.advance()
        pass

    def handle_var(self):
        pass

    def handle_expression(self):
        # at the first line of expression
        self.compile_expression()
        # already at line after expression
        # this line should be ")"
        # write ")"
        self.compile_line()
        self.advance()
        pass

    def handle_op_term(self):
        # op already written
        # at the first line of a term
        self.compile_term()
        pass

    def handle_subroutine_call_b(self):
        # (className| varName) already written, current line is "."
        # write "."
        self.compile_line()
        self.advance()
        # current line is subroutine name
        # can be replaced with compile subroutine
        self.compile_line()
        self.advance()
        # whats lest the the rest of subroutine call
        self.handle_subroutine_call_a()
        pass



