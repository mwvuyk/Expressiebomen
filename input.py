from Expressiebomen import *
import traceback
trees = {}
helpstr = {"new"        : "Create a new tree from an expression. Syntax: new <name> <expression>.",
           "simplify"   : "Simplify a tree to a new tree. Syntax: simplify <name> <new name>.",
           "diff"       : "Differentiate by a variable from a tree to a new tree. Syntax: diff <variable> <name> <new name>.",
           "print"      : "Print the expression represented by a tree. Syntax: print <name>.",
           "stop"       : "Exit the program.",
           "help"       : "You're already using this command.",
           "visualize"  : "Visualize a tree. Syntax: visualize <name>."}
print('Commands: new, simplify, diff, visualize, print, stop, help. Other operations (+,*,etc) work too.')
print('You must access trees outside of commands by doing: "trees['+"'treename'"+']".')
print("For example: trees['c'] = trees['a'] + trees['b'].")
print("Also, in order to modify a tree with a mathematical function, you must use")
print("trees['a'] = Expression.sin(trees['a']), not sin(trees['a']).")
print("Available functions: sin, cos, tan, log, exp")

while True:
    try:
        h = input()
        if h != "":
            i = h.split()
            if i[0] == "new":
                if i[1].isalpha():
                        trees[i[1]] = Expression.fromString("".join(i[2:]))
                        print('New tree named "' + i[1] + '" created with expression: ' + str(trees[i[1]]))
                else:
                    print('Tree names must be only letters')

            elif i[0] == "simplify":
                if len(i) == 3:
                    if i[2].isalpha():
                        trees[i[2]] = trees[i[1]].simplify()
                        print('Expression simplified from '+ str(trees[i[1]])+' to: ' + str(trees[i[2]]))
                    else:
                        print('Tree names must be only letters')                    
                else:
                    print('Wrong number of arguments. Expected: 2')

            elif i[0] == "diff":
                if len(i) == 4:
                    if i[3].isalpha():
                        trees[i[3]] = trees[i[2]].diff(i[1])
                        print('Expression differentiated from '+ str(trees[i[2]])+' to: ' + str(trees[i[3]]))
                    else:
                        print('Tree names must be only letters')
                else:
                    print('Wrong number of arguments. Expected: 3')                
                
            elif i[0] == "visualize":
                if len(i) == 2:
                    trees[i[1]].visualizeTree()
                else:
                    print('Wrong number of arguments. Expected: 1')
                
            elif i[0] == "print":
                if len(i) == 2:
                    print(str(trees[i[1]]))
                else:
                    print('Wrong number of arguments. Expected: 1')            

                
            elif i[0] == "stop":
                break

            elif i[0] == "help":
                try:
                    print(helpstr[i[1]])
                except:
                    print('No help available for that subject.')
            else:
                exec(h)
    except KeyError:
        print("Unknown tree name.")
    except Exception as exc:
        print(traceback.format_exc())

