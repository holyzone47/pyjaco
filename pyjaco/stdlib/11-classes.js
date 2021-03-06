/**
  Copyright 2011-2013 Christian Iversen <chrivers@iversen-net.dk>

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation
  files (the "Software"), to deal in the Software without
  restriction, including without limitation the rights to use,
  copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.
**/

var __inherit = function(cls, name) {

    if (name === undefined) {
        throw __builtins__.PY$TypeError("The function __inherit must get exactly 2 arguments");
    }

    var res = function() {
        var x = res.PY$__create__;
        if (x !== undefined) {
            return res.PY$__create__.apply(null, [res].concat(Array.prototype.slice.call(arguments)));
        } else {
            throw __builtins__.PY$AttributeError("Class " + name + " does not have __create__ method");
        }
    };

    for (var o in cls) {
        res[o] = cls[o];
    }

    res.PY$__name__  = name;
    res.PY$__super__ = cls;
    res.__isclass = true;
    res.__isinstance = false;
    return res;
};

var object = __inherit(null, "object");

__builtins__.PY$object = object;

object.PY$__init__ = function(self) {
};

object.PY$__create__ = function(cls) {
    var args = Array.prototype.slice.call(arguments, 1);
    var obj = function() {
        var x = cls.PY$__call__;
        if (x !== undefined) {
            return cls.PY$__call__.apply(null, [obj].concat(Array.prototype.slice.call(arguments)));
        } else {
            throw __builtins__.PY$AttributeError("Object " + js(cls.PY$__name__) + " does not have __call__ method");
        }
    };

    if (obj.__proto__ === undefined) {
        var x = function() {};
        x.prototype = cls;
        obj = new x();
    } else {
        obj.__proto__ = cls;
    };

    obj.PY$__class__ = cls;
    obj.PY$__super__ = undefined;
    obj.id = prng();
    obj.__isinstance = true;
    obj.__isclass = false;
    obj.PY$__init__.apply({}, [obj].concat(args));
    return obj;
};

$PY.setattr = function(obj, k, v) {
    obj["PY$" + k] = v;
};

$PY.getattr = function(obj, k) {
    var name = "PY$" + k;
    var res;
    var pyclass;
    if ("PY$__getattribute__" in obj) {
        return obj.PY$__getattribute__(obj, k);
    } else if ((res = obj[name]) !== undefined) {
        if (res.PY$__get__ !== undefined) {
            pyclass = obj.PY$__class__;
            if (pyclass) {
                return res.PY$__get__(res, obj, pyclass);
            } else {
                return res.PY$__get__(res, None, obj);
            }
        } else if (typeof res === 'function' && !(res.__isclass || res.__isinstance)) {
            return function() { return res.apply(null, [obj].concat(Array.prototype.slice.call(arguments))); };
        } else {
            if (k === '__name__') {
                return str(res);
            } else {
                return res;
            }
        }
    } else if (obj.PY$__class__ && name in obj.PY$__class__) {
        res = obj.PY$__class__[name];
        if (typeof res === 'function' && obj.__isinstance) {
            return function() { return res.apply(obj.PY$__class__, arguments); };
        } else {
            return res;
        }
    } else if ("PY$__getattr__" in obj) {
        res = obj.PY$__getattr__(obj, k);
        return res;
    }
    throw __builtins__.PY$AttributeError(js(obj.PY$__repr__(obj)) + " does not have attribute '" + js(k) + "'");
};

$PY.delattr = function(obj, k) {
    delete obj["PY$" + k];
};

object.PY$__repr__ = function(self) {
    if (self.PY$__class__) {
        return str("<instance of " + self.PY$__class__.PY$__name__ + " at 0x" + self.id.toString(16) + ">");
    } else if (self.PY$__name__) {
        return str("<type '" + self.PY$__name__ + "'>");
    } else {
        return str("<javascript: " + self + ">");
    }
};

object.PY$__str__ = object.PY$__repr__;

object.PY$__eq__ = function(self, other) {
    return self === other ? True : False;
};

object.PY$__ne__ = function(self, other) {
    return $PY.__not__(self.PY$__eq__(self, other));
};

object.PY$__gt__ = function(self, other) {
    if (self.PY$__class__ === undefined) {
        return self.PY$__name__ > other.PY$__name__ ? True : False;
    } else {
        return self.PY$__class__.PY$__name__ > other.PY$__class__.PY$__name__ ? True : False;
    }
};

object.PY$__lt__ = function(self, other) {
    if (other === self) {
        return False;
    } else {
        if (self.PY$__class__ === undefined) {
            return self.PY$__name__ < other.PY$__name__ ? True : False;
        } else {
            return self.PY$__class__.PY$__name__ < other.PY$__class__.PY$__name__ ? True : False;
        }
    }
};

object.PY$__ge__ = function(self, other) {
    return self.PY$__lt__(self, other) === False ? True : False;
};

object.PY$__le__ = function(self, other) {
    return self.PY$__gt__(self, other) === False ? True : False;
};

object.PY$__cmp__ = function(self, y) {
    if (self.PY$__gt__(self, y) === True) {
        return $c1;
    } else {
        if (self.PY$__lt__(self, y) === True) {
            return $cn1;
        } else {
            return $c0;
        }
    }
};

object.toString = function() {
    return js(this.PY$__str__(this));
};
