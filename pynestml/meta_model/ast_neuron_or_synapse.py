#
# ast_neuron.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_neuron_body import ASTNeuronBody
from pynestml.meta_model.ast_synapse_body import ASTSynapseBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages

def symbol_by_name(name, symbols):
    """get a symbol from a list of symbols by the given name"""
    for sym in symbols:
        if sym.name == name:
            return sym
    return None

class ASTNeuronOrSynapse(ASTNode):
    """
    This class is used to stuff common to neurons and synapses
    """

    def __init__(self, name, body, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.
        :param name: the name of the neuron.
        :type name: str
        :param body: the body containing the definitions.
        :type body: ASTSynapseBody or ASTNeuronBody
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        :param artifact_name: the name of the file this neuron is contained in
        :type artifact_name: str
        """
        assert isinstance(name, str), \
            '(PyNestML.AST.ASTNeuronOrSynapse) No  or wrong type of neuron name provided (%s)!' % type(name)
        assert isinstance(body, ASTSynapseBody) or isinstance(body, ASTNeuronBody), \
            '(PyNestML.AST.Neuron) No or wrong type of neuron body provided (%s)!' % type(body)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.Neuron) No or wrong type of artifact name provided (%s)!' % type(artifact_name)
        super(ASTNeuronOrSynapse, self).__init__(*args, **kwargs)
        self.name = name
        self.body = body
        self.artifact_name = artifact_name


    def get_name(self):
        """
        Returns the name of the neuron.
        :return: the name of the neuron.
        :rtype: str
        """
        return self.name


    def set_name(self, name):
        """
        Set the name of the node.
        """
        self.name = name


    def get_body(self):
        """
        Return the body of the neuron.
        :return: the body containing the definitions.
        :rtype: ASTSynapseBody or ASTNeuronBody
        """
        return self.body


    def get_artifact_name(self):
        """
        Returns the name of the artifact this neuron has been stored in.
        :return: the name of the file
        :rtype: str
        """
        return self.artifact_name


    def get_functions(self):
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        :rtype: list(ASTFunction)
        """
        ret = list()
        from pynestml.meta_model.ast_function import ASTFunction
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTFunction):
                ret.append(elem)
        return ret


    def get_update_blocks(self):
        """
        Returns a list of all update blocks defined in this body.
        :return: a list of update-block elements.
        :rtype: list(ASTUpdateBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_update_block import ASTUpdateBlock
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTUpdateBlock):
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret


    def get_state_blocks(self):
        """
        Returns a list of all state blocks defined in this body.
        :return: a list of state-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_state:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret


    def get_initial_blocks(self):
        """
        Returns a list of all initial blocks defined in this body.
        :return: a list of initial-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_initial_values:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret


    def get_parameter_blocks(self):
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_parameters:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret


    def get_internals_blocks(self):
        """
        Returns a list of all internals blocks defined in this body.
        :return: a list of internals-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_internals:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret


    def get_equations_blocks(self):
        """
        Returns a list of all equations BLOCKS defined in this body.
        :return: a list of equations-blocks.
        :rtype: list(ASTEquationsBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def get_equations_block(self):
        """
        Returns the unique equations block defined in this body.
        :return: a  equations-block.
        :rtype: ASTEquationsBlock
        """
        return self.get_equations_blocks()

    def remove_equations_block(self):
        # type: (...) -> None
        """
        Deletes all equations blocks. By construction as checked through cocos there is only one there.
        """

        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                self.get_body().get_body_elements().remove(elem)

    def get_initial_values_declarations(self):
        """
        Returns a list of initial values declarations made in this neuron.
        :return: a list of initial values declarations
        :rtype: list(ASTDeclaration)
        """
        initial_values_block = self.get_initial_blocks()
        initial_values_declarations = list()
        if initial_values_block is not None:
            for decl in initial_values_block.get_declarations():
                initial_values_declarations.append(decl)
        return initial_values_declarations

    def get_equations(self):
        """
        Returns all ode equations as defined in this neuron.
        :return list of ode-equations
        :rtype list(ASTOdeEquation)
        """
        from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
        ret = list()
        blocks = self.get_equations_blocks()
        # the get equations block is not deterministic method, it can return a list or a single object.
        if isinstance(blocks, list):
            for block in blocks:
                ret.extend(block.get_ode_equations())
        elif isinstance(blocks, ASTEquationsBlock):
            return blocks.get_ode_equations()
        else:
            return ret

    def get_parameter_symbols(self):
        """
        Returns a list of all parameter symbol defined in the model.
        :return: a list of parameter symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.PARAMETERS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_state_symbols(self):
        """
        Returns a list of all state symbol defined in the model.
        :return: a list of state symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.STATE and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_internal_symbols(self):
        """
        Returns a list of all internals symbol defined in the model.
        :return: a list of internals symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.INTERNALS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_function_symbols(self):
        """
        Returns a list of all function symbols defined in the model.
        :return: a list of function symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
             and (symbol.block_type == BlockType.EQUATION or symbol.block_type == BlockType.INITIAL_VALUES) \
             and symbol.is_function:
                ret.append(symbol)
        return ret

    def get_output_blocks(self):
        """
        Returns a list of all output-blocks defined.
        :return: a list of defined output-blocks.
        :rtype: list(ASTOutputBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_output_block import ASTOutputBlock
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTOutputBlock):
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def is_multisynapse_spikes(self):
        """
        Returns whether this neuron uses multi-synapse spikes.
        :return: True if multi-synaptic, otherwise False.
        :rtype: bool
        """
        buffers = self.get_spike_buffers()
        for iBuffer in buffers:
            if iBuffer.has_vector_parameter():
                return True
        return False

    def get_multiple_receptors(self):
        """
        Returns a list of all spike buffers which are defined as inhibitory and excitatory.
        :return: a list of spike buffers variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for iBuffer in self.get_spike_buffers():
            if iBuffer.is_excitatory() and iBuffer.is_inhibitory():
                if iBuffer is not None:
                    ret.append(iBuffer)
                else:
                    code, message = Messages.get_could_not_resolve(iBuffer.get_symbol_name())
                    Logger.log_message(
                        message=message,
                        code=code,
                        error_position=iBuffer.get_source_position(),
                        log_level=LoggingLevel.ERROR)
        return ret

    def get_parameter_non_alias_symbols(self):
        """
        Returns a list of all variable symbols representing non-function parameter variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.get_parameter_symbols():
            if not param.is_function and not param.is_predefined:
                ret.append(param)
        return ret

    def get_state_non_alias_symbols(self):
        """
        Returns a list of all variable symbols representing non-function state variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.get_state_symbols():
            if not param.is_function and not param.is_predefined:
                ret.append(param)
        return ret

    def get_initial_values_non_alias_symbols(self):
        ret = list()
        for init in self.get_initial_values_symbols():
            if not init.is_function and not init.is_predefined:
                ret.append(init)
        return ret

    def get_internal_non_alias_symbols(self):
        """
        Returns a list of all variable symbols representing non-function internal variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.get_internal_symbols():
            if not param.is_function and not param.is_predefined:
                ret.append(param)

        return ret

    def get_initial_values_symbols(self):
        """
        Returns a list of all initial values symbol defined in the model. Note that the order here is the same as the order by which the symbols are defined in the model: this is important if a particular variable is defined in terms of another (earlier) variable.
        
        :return: a list of initial values symbols.
        :rtype: list(VariableSymbol)
        """

        """from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
             and symbol.block_type == BlockType.INITIAL_VALUES \
             and not symbol.is_predefined:
                ret.append(symbol)
        return ret"""

        iv_syms = []
        symbols = self.get_scope().get_symbols_in_this_scope()
        
        iv_blk = self.get_initial_values_blocks()
        for decl in iv_blk.get_declarations():
            for var in decl.get_variables():
                iv_sym = symbol_by_name(var.get_complete_name(), symbols)
                assert not iv_sym is None, "Symbol by name \"" + var.get_complete_name() + "\" not found in initial values block"
                iv_syms.append(iv_sym)
        #print("Returning syms: " + ", ".join([iv_sym.name for iv_sym in iv_syms]))
        return iv_syms
                
        

    def get_initial_values_blocks(self):
        """
        Returns a list of all initial blocks defined in this body.
        :return: a list of initial-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_initial_values:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def remove_initial_blocks(self):
        """
        Remove all equations blocks
        """
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_initial_values:
                self.get_body().get_body_elements().remove(elem)

    def get_function_initial_values_symbols(self):
        """
        Returns a list of all initial values symbols as defined in the model which are marked as functions.
        :return: a list of symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for symbol in self.get_initial_values_symbols():
            if symbol.is_function:
                ret.append(symbol)
        return ret

    def get_non_function_initial_values_symbols(self):
        """
        Returns a list of all initial values symbols as defined in the model which are not marked as functions.
        :return: a list of symbols
        :rtype:list(VariableSymbol)
        """
        ret = list()
        for symbol in self.get_initial_values_symbols():
            if not symbol.is_function:
                ret.append(symbol)
        return ret

    def is_array_buffer(self):
        """
        This method indicates whether this neuron uses buffers defined vector-wise.
        :return: True if vector buffers defined, otherwise False.
        :rtype: bool
        """
        buffers = self.get_input_buffers()
        for BUFFER in buffers:
            if BUFFER.has_vector_parameter():
                return True
        return False

    def get_parameter_invariants(self):
        """
        Returns a list of all invariants of all parameters.
        :return: a list of rhs representing invariants
        :rtype: list(ASTExpression)
        """
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        ret = list()
        blocks = self.get_parameter_blocks()
        # the get parameters block is not deterministic method, it can return a list or a single object.
        if isinstance(blocks, list):
            for block in blocks:
                for decl in block.get_declarations():
                    if decl.has_invariant():
                        ret.append(decl.get_invariant())
        elif isinstance(blocks, ASTBlockWithVariables):
            for decl in blocks.get_declarations():
                if decl.has_invariant():
                    ret.append(decl.get_invariant())
        return ret

    def add_to_internal_block(self, declaration, index=-1):
        # todo by KP: factor me out to utils
        """
        Adds the handed over declaration the internal block
        :param declaration: a single declaration
        :type declaration: ast_declaration
        """
        if self.get_internals_blocks() is None:
            ASTUtils.create_internal_block(self)
        #print("In ASTNeuron::add_to_internal_block(): decl = " + str(declaration) + ", scope = " + str(self.get_internals_blocks().get_scope()))
        n_declarations = len(self.get_internals_blocks().get_declarations())
        if n_declarations == 0:
            index = 0
        else:
            index = 1 + (index % len(self.get_internals_blocks().get_declarations()))
        self.get_internals_blocks().get_declarations().insert(index, declaration)
        declaration.update_scope(self.get_internals_blocks().get_scope())
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        symtable_vistor = ASTSymbolTableVisitor()
        symtable_vistor.block_type_stack.push(BlockType.INTERNALS)
        declaration.accept(symtable_vistor)
        symtable_vistor.block_type_stack.pop()

    def add_to_initial_values_block(self, declaration):
        # todo by KP: factor me out to utils
        """
        Adds the handed over declaration to the initial values block.
        :param declaration: a single declaration.
        :type declaration: ast_declaration
        """
        #print("In ASTNeuron::add_to_initial_values_block(): decl = " + str(declaration) + ", scope = " + str(self.get_initial_blocks().get_scope()))
        if self.get_initial_blocks() is None:
            ASTUtils.create_initial_values_block(self)
        self.get_initial_blocks().get_declarations().append(declaration)
        declaration.update_scope(self.get_initial_blocks().get_scope())
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        #from pynestml.symbols.variable_symbol import BlockType

        symtable_vistor = ASTSymbolTableVisitor()
        symtable_vistor.block_type_stack.push(BlockType.INITIAL_VALUES)
        declaration.accept(symtable_vistor)
        symtable_vistor.block_type_stack.pop()
        #self.get_initial_blocks().accept(symtable_vistor)
        from pynestml.symbols.symbol import SymbolKind
        assert not declaration.get_variables()[0].get_scope().resolve_to_symbol(declaration.get_variables()[0].get_name(), SymbolKind.VARIABLE) is None
        assert not declaration.get_scope().resolve_to_symbol(declaration.get_variables()[0].get_name(), SymbolKind.VARIABLE) is None

    def add_shape(self, shape):
        # type: (ASTOdeShape) -> None
        """
        Adds the handed over declaration to the initial values block.
        :param shape: a single declaration.
        """
        assert self.get_equations_block() is not None
        self.get_equations_block().get_declarations().append(shape)
        shape.update_scope(self.get_equations_blocks().get_scope())

    """
    The following print methods are used by the backend and represent the comments as stored at the corresponding 
    parts of the neuron definition.
    """

    def print_dynamics_comment(self, prefix=None):
        """
        Prints the dynamic block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_update_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_parameter_comment(self, prefix=None):
        """
        Prints the update block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_parameter_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_state_comment(self, prefix=None):
        """
        Prints the state block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_state_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_internal_comment(self, prefix=None):
        """
        Prints the internal block comment.
        :param prefix: a prefix string
        :type prefix: str
        :return: the corresponding comment.
        :rtype: str
        """
        block = self.get_internals_blocks()
        if block is None:
            return prefix if prefix is not None else ''
        return block.print_comment(prefix)

    def print_comment(self, prefix=None):
        """
        Prints the header information of this neuron.
        :param prefix: a prefix string
        :type prefix: str
        :return: the comment.
        :rtype: str
        """
        ret = ''
        if self.get_comment() is None or len(self.get_comment()) == 0:
            return prefix if prefix is not None else ''
        for comment in self.get_comment():
            ret += (prefix if prefix is not None else '') + comment + '\n'
        return ret

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_body() is ast:
            return self
        elif self.get_body().get_parent(ast) is not None:
            return self.get_body().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTNeuron):
            return False
        return self.get_name() == other.get_name() and self.get_body().equals(other.get_body())

    def get_initial_value(self, variable_name):
        assert type(variable_name) is str

        for decl in self.get_initial_values_blocks().get_declarations():
            for var in decl.variables:
                if var.get_complete_name() == variable_name:
                    return decl.get_expression()

        return None

    def get_shape_by_name(self, shape_name) -> Optional[ASTOdeShape]:
        assert type(shape_name) is str
        shape_name = shape_name.split("__X__")[0]

        # check if defined as a direct function of time
        for decl in self.get_equations_block().get_declarations():
            if type(decl) is ASTOdeShape and shape_name in decl.get_variable_names():
                #print("Is shape " + str(shape_name) + "? YES")
                return decl

        # check if defined for a higher order of differentiation
        for decl in self.get_equations_block().get_declarations():
            if type(decl) is ASTOdeShape and shape_name in [s.replace("$", "__DOLLAR").replace("'", "") for s in decl.get_variable_names()]:
                #print("Is shape " + str(shape_name) + "? YES2")
                return decl

        return None


    def get_all_shapes(self):
        shapes = []
        for decl in self.get_equations_block().get_declarations():
            if type(decl) is ASTOdeShape:
                shapes.append(decl)
        return shapes



