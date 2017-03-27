#import math
#import numpy as py
from sympy import Symbol
from collections import namedtuple

#dictionary of operators with corresponding attributes (precedence and associativity)

opatt = namedtuple('type', 'precedence associativity')

oplist = {
        '(' : opatt(9, 'Left'),
        ')' : opatt(0, 'Left'),
        '+' : opatt(2, 'Left'),
        '-' : opatt(2, 'Left'),
        '*' : opatt(3, 'Left'),
        '/' : opatt(3, 'Left'),
        '%' : opatt(3, 'Left'),
        '**': opatt(4, 'Right'),
        '^' : opatt(4, 'Right'),
        
        }
# split string into list with appropriate attributes for operators
def tokenize(string):
    #1) split string into constants and operators
    tokenstring = []
    for c in string:
        if c in oplist:
            tokenstring.append(' %s ' % c)
        elif c == ' ':
            continue
        else: 
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    stringlist = tokenstring.split() 
    #2) additional case for multiple letter operators
    ans = []    
    for t in stringlist:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    #3) classify 
    tokens = []
    for i in ans:
        if i in oplist:
            tokens.append((i, oplist[i])) #if operator
        elif isnumber(i):
            tokens.append(('num', i))   #if constant
        else: 
            tokens.append(('var', i))   #if variable
            
    return tokens

    
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# check if a string represents an integer value 
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    

class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """
    # TODO: when adding new methods that should be supported by all subclasses, add them to this list
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
    
    def __sub__(self, other):
        return SubNode(self, other)
    
    def __mul__(self, other):
        return MulNode(self, other)
    
    def __truediv__(self, other):
        return DivNode(self, other)
    
    def __pow__(self, other):
        return PowNode(self, other)
    
    def __xor__(self, other):
        return PowNode2(self, other)
        
    # TODO: other overloads, such as __sub__, __mul__, etc.
    
    # basic Shunting-yard algorithm
    def fromString(string):
        # turn string into list with operator values 
        tokens = tokenize(string)
        # stack used by the Shunting-Yard algorithm
        stack, output = [], []
        
        for token, value in tokens:
            if token == 'num':
                if isint(value): #Append the numbers to the output as a float or an int.
                    output.append(Constant(int(value))) 
                else:
                    output.append(Constant(float(value)))
            elif token == 'var':
                output.append(Variable(value))
                'if value = token -> strange result'
                
            elif token in oplist:
                t1, (p1, a1) = token, value
                while len(stack)>0:
                    t2, (p2, a2) = stack[-1] 
                    if (a1 == 'Left' and p1 <= p2) or (a1 == 'Right' and p1 < p2): #p1 lower rank
                        if t1 != ')':
                            if t2 != '(':
                                stack.pop()
                                output.append(t2)
                            else: 
                                break
                        else:
                            if t2 != '(':
                                stack.pop()
                                output.append(t2)
                            else:
                                stack.pop()
                                break
                    else:
                        break
                if t1 != ')':
                    stack.append((token, value))
            else: 
                raise ValueError('Unknown token: %s' % token)
                    
        while stack:
            t2, (p2, a2) = stack[-1]
            stack.pop()
            output.append(t2)   
        #convert RPN to actual expression tree
        for t in output:
             try:       
                if t in oplist:
                    y = stack.pop()
                    x = stack.pop()
                    stack.append(eval('x %s y' % t))
                else:
                    stack.append(t)
             except TypeError:
                 stack.append(t) 
        return stack[0]        
    
class Variable(Expression):
    """Represents variable"""
    def __init__(self, x):
        self.symbol = Symbol(str(x))
     
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.symbol == other.symbol
        else:
            return False
        
    def __str__(self):
        return str(self.symbol)
    

class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        
        # TODO: do we always need parantheses?
        return "(%s %s %s)" % (lstring, self.op_symbol, rstring)
        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')
        
class SubNode(BinaryNode):
    """Represents the subtraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs, '-')    
        
class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs, '*')
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/')        
        
class PowNode(BinaryNode):
    """Represents the exponential operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs, '**') 
      
class XorNode(BinaryNode):
    """Represents the exponential operator"""
    def __init__(self, lhs, rhs):
        super(XorNode, self).__init__(lhs, rhs, '^')  
        #werkt nog niet
        
        
        
        
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.



tokens = tokenize('1+2')



expr1 = Expression.fromString('( 1 + x ) / 5 ** 6')
print(expr1)
#expr2 = Expression.fromString('1+2+3')
#expr3 = Expression.fromString('1+2+4')
