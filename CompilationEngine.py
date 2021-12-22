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


def structure_type(keyword):
    if keyword in {"static", "field"}:
        return CLASS_VAR_DEC
    if keyword in {"constructor", "function", "method"}:
        return SUBROUTINE_DECLARATION


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
        self.nested_number += 1
        self.advance()
        while self.tokenizer.has_more_tokens():
            if structure_type(self.tokenizer.keyword()) == CLASS_VAR_DEC:
                self.compile_class_var_dec()
            if structure_type(self.tokenizer.keyword()) == SUBROUTINE_DECLARATION:
                self.compile_subroutine()
            # assume no exceptions
            self.advance()
        self.nested_number -= 1
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
        self.nested_number += 1
        self.compile_parameter_list()
        self.nested_number -= 1
        self.write_line(SYMBOL, ")")
        # write subroutine body
        self.nested_number += 1
        self.compile_subroutine_body()
        self.nested_number -= 1

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
        self.write_tag("subroutineBody", True)
        self.nested_number += 1

        self.nested_number -= 1
        self.write_tag("subroutineBody", False)
        pass

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        pass

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        pass

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        pass

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        pass

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        pass

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
