
import ast

def make_arg(name: str) -> ast.arg:
    return ast.arg(arg=name, annotation=None, type_comment=None)

def make_empty_dict() -> ast.Dict:
    return ast.Dict(keys=[], values=[])

## target_name = expr
def make_var_assign(target_name: str, expr: ast.AST) -> ast.Assign:
    target = ast.Name(id=target_name, ctx=ast.Store())
    assignment = ast.Assign(targets=[target], 
                            value=expr, 
                            type_comment=None)
    return assignment

## self.target_name = expr
def make_field_assign(target_name: str, expr: ast.AST) -> ast.Assign:
    target = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=target_name, ctx=ast.Store())
    assignment = ast.Assign(targets=[target], 
                            value=expr, 
                            type_comment=None)
    return assignment

## self.target_name
def make_self_field_access(target_name: str) -> ast.Attribute:
    access = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=target_name, ctx=ast.Load())
    return access

## obj['index']
def make_constant_subscript(obj: str, index: str) -> ast.Subscript:
    return ast.Subscript(value=ast.Name(id=obj, ctx=ast.Load()), 
                         slice=ast.Index(value=ast.Constant(value=index, kind=None)), ctx=ast.Load())

## from x import y
def make_import_from(from_module: str, name: str) -> ast.ImportFrom:
    return ast.ImportFrom(module=from_module, 
                          names=[ast.alias(name=name, asname=None)], 
                          level=0)

## [constant1, constant2, ...]
def make_constant_list(elements) -> ast.List:
    element_asts = [ast.Constant(value=el) for el in elements]
    return ast.List(elts=element_asts, ctx=ast.Load())

    
def call_func_name(call) -> str:
    return call.func.id

def call_func_args(call) -> ast.arguments:
    return call.args

def expr_constant_value(expr):
    return expr.value

