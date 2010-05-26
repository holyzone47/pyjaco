#! /usr/bin/env python

"""
Python grammar, the AST classes contain those arguments as properties.

module Python version "$Revision: 62047 $"
{
    mod = Module(stmt* body)
        | Interactive(stmt* body)
        | Expression(expr body)

    stmt = FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
          | ClassDef(identifier name, expr* bases, stmt* body, expr *decorator_list)
          | Return(expr? value)

          | Delete(expr* targets)
          | Assign(expr* targets, expr value)
          | AugAssign(expr target, operator op, expr value)

          | Print(expr? dest, expr* values, int nl)

          | For(expr target, expr iter, stmt* body, stmt* orelse)
          | While(expr test, stmt* body, stmt* orelse)
          | If(expr test, stmt* body, stmt* orelse)
          | With(expr context_expr, expr? optional_vars, stmt* body)

          | Raise(expr? type, expr? inst, expr? tback)
          | TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
          | TryFinally(stmt* body, stmt* finalbody)
          | Assert(expr test, expr? msg)

          | Import(alias* names)
          | ImportFrom(identifier module, alias* names, int? level)

          | Exec(expr body, expr? globals, expr? locals)

          | Global(identifier* names)
          | Expr(expr value)
          | Pass | Break | Continue

    expr = BoolOp(boolop op, expr* values)
         | BinOp(expr left, operator op, expr right)
         | UnaryOp(unaryop op, expr operand)
         | Lambda(arguments args, expr body)
         | IfExp(expr test, expr body, expr orelse)
         | Dict(expr* keys, expr* values)
         | ListComp(expr elt, comprehension* generators)
         | GeneratorExp(expr elt, comprehension* generators)
         | Yield(expr? value)
         | Compare(expr left, cmpop* ops, expr* comparators)
         | Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
         | Repr(expr value)
         | Num(object n)
         | Str(string s)

         | Attribute(expr value, identifier attr, expr_context ctx)
         | Subscript(expr value, slice slice, expr_context ctx)
         | Name(identifier id, expr_context ctx)
         | List(expr* elts, expr_context ctx)
         | Tuple(expr* elts, expr_context ctx)

    expr_context = Load | Store | Del | AugLoad | AugStore | Param

    slice = Ellipsis
          | Slice(expr? lower, expr? upper, expr? step)
          | ExtSlice(slice* dims)
          | Index(expr value)

    boolop = And | Or

    operator = Add | Sub | Mult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv

    unaryop = Invert | Not | UAdd | USub

    cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

    comprehension = (expr target, expr iter, expr* ifs)

    excepthandler = ExceptHandler(expr? type, expr? name, stmt* body)

    arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    keyword = (identifier arg, expr value)

    alias = (identifier name, identifier? asname)
}
"""

import ast
import inspect
from optparse import OptionParser

def scope(func):
    func.scope = True
    return func

class JSError(Exception):
    pass

