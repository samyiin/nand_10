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
INDENTATION = "    "

CLASS_VAR_DEC = "class_var_dec"
SUBROUTINE_DECLARATION = "subroutine_dec"
VAR_DEC = "var_dec"
STATEMENT = "statement"

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

    def write_line(self, label, name):
        self.write_indentation()
        self.output.write("<{}> {} </{}>\n".format(label, name, label))

    # integrated write line function
    # from compile_var_dec and below it uses compile_line instead of write line, if time permits I will change the above
    def compile_line(self):
        self.write_indentation()
        label = self.tokenizer.token_type()
        name = ""
        if label == KEYWORD:
            name = self.tokenizer.keyword()
        if label == SYMBOL:
            name = self.tokenizer.symbol()
        if label == IDENTIFIER:
            name = self.tokenizer.identifier()
        self.output.write("<{}> {} </{}>\n".format(label, name, label))

    def write_tag(self, tag_name, start):
        self.write_indentation()
        if start:
            self.output.write("<{}>\n".format(tag_name))
        else:
            self.output.write("</{}>\n".format(tag_name))

    def write_indentation(self):
        self.output.write("{}".format(self.nested_number * INDENTATION))

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
        self.write_line(KEYWORD, "class")
        self.advance()
        self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        self.write_line(SYMBOL, "{")

        self.advance()
        while self.tokenizer.has_more_tokens():
            if structure_type(self.tokenizer.keyword()) == CLASS_VAR_DEC:
                self.compile_class_var_dec()
            if structure_type(self.tokenizer.keyword()) == SUBROUTINE_DECLARATION:
                self.compile_subroutine()
            # assume no exceptions
            self.advance()
        self.write_line(SYMBOL, "}")
        self.nested_number -= 1
        self.write_tag("class", False)
        pass

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # already at the first line of this block, aka the keyword
        self.write_tag("classVarDec", True)
        self.nested_number += 1
        # write keyword
        self.write_line(KEYWORD, self.tokenizer.keyword())
        self.advance()
        # write type
        self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        # write varName
        self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        # if input correct, the token tpe should be symbol, either "," or ";"
        while self.tokenizer.symbol() == ",":
            self.write_line(SYMBOL, ",")
            self.advance()
            # if input is correct, followed by the "," should be a variable name
            self.write_line(IDENTIFIER, self.tokenizer.identifier())
            self.advance()
        self.write_line(SYMBOL, ";")
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

        self.write_line(KEYWORD, self.tokenizer.keyword())
        self.advance()
        # write return type, could be keyword or identifier
        if self.tokenizer.token_type() == KEYWORD:
            self.write_line(KEYWORD, self.tokenizer.keyword())
        if self.tokenizer.token_type() == IDENTIFIER:
            self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        # write function name (subroutine name)
        self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        # if input correct, here should be "(", so there is no difference with using tokenizer.symbol
        self.write_line(SYMBOL, "(")
        self.advance()
        # write parameter list
        self.compile_parameter_list()
        self.write_line(SYMBOL, ")")
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
        if self.tokenizer.token_type() == SYMBOL:
            return
        self.write_tag("parameterList", True)
        self.nested_number += 1
        # write arg[0] type, if input correct, this must be a key word (int, bool, etc)
        self.write_line(KEYWORD, self.tokenizer.keyword())
        self.advance()
        # write variable name, if input correct, here must be an identifier, input name
        self.write_line(IDENTIFIER, self.tokenizer.identifier())
        self.advance()
        # if input correct, here must be a symbol, either "," or ")"
        while self.tokenizer.symbol() == ",":
            # write arg[i] type, if input correct, this must be a key word (int, bool, etc)
            self.write_line(KEYWORD, self.tokenizer.keyword())
            self.advance()
            # write variable name, if input correct, here must be an identifier, input name
            self.write_line(IDENTIFIER, self.tokenizer.identifier())
            self.advance()
        self.nested_number -= 1
        self.write_tag("parameterList", False)

        pass

    def compile_subroutine_body(self) -> None:
        # if input correct, current line is "{"
        self.write_tag("subroutineBody", True)
        self.nested_number += 1
        self.write_line(SYMBOL, "{")
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
        self.write_line(SYMBOL, "}")
        self.nested_number -= 1
        self.write_tag("subroutineBody", False)
        pass

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_tag("varDec", True)
        self.nested_number += 1
        # if input correct, tokenizer.keyword == var
        self.write_line(KEYWORD, "var")
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

        self.write_tag("statements", True)
        self.nested_number += 1
        # current line should be the keyword o which kind of statement
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
        pass

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
        # Your code goes here!
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
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass
