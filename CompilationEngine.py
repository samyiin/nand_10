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

VAR_DECLARATION = "var_dec"
SUBROUTINE_DECLARATION = "subroutine_dec"
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
            self.write_indentation()
        else:
            print("no more tokens")

    def write_line(self, label, name ):
        self.output.write("<{}> {} </{}>\n".format(label, name, label))

    def write_indentation(self):
        self.output.write("{}".format(self.nested_number * INDENTATION))

    def structure_type(self, keyword):
        if keyword in {"static", "field"}:
            return VAR_DECLARATION
        if keyword in {"constructor", "function", "method"}:
            return SUBROUTINE_DECLARATION
# we will not check correctness every time we write line
# if input correct and our function correct, then there shall be no problem
    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write("<class>\n")
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
            if self.structure_type(self.tokenizer.keyword()) == VAR_DECLARATION:
                self.compile_class_var_dec()
            if self.structure_type(self.tokenizer.keyword()) == SUBROUTINE_DECLARATION:
                self.compile_subroutine()
            # assume no exceptions
            self.advance()
        self.write_line(SYMBOL, "}")
        self.nested_number += 1
        self.output.write("</class>\n")
        pass

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # already at the first line of this block
        self.output.write("variable declaration")
        pass

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # already at the first line of this block
        self.output.write("subroutine declaration")
        pass

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
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
