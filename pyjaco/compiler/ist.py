######################################################################
##
## Copyright 2013 Christian Iversen <ci@sikkerhed.org>
##
## Permission is hereby granted, free of charge, to any person
## obtaining a copy of this software and associated documentation
## files (the "Software"), to deal in the Software without
## restriction, including without limitation the rights to use,
## copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following
## conditions:
##
## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
## OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
## HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
## WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
## OTHER DEALINGS IN THE SOFTWARE.
##
######################################################################

__all__ = ["ISTNode", "Annotation", "Comment", "Code", "Nop", "Function", "Parameters", "Statement", "Module", "If", "While", "TryExcept", "For", "ForEach", "Raise", "Break", "Continue", "Return", "ClassDef", "Call", "Assign", "BinOp", "Number", "GetAttr", "Name", "String", "TryExcept", "TryFinally", "TryHandler", "Tuple", "List", "AugAssign", "Delete", "BoolOp", "Compare", "GetItem", "Lambda", "UnaryOp", "Dict", "Global", "Yield", "Slice", "Generator", "ListComp", "Comprehension", "Import", "ImportFrom", "IfExp", "Assert", "Var"]

class ISTNode(object):

    _defaults = dict()

    def __init__(self, **attr):
        for x in attr:
            if not x in self._fields:
                raise TypeError("IST node [%s] does not take attribute [%s]" % (self.__class__.__name__, x))
            else:
                setattr(self, x, attr[x])
        for x in self._fields:
            if not hasattr(self, x):
                if x in self._defaults:
                    setattr(self, x, self._defaults[x])
                else:
                    raise TypeError("IST node [%s] requires attribute [%s]" % (self.__class__.__name__, x))


    def str(self, indent = 0):
        i = "  "*indent
        s = "%s%s: " % (i, self.__class__.__name__)
        i += "  "
        f = []
        for k in self._fields:
            v = getattr(self, k)
            if isinstance(v, list):
                s += "\n%s%s [" % (i, k)

                for l in v:
                    s += "\n%s" % (l.str(indent + 2))

                if v == []:
                    s += "]"
                else:
                    s += "\n%s]" % i
            else:
                if isinstance(v, ISTNode):
                    f = "%s = %s" % (k, v.str(indent))
                else:
                    f = "%s = %s" % (k, v)
                s += "\n%s%s" % (i, f)
        return s

## Annotations

class Annotation(ISTNode):
    _fields = ["data"]

class Comment(Annotation):
    _fields = ["comment"]

class Code(ISTNode):
    _fields = []

class Nop(Code):
    _fields = []

class Function(Code):
    _fields = {"name", "params", "body", "decorators"}
    _defaults = dict(decorators = [])

class Parameters(Code):
    _fields = ["args", "defaults", "kwargs", "varargs"]

## Statements

class Statement(Code):
    _fields = []

class Module(Code):
    _fields = ["body"]

class If(Code):
    _fields = ["body", "cond", "orelse"]
    _defaults = dict(orelse = [])

class While(Code):
    _fields = ["body", "cond", "orelse"]
    _defaults = dict(orelse = [])

class TryExcept(Code):
    _fields = ["body", "errorbody"]

class For(Code):
    _fields = ["body", "init", "cond", "incr"]

class ForEach(Code):
    _fields = ["body", "iter", "target", "orelse"]
    _defaults = dict(orelse = [])

class Raise(Code):
    _fields = ["expr"]

class Break(Code):
    _fields = []

class Continue(Code):
    _fields = []

class Return(Code):
    _fields = ["expr"]

class ClassDef(Code):
    _fields = ["body", "name", "bases", "decorators"]
    _defaults = dict(decorators = [])

## Expressions

class Call(Code):
    _fields = ["func", "args", "keywords", "varargs", "kwargs"]
    _defaults = dict(keywords = [], varargs = None, kwargs = None)

class Assign(Code):
    _fields = ["lvalue", "rvalue"]

class BinOp(Code):
    _fields = ["left", "right", "op"]

class Number(Code):
    _fields = ["value"]

class GetAttr(Code):
    _fields = ["base", "attr"]

class Name(Code):
    _fields = ["id"]

class String(Code):
    _fields = ["value"]

class TryExcept(Code):
    _fields = ["body", "handlers", "orelse"]
    _defaults = dict(orelse = [])

class TryFinally(Code):
    _fields = ["body", "finalbody"]

class TryHandler(Code):
    _fields = ["body", "name", "type"]

class Tuple(Code):
    _fields = ["values"]

class List(Code):
    _fields = ["values"]

class AugAssign(Code):
    _fields = ["target", "value", "op"]

class Delete(Code):
    _fields = ["targets"]

class BoolOp(Code):
    _fields = ["values", "op"]

class Compare(Code):
    _fields = ["comps", "ops", "lvalue"]

class GetItem(Code):
    _fields = ["value", "slice"]

class Lambda(Code):
    _fields = ["body", "params", "name"]
    _defaults = dict(name = "")

class UnaryOp(Code):
    _fields = ["op", "lvalue"]

class Dict(Code):
    _fields = ["keys", "values"]

class Global(Code):
    _fields = ["names"]

class Yield(Code):
    _fields = ["value"]

class Slice(Code):
    _fields = ["lower", "upper", "step"]

class Generator(Code):
    _fields = ["expr", "generators"]

class ListComp(Code):
    _fields = ["expr", "generators"]

class Comprehension(Code):
    _fields = ["conds", "iter", "target"]

class Import(Code):
    _fields = ["names"]

class ImportFrom(Code):
    _fields = ["module", "names"]

class IfExp(Code):
    _fields = ["body", "orelse", "cond"]

class Assert(Code):
    _fields = ["msg", "cond"]

class Var(Code):
    _fields = ["name", "expr"]
    _defaults = dict(expr = None)