class JS(object):

    name_map = {
        'self'   : 'this',
        'True'   : 'true',
        'False'  : 'false',
        'None'  : 'null',

        'int' : '_int',
        'float' : '_float',

        # ideally we should check, that this name is available:
        'py_builtins' : '___py_hard_to_collide',
    }

    builtin = set([
        'NotImplementedError',
        'ZeroDivisionError',
        'AssertionError',
        'AttributeError',
        'RuntimeError',
        'ImportError',
        'TypeError',
        'ValueError',
        'NameError',
        'IndexError',
        'KeyError',
        'StopIteration',

        '_int',
        '_float',
        'max',
        'min',
        'sum',
    ])

    bool_op = {
        'And'    : '&&',
        'Or'     : '||',
    }

    unary_op = {
        'Invert' : '~',
        'Not'    : '!',
        'UAdd'   : '+',
        'USub'   : '-',
    }

    binary_op = {
        'Add'    : '+',
        'Sub'    : '-',
        'Mult'   : '*',
        'Div'    : '/',
        'Mod'    : '%',
        'LShift' : '<<',
        'RShift' : '>>',
        'BitOr'  : '|',
        'BitXor' : '^',
        'BitAnd' : '&',
    }

    comparison_op = {
            'Eq'    : "==",
            'NotEq' : "!=",
            'Lt'    : "<",
            'LtE'   : "<=",
            'Gt'    : ">",
            'GtE'   : ">=",
            'Is'    : "===",
            'IsNot' : "is not", # Not implemented yet
        }

    def __init__(self):
        self.dummy = 0
        self.classes = ['dict', 'list', 'tuple']
        # This is the name of the class that we are currently in:
        self._class_name = None

        # This lists all variables in the local scope:
        self._scope = []
        self._classes = {'object':None}
        #~ self._classes = {}

    def new_dummy(self):
        dummy = "__dummy%d__" % self.dummy
        self.dummy += 1
        return dummy

    def name(self, node):
        return node.__class__.__name__

    def get_bool_op(self, node):
        return self.bool_op[node.op.__class__.__name__]

    def get_unary_op(self, node):
        return self.unary_op[node.op.__class__.__name__]

    def get_binary_op(self, node):
        return self.binary_op[node.op.__class__.__name__]

    def get_comparison_op(self, node):
        return self.comparison_op[node.__class__.__name__]

    #This python code taken from pypy:
    #License for files in the pypy/ directory 
    #==================================================
    #
    #Except when otherwise stated (look for LICENSE files in directories or
    #information at the beginning of each file) all software and
    #documentation in the 'pypy' directories is licensed as follows: 
    #
    #    The MIT License
    #
    #    Permission is hereby granted, free of charge, to any person 
    #    obtaining a copy of this software and associated documentation 
    #    files (the "Software"), to deal in the Software without 
    #    restriction, including without limitation the rights to use, 
    #    copy, modify, merge, publish, distribute, sublicense, and/or 
    #    sell copies of the Software, and to permit persons to whom the 
    #    Software is furnished to do so, subject to the following conditions:
    #
    #    The above copyright notice and this permission notice shall be included 
    #    in all copies or substantial portions of the Software.
    #
    #    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
    #    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
    #    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
    #    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
    #    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
    #    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
    #    DEALINGS IN THE SOFTWARE.
    #
    #
    #PyPy Copyright holders 2003-2010
    #----------------------------------- 
    #
    #Except when otherwise stated (look for LICENSE files or information at
    #the beginning of each file) the files in the 'pypy' directory are each
    #copyrighted by one or more of the following people and organizations:    
    #
    #    Armin Rigo
    #    Maciej Fijalkowski
    #    Carl Friedrich Bolz
    #    Samuele Pedroni
    #    Antonio Cuni
    #    Michael Hudson
    #    Christian Tismer
    #    Holger Krekel
    #    Eric van Riet Paap
    #    Richard Emslie
    #    Anders Chrigstrom
    #    Amaury Forgeot d Arc
    #    Aurelien Campeas
    #    Anders Lehmann
    #    Niklaus Haldimann
    #    Seo Sanghyeon
    #    Leonardo Santagada
    #    Lawrence Oluyede
    #    Jakub Gustak
    #    Guido Wesdorp
    #    Benjamin Peterson
    #    Alexander Schremmer
    #    Niko Matsakis
    #    Ludovic Aubry
    #    Alex Martelli
    #    Toon Verwaest
    #    Stephan Diehl
    #    Adrien Di Mascio
    #    Stefan Schwarzer
    #    Tomek Meka
    #    Patrick Maupin
    #    Jacob Hallen
    #    Laura Creighton
    #    Bob Ippolito
    #    Camillo Bruni
    #    Simon Burton
    #    Bruno Gola
    #    Alexandre Fayolle
    #    Marius Gedminas
    #    Guido van Rossum
    #    Valentino Volonghi
    #    Adrian Kuhn
    #    Paul deGrandis
    #    Gerald Klix
    #    Wanja Saatkamp
    #    Anders Hammarquist
    #    Oscar Nierstrasz
    #    Eugene Oden
    #    Lukas Renggli
    #    Guenter Jantzen
    #    Dinu Gherman
    #    Bartosz Skowron
    #    Georg Brandl
    #    Ben Young
    #    Jean-Paul Calderone
    #    Nicolas Chauvat
    #    Rocco Moretti
    #    Michael Twomey
    #    boria
    #    Jared Grubb
    #    Olivier Dormond
    #    Stuart Williams
    #    Jens-Uwe Mager
    #    Justas Sadzevicius
    #    Mikael Schonenberg
    #    Brian Dorsey
    #    Jonathan David Riehl
    #    Beatrice During
    #    Elmo Mantynen
    #    Andreas Friedge
    #    Alex Gaynor
    #    Anders Qvist
    #    Alan McIntyre
    #    Bert Freudenberg
    #
    #    Heinrich-Heine University, Germany 
    #    Open End AB (formerly AB Strakt), Sweden
    #    merlinux GmbH, Germany 
    #    tismerysoft GmbH, Germany 
    #    Logilab Paris, France 
    #    DFKI GmbH, Germany 
    #    Impara, Germany
    #    Change Maker, Sweden 
    #
    def mro(self, cls):
        order = []
        if cls == 'object':return ['object']
        orderlists = [self.mro(base.id) for base in self._classes[cls].bases if base]
        orderlists.append([cls] + list(c.id for c in self._classes[cls].bases if c))
        while orderlists:
            for candidatelist in orderlists:
                candidate = candidatelist[0]
                if self.blockinglist(candidate, orderlists) is None:
                    break    # good candidate
            else:
                self.mro_error(orderlists)  # no candidate found
            assert candidate not in order
            order.append(candidate)
            for i in range(len(orderlists)-1, -1, -1):
                if orderlists[i][0] == candidate:
                    del orderlists[i][0]
                    if len(orderlists[i]) == 0:
                        del orderlists[i]
        #~ order.append('object')
        return order

    def blockinglist(self,candidate, orderlists):
        for lst in orderlists:
            if candidate in lst[1:]:
                return lst
        return None  # good candidate

    def mro_error(self,orderlists):
        cycle = []
        candidate = orderlists[0][0]
        while candidate not in cycle:
            cycle.append(candidate)
            nextblockinglist = self.blockinglist(candidate, orderlists)
            candidate = nextblockinglist[0]
        # avoid the only use of list.index in the PyPy code base:
        i = 0
        for c in cycle:
            if c == candidate:
                break
            i += 1
        del cycle[:i]
        cycle.append(candidate)
        cycle.reverse()
        #~ names = [cls.__name__ for cls in cycle]
        raise TypeError, "Cycle among base classes: " + ' < '.join(cycle)

    def mronames(self,cls):
        #~ names = [cls.__name__ for cls in mro(cls)]
        #~ return names
        return self.mro(cls)

    def visit(self, node, scope=None):
        try:
            visitor = getattr(self, 'visit_' + self.name(node))
        except AttributeError:
            raise JSError("syntax not supported (%s)" % node)

        if hasattr(visitor, 'statement'):
            return visitor(node, scope)
        else:
            return visitor(node)

    def indent(self, stmts):
        return [ "    " + stmt for stmt in stmts ]

    def visit_Module(self, node):
        module = []

        for stmt in node.body:
            module.extend(self.visit(stmt))

        return module

    @scope
    def visit_FunctionDef(self, node):
        is_static = False
        is_javascript = False
        if node.decorator_list:
            if len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name) and \
                    node.decorator_list[0].id == "JavaScript":
                is_javascript = True # this is our own decorator
            elif self._class_name and \
                    len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name) and \
                    node.decorator_list[0].id == "staticmethod":
                is_static = True
            else:
                raise JSError("decorators are not supported")

        # XXX: disable $def for now, because it doesn't work in IE:
        #if self._class_name:
        if 1:
            if node.args.vararg is not None:
                raise JSError("star arguments are not supported")

            if node.args.kwarg is not None:
                raise JSError("keyword arguments are not supported")

            if node.decorator_list and not is_static and not is_javascript:
                raise JSError("decorators are not supported")

            defaults = [None]*(len(node.args.args) - len(node.args.defaults)) + node.args.defaults

            js_args = []
            js_defaults = []
            self._scope = [arg.id for arg in node.args.args]

            for arg, default in zip(node.args.args, defaults):
                if not isinstance(arg, ast.Name):
                    raise JSError("tuples in argument list are not supported")

                js_args.append(arg.id)

                if default is not None:
                    js_defaults.append("%(id)s = typeof(%(id)s) != 'undefined' ? %(id)s : %(def)s;\n" % { 'id': arg.id, 'def': self.visit(default) })

            if self._class_name:
                prep = "_%s.prototype.%s = function(" % \
                        (self._class_name, node.name)
                if not is_static:
                    if not (js_args[0] == "self"):
                        raise NotImplementedError("The first argument must be 'self'.")
                    del js_args[0]
            else:
                prep = "function %s(" % node.name
            js = [prep + ", ".join(js_args) + ") {"]

            js.extend(self.indent(js_defaults))

            for stmt in node.body:
                js.extend(self.indent(self.visit(stmt)))

            js.append('}')

            #If method is static, we also add it directly to the class
            if is_static:
                js.append("%s.%s = _%s.prototype.%s;" % \
                        (self._class_name, node.name, self._class_name, node.name))

            self._scope = []
            return js
        else:
            defaults = [None]*(len(node.args.args) - len(node.args.defaults)) + node.args.defaults

            args = []
            defaults2 = []
            for arg, default in zip(node.args.args, defaults):
                if not isinstance(arg, ast.Name):
                    raise JSError("tuples in argument list are not supported")
                if default:
                    defaults2.append("%s: %s" % (arg.id, self.visit(default)))
                args.append(arg.id)
            defaults = "{" + ", ".join(defaults2) + "}"
            args = ", ".join(args)
            js = ["var %s = $def(%s, function(%s) {" % (node.name,
                defaults, args)]
            self._scope = [arg.id for arg in node.args.args]
            for stmt in node.body:
                js.extend(self.indent(self.visit(stmt)))
            return js + ["});"]

    @scope
    def visit_ClassDef(self, node):
        js = []
        bases = [self.visit(n) for n in node.bases]
        assert len(bases) >= 1
        bases = ", ".join(bases)
        class_name = node.name
        #self._classes remembers all classes defined
        self._classes[class_name] = node
        js.append("function %s() {" % class_name)
        js.append("    t = new _%s();" % class_name)
        js.append("    _%s.prototype.__init__.apply(t,arguments);" % class_name)
        js.append("    return t;")
        js.append("}")
        js.append("function _%s() {" % class_name)
        js.append("}")
        js.append("_%s.__name__ = '%s';" % (class_name, class_name))
        js.append("_%s.prototype.__class__ = _%s;" % (class_name, class_name))
        js.append("_%s.prototype.toString = _iter.prototype.toString;" % \
                (class_name))
        from ast import dump
        methods = []
        all_attributes = set()
        self._class_name = class_name
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                methods.append(stmt)
                all_attributes.add(stmt.name)
            if isinstance(stmt, ast.Assign):
                value = self.visit(stmt.value)
                for t in stmt.targets:
                    all_attributes.add(t.id )
                    var = self.visit(t)
                    js.append("%s.%s = %s;" % (class_name, var, value))
                    js.append("_%s.prototype.%s = %s.%s;" % (class_name, var, class_name, var))
            else:
                js.extend(self.visit(stmt))
        self._class_name = None

        methods_names = [m.name for m in methods]
        if not "__init__" in methods_names:
            # if the user didn't define __init__(), we have to add it ourselves
            # because we call it from the constructor above
            js.append("_%s.prototype.__init__ = function() {" % class_name)
            js.append("}")

        #TODO: take care of super keyword
        #~ print self.mro(class_name)
        for cls in self.mro(class_name)[1:-1]:
            base_node = self._classes[cls]
            for stmt in base_node.body:
                if isinstance(stmt, ast.FunctionDef) and not stmt.name in all_attributes:
                    all_attributes.add(stmt.name)
                    js.append("_%s.prototype.%s = _%s.prototype.%s;" % (class_name, stmt.name, cls, stmt.name))
                    if len(stmt.decorator_list) == 1 and \
                    isinstance(stmt.decorator_list[0], ast.Name) and \
                    stmt.decorator_list[0].id == "staticmethod":
                        js.append("%s.%s = _%s.prototype.%s;" % (class_name, stmt.name, cls, stmt.name))
                elif isinstance(stmt, ast.Assign):
                    for t in stmt.targets:
                        if not t.id in all_attributes:
                            all_attributes.add(t.id)
                            js.append("_%s.prototype.%s = %s.%s;" % (class_name, t.id, cls, t.id))

        return js

    def visit_Return(self, node):
        if node.value is not None:
            return ["return %s;" % self.visit(node.value)]
        else:
            return ["return;"]

    def visit_Delete(self, node):
        return node

    @scope
    def visit_Assign(self, node):
        assert len(node.targets) == 1
        target = node.targets[0]
        #~ if self._class_name:
            #~ target = self._class_name + '.' + target
        value = self.visit(node.value)
        if isinstance(target, (ast.Tuple, ast.List)):
            js = ["var __dummy%d__ = %s;" % (self.dummy, value)]

            for i, target in enumerate(target.elts):
                var = self.visit(target)
                declare = ""
                if isinstance(target, ast.Name):
                    if not (var in self._scope):
                        self._scope.append(var)
                        declare = "var "
                js.append("%s%s = __dummy%d__.__getitem__(%d);" % (declare,
                    var, self.dummy, i))

            self.dummy += 1
        elif isinstance(target, ast.Subscript):
            js = ["%s.__setitem__(%s, %s);" % (self.visit(target.value),
                self.visit(target.slice), value)]
        else:
            var = self.visit(target)
            declare = ""
            if isinstance(target, ast.Name):
                if not (var in self._scope):
                    self._scope.append(var)
                    declare = "var "
            js = ["%s%s = %s;" % (declare, var, value)]
        return js

    def visit_AugAssign(self, node):
        # TODO: Make sure that all the logic in Assign also works in AugAssign
        target = self.visit(node.target)
        value = self.visit(node.value)

        if isinstance(node.op, ast.Pow):
            return ["%s = Math.pow(%s, %s);" % (target, target, value)]
        if isinstance(node.op, ast.FloorDiv):
            return ["%s = Math.floor((%s)/(%s));" % (target, target, value)]

        return ["%s %s= %s;" % (target, self.get_binary_op(node), value)]

    @scope
    def visit_For(self, node):
        if not isinstance(node.target, ast.Name):
            raise JSError("argument decomposition in 'for' loop is not supported")

        js = []

        for_target = self.visit(node.target)
        for_iter = self.visit(node.iter)

        iter_dummy = self.new_dummy()
        orelse_dummy = self.new_dummy()
        exc_dummy = self.new_dummy()

        js.append("var %s = iter(%s);" % (iter_dummy, for_iter))
        js.append("var %s = false;" % orelse_dummy)
        js.append("while (1) {")
        js.append("    var %s;" % for_target)
        js.append("    try {")
        js.append("        %s = %s.next();" % (for_target, iter_dummy))
        js.append("    } catch (%s) {" % exc_dummy)
        js.append("        if (isinstance(%s, py_builtins.StopIteration)) {" % exc_dummy)
        js.append("            %s = true;" % orelse_dummy)
        js.append("            break;")
        js.append("        } else {")
        js.append("            throw %s;" % exc_dummy)
        js.append("        }")
        js.append("    }")

        for stmt in node.body:
            js.extend(self.indent(self.visit(stmt)))

        js.append("}")

        if node.orelse:
            js.append("if (%s) {" % orelse_dummy)

            for stmt in node.orelse:
                js.extend(self.indent(self.visit(stmt)))

            js.append("}")

        return js

    @scope
    def visit_While(self, node):
        js = []

        if not node.orelse:
            js.append("while (%s) {" % self.visit(node.test))
        else:
            orelse_dummy = self.new_dummy()

            js.append("var %s = false;" % orelse_dummy)
            js.append("while (1) {");
            js.append("    if (!(%s)) {" % self.visit(node.test))
            js.append("        %s = true;" % orelse_dummy)
            js.append("        break;")
            js.append("    }")

        for stmt in node.body:
            js.extend(self.indent(self.visit(stmt)))

        js.append("}")

        if node.orelse:
            js.append("if (%s) {" % orelse_dummy)

            for stmt in node.orelse:
                js.extend(self.indent(self.visit(stmt)))

            js.append("}")

        return js

    @scope
    def visit_If(self, node):
        js = ["if (py_builtins.bool(%s)) {" % self.visit(node.test)]

        for stmt in node.body:
            js.extend(self.indent(self.visit(stmt)))

        if node.orelse:
            js.append("} else {")

            for stmt in node.orelse:
                js.extend(self.indent(self.visit(stmt)))

        return js + ["}"]

    @scope
    def _visit_With(self, node):
        pass

    @scope
    def _visit_Raise(self, node):
        pass

    @scope
    def _visit_TryExcept(self, node):
        pass

    @scope
    def _visit_TryFinally(self, node):
        pass

    def visit_Assert(self, node):
        test = self.visit(node.test)

        if node.msg is not None:
            return ["assert(%s, %s);" % (test, self.visit(node.msg))]
        else:
            return ["assert(%s);" % test]

    def _visit_Import(self, node):
        pass

    def _visit_ImportFrom(self, node):
        pass

    def _visit_Exec(self, node):
        pass

    def visit_Global(self, node):
        self._scope.extend(node.names)
        return []

    def visit_Expr(self, node):
        return [self.visit(node.value) + ";"]

    def visit_Pass(self, node):
        return ["/* pass */"]

    def visit_Break(self, node):
        return ["break;"]

    def visit_Continue(self, node):
        return ["continue;"]

    def visit_BoolOp(self, node):
        return self.get_bool_op(node).join([ "(%s)" % self.visit(val) for val in node.values ])

    def visit_UnaryOp(self, node):
        return "%s(%s)" % (self.get_unary_op(node), self.visit(node.operand))

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Pow):
            return "Math.pow(%s, %s)" % (left, right)
        if isinstance(node.op, ast.FloorDiv):
            return "Math.floor((%s)/(%s))" % (left, right)

        return "(%s)%s(%s)" % (left, self.get_binary_op(node), right)

    def visit_Compare(self, node):
        assert len(node.ops) == 1
        assert len(node.comparators) == 1
        op = node.ops[0]
        comp = node.comparators[0]
        if isinstance(op, ast.In):
            return "%s.__contains__(%s)" % (
                    self.visit(comp),
                    self.visit(node.left),
                    )
        elif isinstance(op, ast.NotIn):
            return "!(%s.__contains__(%s))" % (
                    self.visit(comp),
                    self.visit(node.left),
                    )
        elif isinstance(op, ast.Eq):
            return "py_builtins.eq(%s, %s)" % (
                    self.visit(node.left),
                    self.visit(comp),
                    )
        elif isinstance(op, ast.NotEq):
            #In fact, we'll have to override this too:
            return "!(py_builtins.eq(%s, %s))" % (
                    self.visit(node.left),
                    self.visit(comp),
                    )
        else:
            return "%s %s %s" % (self.visit(node.left),
                    self.get_comparison_op(op),
                    self.visit(comp)
                    )

    def visit_Name(self, node):
        id = node.id
        try:
            id = self.name_map[id]
        except KeyError:
            pass

        if id in self.builtin:
            id = "py_builtins." + id;

        return id

    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        def escape(s):
            s = s.replace("\n", "\\n")
            s = s.replace('"', '\\"')
            return s
        return 'str("%s")' % escape(node.s)

    def visit_Call(self, node):
        if node.keywords:
            keywords = []
            for kw in node.keywords:
                keywords.append("%s: %s" % (kw.arg, self.visit(kw.value)))
            keywords = "{" + ", ".join(keywords) + "}"
            js_args = ",".join([ self.visit(arg) for arg in node.args ])
            return "%s.args([%s], %s)" % (self.visit(node.func), js_args,
                    keywords)
        else:
            if node.starargs is not None:
                raise JSError("star arguments are not supported")

            if node.kwargs is not None:
                raise JSError("keyword arguments are not supported")

            js_args = ",".join([ self.visit(arg) for arg in node.args ])

            return "%s(%s)" % (self.visit(node.func), js_args)

    def visit_Raise(self, node):
        assert node.inst is None
        assert node.tback is None
        return ["throw %s;" % self.visit(node.type)]

    def visit_Print(self, node):
        assert node.dest is None
        assert node.nl
        values = [self.visit(v) for v in node.values]
        values = ", ".join(values)
        return ["py_builtins.print(%s);" % values]

    def visit_Attribute(self, node):
        return "%s.%s" % (self.visit(node.value), node.attr)

    def visit_Tuple(self, node):
        els = [self.visit(e) for e in node.elts]
        return "tuple([%s])" % (", ".join(els))

    def visit_Dict(self, node):
        els = ["    tuple([%s, %s])" % (self.visit(k),
            self.visit(v)) for k, v in zip(node.keys, node.values)]
        return "dict(tuple([\n%s\n]))" % (",\n".join(els))

    def visit_List(self, node):
        els = [self.visit(e) for e in node.elts]
        return "list([%s])" % (", ".join(els))

    def visit_Slice(self, node):
        if node.lower and node.upper and node.step:
            return "slice(%s, %s, %s)" % (self.visit(node.lower),
                    self.visit(node.upper), self.visit(node.step))
        if node.lower and node.upper:
            return "slice(%s, %s)" % (self.visit(node.lower),
                    self.visit(node.upper))
        if node.upper and not node.step:
            return "slice(%s)" % (self.visit(node.upper))
        if node.lower and not node.step:
            return "slice(%s, null)" % (self.visit(node.lower))
        if not node.lower and not node.upper and not node.step:
            return "slice(null)"
        raise NotImplementedError("Slice")

    def visit_Subscript(self, node):
        return "%s.__getitem__(%s)" % (self.visit(node.value), self.visit(node.slice))

    def visit_Index(self, node):
        return self.visit(node.value)

