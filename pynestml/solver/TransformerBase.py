#
# TransformerBase.py
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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
import re as re


class TransformerBase(object):
    """
    This class contains several methods as used to adjust a given neuron instance to properties as
    returned by the solver.
    """

    @classmethod
    def addVariablesToInternals(cls, _neuron=None, _declarations=None):
        """
        Adds the variables as stored in the declaration tuples to the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declarations: a list of declaration tuples
        :type _declarations: list((str,str))
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_declarations is not None and isinstance(_declarations, list)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of declarations provided (%s)!' % type(_declarations)
        for declaration in _declarations:
            cls.addVariableToInternals(_neuron, declaration)
        return _neuron

    @classmethod
    def addVariableToInternals(cls, _neuron=None, _declaration=None):
        """
        Adds the variable as stored in the declaration tuple to the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declaration: a single declaration
        :type _declaration: dict
        :return: the neuron extended by the variable
        :rtype: ASTNeuron
        """
        try:
            (var, value) = ASTUtils.getTupleFromSingleDictEntry(_declaration)
            tmp = ModelParser.parseExpression(value)
            vector_variable = ASTUtils.getVectorizedVariable(tmp, _neuron.getScope())
            declaration_string = var + ' real' + (
                '[' + vector_variable.getVectorParameter() + ']'
                if vector_variable is not None and vector_variable.hasVectorParameter() else '') + ' = ' + value
            ast_declaration = ModelParser.parseDeclaration(declaration_string)
            if vector_variable is not None:
                ast_declaration.setSizeParameter(vector_variable.getVectorParameter())
            _neuron.addToInternalBlock(ast_declaration)
            return _neuron
        except:
            raise RuntimeError('Must not fail by construction.')

    @classmethod
    def replaceIntegrateCallThroughPropagation(cls, _neuron=None, _constInput=None, _propagatorSteps=None):
        """
        Replaces all intergrate calls to the corresponding references to propagation.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _constInput: an initial constant value
        :type _constInput: tuple
        :param _propagatorSteps: a list of propagator steps
        :type _propagatorSteps: list(str)
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTBlock import ASTBlock
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_propagatorSteps is not None and isinstance(_propagatorSteps, list)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of propagator steps provided (%s)!' % type(
                _propagatorSteps)
        integrate_call = ASTUtils.getFunctionCall(_neuron.getUpdateBlocks(), PredefinedFunctions.INTEGRATE_ODES)
        # by construction of a valid neuron, only a single integrate call should be there
        if isinstance(integrate_call, list):
            integrate_call = integrate_call[0]
        if integrate_call is not None:
            small_statement = _neuron.getParent(integrate_call)
            assert (small_statement is not None and isinstance(small_statement, ASTSmallStmt))

            block = _neuron.getParent(small_statement)
            assert (block is not None and isinstance(block, ASTBlock))
            for i in range(0, len(block.getStmts())):
                if block.getStmts()[i].equals(small_statement):
                    del block.getStmts()[i]
                    const_tuple = ASTUtils.getTupleFromSingleDictEntry(_constInput)
                    update_statements = list()
                    update_statements.append(ModelParser.parseStmt(const_tuple[0] + " real = " + const_tuple[1]))
                    update_statements += list((ModelParser.parseStmt(prop) for prop in _propagatorSteps))
                    block.getStmts()[i:i] = update_statements
                    break
        else:
            code, message = Messages.getOdeSolutionNotUsed()
            Logger.logMessage(_neuron=_neuron, _code=code, _message=message, _errorPosition=_neuron.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.INFO)
        return _neuron

    @classmethod
    def addVariablesToInitialValues(cls, _neuron=None, _declarationsFile=None):
        """
        Adds a list with declarations to the internals block in the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declarationsFile: a single
        :type _declarationsFile: list(tuple)
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        for decl in _declarationsFile:
            cls.addVariableToInitialValue(_neuron, decl)
        return _neuron

    @classmethod
    def addVariableToInitialValue(cls, _neuron=None, _declaration=None):
        """
        Adds a single declaration to the internals block of the neuron.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :param _declaration: a single key,value tuple
        :type _declaration: tuple
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        try:
            (var, value) = _declaration
            tmp = ModelParser.parseExpression(value)
            vector_variable = ASTUtils.getVectorizedVariable(tmp, _neuron.getScope())
            declaration_string = var + ' real' + (
                '[' + vector_variable.getVectorParameter() + ']'
                if vector_variable is not None and vector_variable.hasVectorParameter() else '') + ' = ' + value
            ast_declaration = ModelParser.parseDeclaration(declaration_string)
            if vector_variable is not None:
                ast_declaration.setSizeParameter(vector_variable.getVectorParameter())
            _neuron.addToInitialValuesBlock(ast_declaration)
            return _neuron
        except:
            raise RuntimeError('Must not fail by construction.')

    @classmethod
    def applyIncomingSpikes(cls, _neuron=None):
        """
        Adds a set of update instructions to the handed over neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        conv_calls = OdeTransformer.get_sumFunctionCalls(_neuron)
        printer = ExpressionsPrettyPrinter()
        spikes_updates = list()
        for convCall in conv_calls:
            shape = convCall.getArgs()[0].getVariable().getCompleteName()
            buffer = convCall.getArgs()[1].getVariable().getCompleteName()
            initialValues = (_neuron.getInitialBlocks().getDeclarations()
            if _neuron.getInitialBlocks() is not None else list())
            for astDeclaration in initialValues:
                for variable in astDeclaration.getVariables():
                    if re.match(shape + "[\']*", variable.getCompleteName()) or re.match(shape + '__[\\d]+$',
                                                                                         variable.getCompleteName()):
                        assignment = ModelParser.parseAssignment(
                            variable.getCompleteName() + " += " + buffer + " * " + printer.printExpression(
                                astDeclaration.getExpression()))
                        spikes_updates.append(assignment)
        for update in spikes_updates:
            cls.addAssignmentToUpdateBlock(update, _neuron)
        return _neuron

    @classmethod
    def addAssignmentToUpdateBlock(cls, _assignment=None, _neuron=None):
        """
        Adds a single assignment to the end of the update block of the handed over neuron.
        :param _assignment: a single assignment
        :type _assignment: ASTAssignment
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTAssignment import ASTAssignment
        from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of assignment provided (%s)!' % type(_assignment)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        small_stmt = ASTSmallStmt(_assignment=_assignment, _sourcePosition=ASTSourcePosition.getAddedSourcePosition())
        _neuron.getUpdateBlocks().getBlock().getStmts().append(small_stmt)
        return _neuron

    @classmethod
    def addDeclarationToUpdateBlock(cls, _declaration=None, _neuron=None):
        """
        Adds a single declaration to the end of the update block of the handed over neuron.
        :param _declaration:
        :type _declaration: ASTDeclaration
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of declaration provided (%s)!' % type(_declaration)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        small_stmt = ASTSmallStmt(_declaration=_declaration, _sourcePosition=ASTSourcePosition.getAddedSourcePosition())
        _neuron.getUpdateBlocks().getBlock().getStmts().append(small_stmt)
        return _neuron

    @classmethod
    def computeShapeStateVariablesWithInitialValues(cls, _solverOutput=None):
        """
        Computes a set of state variables with the corresponding set of initial values from the given solver output.
        :param _solverOutput: a single solver output file
        :type _solverOutput: SolverOutput
        :return: a list of variable initial value tuple as strings
        :rtype: tuple
        """
        from pynestml.solver.SolverOutput import SolverOutput
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of solver output provided (%s)!' % tuple(_solverOutput)
        state_shape_variables_with_initial_values = list()
        for shapeStateVariable in _solverOutput.shape_state_variables:
            for initialValueAsDict in _solverOutput.initial_values:
                for var in initialValueAsDict.keys():
                    if var.endswith(shapeStateVariable):
                        state_shape_variables_with_initial_values.append((shapeStateVariable, initialValueAsDict[var]))
        return state_shape_variables_with_initial_values
