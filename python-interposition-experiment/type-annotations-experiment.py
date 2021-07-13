import ast
import pprint

test_source_file = "type-annotations-experiment-test.py"

with open(test_source_file) as f:
    test_source = f.read()

test_ast = ast.parse(test_source,
                     filename=test_source_file,
                     type_comments=True)

# pp = pprint.PrettyPrinter(indent=4)
# print(pp.pprint(ast.dump(test_ast)))
print(ast.dump(test_ast))