def convert_py2js(s):
    """
    Takes Python code as a string 's' and converts this to JavaScript.

    Example:

    >>> convert_py2js("x[3:]")
    'x.__getitem__(slice(3, null));'

    """
    v = JS()
    t = ast.parse(s)
    return "\n".join(v.visit(t))

class JavaScript(object):
    """
    Decorator that you can use to convert methods to JavaScript.

    For example this code::

        @JavaScript
        class TestClass(object):
            def __init__(self):
                alert('TestClass created')
                self.reset()

            def reset(self):
                self.value = 0

            def inc(self):
                alert(self.value)
                self.value += 1

        print str(TestClass)

    prints::

        function TestClass() {
            return new _TestClass();
        }
        function _TestClass() {
            this.__init__();
        }
        _TestClass.__name__ = 'TestClass'
        _TestClass.prototype.__class__ = _TestClass
        _TestClass.prototype.__init__ = function() {
            alert("TestClass created");
            this.reset();
        }
        _TestClass.prototype.reset = function() {
            this.value = 0;
        }
        _TestClass.prototype.inc = function() {
            alert(this.value);
            this.value += 1;
        }

    Alternatively, an equivalent way is to use JavaScript() as a function:

        class TestClass(object):
            def __init__(self):
                alert('TestClass created')
                self.reset()

            def reset(self):
                self.value = 0

            def inc(self):
                alert(self.value)
                self.value += 1

        print str(JavaScript(TestClass))

    If you want to call the original function/class as Python, use the
    following syntax::

        js = JavaScript(TestClass)
        test_class = js() # Python instance of TestClass() will be created
        js_class = str(js) # A string with the JS code

    """

    def __init__(self, obj):
        self._obj = obj
        obj_source = inspect.getsource(obj)
        self._js = convert_py2js(obj_source)

    def __str__(self):
        return self._js

    def __call__(self, *args, **kwargs):
        return self._obj(*args, **kwargs)

def main():
    parser = OptionParser(usage="%prog [options] filename",
        description="Python to JavaScript compiler.")
    parser.add_option("--include-builtins",
            action="store_true", dest="include_builtins",
            default=False, help="include py-builtins.js library in the output")
    options, args = parser.parse_args()
    if len(args) == 1:
        filename = args[0]
        s = open(filename).read()
        builtins = open("py-builtins.js").read()
        js = convert_py2js(s)
        if options.include_builtins:
            print builtins
        print js
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
