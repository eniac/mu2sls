
## An experiment trying to rewrite globally accessible variable

a = str([1,2,3])

print("a:" + a)

def new_str(x):
    print("New str is the best str!")
    return old_str(x)

## Save the old str
old_str = str

## Change the new str
str = new_str

b = str([1,2,3])

print("b:" + b)
