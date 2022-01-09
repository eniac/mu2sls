
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

## obj['index']
def make_constant_subscript(obj: str, index: str) -> ast.Subscript:
    return ast.Subscript(value=ast.Name(id=obj, ctx=ast.Load()), 
                         slice=ast.Index(value=ast.Constant(value=index, kind=None)), ctx=ast.Load())

def call_func_name(call) -> str:
    return call.func.id

def call_func_args(call) -> ast.arguments:
    return call.args

def expr_constant_value(expr):
    return expr.value

