import sys

from compiler.service import Service

import ast

from uncompyle6.main import decompile

## TODO: Check ast.unparse in python 3.9
##
## This function takes an AST and saves python_source code in the out_file
def ast_to_source(ast_node, out_file):
    ## TODO: Do we need the filename
    ##
    ## TODO: This is very wasteful, we should not need to first compile to bytecode before deparsing.
    code_object = compile(ast_node, filename="<ast>", mode="exec")

    ## TODO: Do we actually need the bytecode version?
    ##       By default uncompyle should use the interpreter version.
    ##
    ## TODO: It seems that uncompyle does not produce comments in the code,
    ##       meaning that they are lost.
    bytecode_version=None
    with open(out_file, "w") as out_f:
        decompiled_code = decompile(bytecode_version,
                                    code_object,
                                    out=out_f)
    
    ## TODO: I am not sure what this object is and whether we need it
    return decompiled_code

def persistent_object_target_init_ast(persistent_object_name, _persistent_object_init_ast):
    ## TODO: Replace that with the proper descriptor initialization value
    value = ast.Constant(value=1)
    assign_node = ast.Assign(targets=[ast.Name(id=persistent_object_name, ctx=ast.Store())],
                             value=value)
    return assign_node

## TODO: Not sure if this should be a method of Service or a function here
def service_to_ast(service: Service):
    print(service)

    ## TODO: Make sure to fix locations

    ## TODO: For now only work for persistent fields and thrift
    persistent_objects = service.state.persistent_fields
    assignments = []
    for per_obj_name, per_obj_init_ast in persistent_objects.items():
        target_ast = persistent_object_target_init_ast(per_obj_name, per_obj_init_ast)
        assignments.append(target_ast)
    
    body = assignments + service.methods
    
    new_class = ast.ClassDef(name=service.name(),
                             bases=service.bases(),
                             keywords=service.keywords(),
                             body=body,
                             decorator_list=service.decorator_list())
    
    print(ast.dump(new_class))  

    new_module = ast.Module(body=[new_class],
                            type_ignores=[])
    fixed_lines_module = ast.fix_missing_locations(new_module)
    return fixed_lines_module

