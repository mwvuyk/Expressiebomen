from sympy import Symbol
from math import sin,cos,tan,log,exp
import turtle

precedence = { # Dictionary of operators with corresponding presedence
        '+' : 2,
        '-' : 2,
        '*' : 3,
        '/' : 3,
        '%' : 3,
        '**': 4,
        '^' : 4,
        '#' : 5,
        }

associativity = { # Dictionary of operators with corresponding associativity
        '+' : 'Left',
        '-' : 'Left',
        '*' : 'Left',
        '/' : 'Left',
        '%' : 'Left',
        '**': 'Right',
        '^' : 'Right',
        '#' : 'Left',
        }

oplist = ['+','-','*','/','%','**','^','(',')'] # list of operators to use when to check if element/node is an operator
flist = ['sin','cos','tan','log','exp']         # list of functions to use when to check if element/node is a function

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

        elif len(ans) > 2 and t == '(' and ans[-1] in flist:
            ans[-1] = ans[-1] # ???
            ans.append(t)
        else:
            ans.append(t)
    #3) classify 
    tokens = []
    prev = None
    for i in ans:
        
        if ((prev != ')' and prev in oplist) or prev == None) and i == '-':
            tokens.append(('neg','#'))    # if negation -
        elif len(i)>1 and i in flist:
            tokens.append(('func',i))     # if function
        elif i == '(':
            tokens.append(('leftp',i))    # if parenthesis
        elif i == ')':
            tokens.append(('rightp',i))   # if parenthesis
        elif i in oplist:
            tokens.append(('oper', i))    # if operator
        elif isnumber(i):
            tokens.append(('num', i))     # if constant
        else: 
            tokens.append(('var', i))     # if variable
        prev = i
            
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
    
    # overloading operators and functions
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
        return XorNode(self, other)

    def __neg__(self):
        return NegNode(self)

    def sin(self):
        return SinNode(self)

    def cos(self):
        return CosNode(self)

    def tan(self):
        return TanNode(self)

    def exp(self):
        return ExpNode(self)

    def log(self):
        return LogNode(self)
    
    
    def visualizeTree(self): 
        " Uses turtle module to visualize the expression tree "
        def tele_to(x, y):        # Teleports to coordinates (without drawing)
            t.penup()
            t.goto(x, y)
            t.pendown()
        def draw(self, x, y, dx): # Draws lines to connect nodes and writes down text for operators/variables/constants etc.
            if self != None:
                t.goto(x, y)
                tele_to(x, y-20)
                # Writes down type of node in corresponding colour and font
                if self.content in oplist:      # operator = black
                    t.pencolor('Black')
                    t.write(self.content, move = False, align='left', font=('Arial', 14, 'bold'))
                elif self.content in flist:     # function = green
                    t.pencolor('Green')
                    t.write(self.content, move = False, align='left', font=('Arial', 12, 'bold'))
                elif type(self) == Variable:    # variable = red
                    t.pencolor('Red')
                    t.write(self.content, move = False, align='left', font=('Arial', 12, 'normal'))
                elif type(self) == Constant:    # constant = blue
                    t.pencolor('Blue')
                    t.write(self.content, move = False, align='left', font=('Arial', int(13 - (len(str(self.content))/2)), 'normal'))
                t.pencolor('Black')             # switches back to the colour black
                draw(self.lhs, x-dx, y-60, dx/2)# draws steeper lines after every recursion in order to make it fit
                tele_to(x, y-20)
                draw(self.rhs, x+dx, y-60, dx/2)
        def depth(self):                        # calculates maximum depth in order to determine appropriate measurements
            if self != None:
                depth_lrs = depth(self.lhs)
                depth_rhs = depth(self.rhs)
                
                if (depth_lrs > depth_rhs):
                    return depth_lrs + 1
                else:
                    return depth_rhs + 1
            else:
                return 0        
        t = turtle.Turtle()
        h = depth(self)                 # height
        if h>= 10:
            return print("Expression tree is too large to visualize. You might want to try .simplify() first")
        tele_to(0, 30*h)                # starting location
        draw(self, 0, 30*h, 30*h)       # draws whole tree
        t.hideturtle()                  # hides turtle
        turtle.mainloop()               # closes interactive mode

        
    def simplify(self, prev = None):
        " Simplifies Expression Tree "
        if type(self) == Constant or type(self) == Variable:
            return self
        try: 
            # Simplying parts with just Constants
            c = float(eval(str(self)))
            if c >= 0:                          # when evaluation of children is larger than zero -> just use constant
                if float(c) == int(c):          
                    self = Constant(int(c))
                    return self
                else:
                    self = Constant(float(c))
                    return self
            elif c<0:                           # when evaluation of children is less than zero -> use negation
                if float(c) == int(c):
                    self = NegNode(int(abs(c)))
                    return self
                else:
                    self = NegNode(float(abs(c)))
                    return self
        except:
            # individual special cases for each operator/function with present variables
            if type(self) == MulNode:
                if self.rhs.content == 0 or self.lhs.content == 0:
                    self = Constant(0)
                    return self
                elif self.rhs.content == 1:
                    self = self.lhs
                    return self
                elif self.lhs.content == 1:
                    self = self.rhs   
                    return self    
            elif type(self) == DivNode:
                if self.rhs.content == 0:
                    print("ERROR! Division by zero is not valid! Cannot be simplified.")    # exception 1) for division by zero which is not allowed
                    return self
                elif self.rhs.content == 1:
                    self = self.lhs
                    return self
                elif self.lhs.content == 0:
                    self = Constant(0)
            elif type(self) == AddNode:
                if self.rhs.content == 0:
                    self = self.lhs
                    return self
                elif self.lhs.content == 0:
                    self = self.rhs 
                    return self
            elif type(self) == SubNode:
                if self.rhs.content == 0:
                    self = self.lhs
                    return self
                elif self.lhs.content == 0 and self.rhs.content != 0:
                    self = NegNode(self.lhs) 
                    return self
            elif type(self) == PowNode:
                if self.rhs.content == 0:
                    self = Constant(1)
                    return self
                elif self.rhs.content == 1:
                    self = self.lhs
                    return self    
            elif type(self) == LogNode:
                if self.lhs.content == 0:
                    print("ERROR! Log(0) is not valid! Cannot be simplified.")              # exception 2) for log(0) which is also not allowed
                if self.lhs.content == 1:
                    self = Constant(0)
                    return self 
            elif type(self) == CosNode or type(self) == ExpNode:               # same case for both cos (x) and e^x
                if self.lhs.content == 0:
                    self = Constant(1)
                    return self
            elif type(self) == SinNode:
                if self.lhs.content == 0:
                    self = Constant(0)
                    return self 
        self.lhs = Expression.simplify(self.lhs)
        if not isinstance(self, Function) and not isinstance(self, NegNode):
            self.rhs = Expression.simplify(self.rhs)
        if self == prev:                                                       # if nothing changes after another recursion, simplify stops
            return self
        else: 
            return self.simplify(prev = self)


    def findVariable(self, var, val):       # to be called for partial evaluations
        try:    
            if type(self) == Variable and str(self.content) == var:
                return Constant(val)
            self.lhs = self.lhs.findVariable(var, val)
            if not isinstance(self, Function) and not isinstance(self, NegNode):
                self.rhs = self.rhs.findVariable(var, val)
            return self
        except AttributeError:
            return self
        
        
    def evaluate(self, d={}):                   # uses dictionary to fill in value for the given variables
        try:                                    # simple evaluate with all values of variables given
            for var in d:
                exec("%s = %d" % (var, d[var])) 
            return eval(str(self))
        except:                                 # partial evaluation
            for var in d:
                self = self.findVariable(var, d[var])     
            return self.simplify()    
                
    
    def fromString(string):
        " Makes Expression Tree from string input "
        #step 1: Puts string in RPN with Shunting-Yard algoritm
        
        tokens = tokenize(string)                           # turn string into list with operator values 
        stack, output = [], []                              # creates stack list Shunting Yard and output list for RPN
        for token, value in tokens:
            if token == 'num':
                if isint(value):                            # append the numbers to the output as a float or an int
                    output.append(Constant(int(value))) 
                else:
                    output.append(Constant(float(value)))
            elif token == 'func':
                stack.append((token,value))                 # will be evaluated by Shunting Yard
            elif token == 'var':
                output.append(Variable(value))              # append variables to output list              
            elif token == 'oper' or token == 'neg':
                value1 = value
                if stack:
                    while stack[-1][0] == 'oper' or stack[-1][0] == 'neg':   # While there are operators left to process
                        value2 = stack[-1][1]                                # Copy values from the top of the stack
                        if ((associativity[value1] == 'Left' and (precedence[value1] <= precedence[value2]))
                        or (associativity[value1] == 'Right' and (precedence[value1] < precedence[value2]))):
                            # Evaluate precedence and associativity of operators
                            output.append(stack.pop())
                            if not stack:
                                break
                        else:
                            break        
                stack.append((token,value))         
            elif token == 'leftp':                      # when token is LEFT paranthesis
                stack.append((token,value))             # token is added to top of stack
                
            elif token == 'rightp':                     # when token is RIGHT paranthesis
                while stack[-1][0] != 'leftp':          # as long there are no left parantheses on top of stack
                    try:                                # add all items on stack to output
                        output.append(stack.pop())
                    except IndexError:                  # catches error for incorrect use of parantheses
                        raise 'MismatchedParenthesis'
                stack.pop()
                if len(stack) > 0 and stack[-1][0] == 'func': # when left paranthesis is found and function is on top of stack
                    output.append(stack.pop())                # add it to output
            else: 
                raise ValueError('Unknown token: %s' % token) # catches error for incorrect use of tokens
                    
        while stack:                                    # after all tokens are evaluated, elements still on stack are added to output
            token = stack.pop()
            if token == 'leftp' or token == 'rightp':
                raise 'MismatchedParenthesis'
            output.append(token)
            
        # step 2: convert RPN to actual expression tree
        for t in output:
            if type(t) == tuple:                                # reduce to just its value
                t = t[1]
            try:       
                if t in oplist:
                    y = stack.pop()
                    x = stack.pop()
                    stack.append(eval('x %s y' % t))            # evaluate operators
                elif t in flist:
                    x = stack.pop()
                    stack.append(eval('Expression.%s(x)' % t))  # evaluate functions
                elif t == '#':
                    x = stack.pop()
                    stack.append(eval('-x'))                    # evaluate negations
                else:
                    stack.append(t)
            except TypeError:
                 stack.append(t) 
        return stack[0]                                         # return Expression Tree 
      
    
class Variable(Expression):
    """Represents variable"""
    def __init__(self, x):
        self.content = Symbol(str(x))
        self.lhs = None
        self.rhs = None
     
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.content == other.content
        else:
            return False
        
    def __str__(self):
        return str(self.content)

    def diff(self,var='x'):
        if str(self.content) == var:
            return Constant(1)
        else:
            return Constant(0)
    

class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.content = value
        self.lhs = None
        self.rhs = None
        
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.content == other.content
        else:
            return False
        
    def __str__(self):
        return str(self.content)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.content)
        
    def __float__(self):
        return float(self.content)

    def diff(self,var='x'):
        return Constant(0)
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.content = op_symbol
    
    def __eq__(self, other):
        if type(self) == type(other):
            if self.content == '+' or self.content == '*':
                return (self.lhs == other.lhs and self.rhs == other.rhs) or (self.lhs == other.rhs and self.rhs == other.lhs)
            else:
                return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):              # overloading of __str__ which calls its children (other subclasses) in the process 
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        if isinstance(self.lhs, BinaryNode) and precedence[self.lhs.content] <= precedence[self.content]:
            lstring = '(' + lstring + ')'
        if isinstance(self.rhs, BinaryNode) and precedence[self.rhs.content] <= precedence[self.content]:        
            rstring = '(' + rstring + ')'
        return "%s %s %s" % (lstring, self.content, rstring)

class UnaryNode(Expression):
    """A node in the expression tree representing a unary operator."""

    def __init__(self,lhs,op_symbol):
        self.lhs = lhs
        self.rhs = None
        self.content = op_symbol

    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs
        else:
            return False
    def __str__(self):
        lstring = str(self.lhs)
        return "%s %s" % (self.content,lstring)
    
class Function(Expression):
    """A node in the expressin tree representing a function operator."""
    def __init__(self,lhs,content):
        self.lhs = lhs
        self.content = content
        self.rhs = None

    def __str__(self):
        lstring = str(self.lhs)
        return "%s(%s)" % (self.content, lstring)
    
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

    def diff(self,var='x'):
        result = self.lhs.diff(var) + self.rhs.diff(var)
        return result
        
class SubNode(BinaryNode):
    """Represents the subtraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs, '-')
        
    def diff(self,var='x'):
        result = self.lhs.diff(var) - self.rhs.diff(var)
        return result
    
class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs, '*')

    def diff(self,var='x'):
        result = (self.lhs.diff(var)*self.rhs)+(self.rhs.diff(var)*self.lhs)
        return result        
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/')

    def diff(self,var='x'):
        result = (self.lhs.diff(var)*self.rhs-self.rhs.diff(var)*self.lhs)/(self.rhs**2)
        return result
        
class PowNode(BinaryNode):
    """Represents the exponential operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs, '**') 

    def diff(self,var='x'):
        f = self.lhs
        g = self.rhs
        df = self.lhs.diff(var)
        dg = self.rhs.diff(var)
        result = f**(g-Constant(1))*(g*df+f*Expression.log(f)*dg)
        return result           
    
class XorNode(BinaryNode):
    """Represents the exclusive or operator"""
    def __init__(self, lhs, rhs):
        super(XorNode, self).__init__(lhs, rhs, '^')

    def diff(self,var='x'):
        print("You cannot diff Xor. Did you mean **?")

class SinNode(Function):
    """Represents the sin function"""
    def __init__(self, lhs):
        super (SinNode, self).__init__(lhs,'sin')

    def diff(self,var='x'):
        result = self.lhs.diff(var)*Expression.cos(self.lhs)
        return result

class TanNode(Function):
    """Represents the tan function"""
    def __init__(self,lhs):
        super (TanNode,self).__init__(lhs,'tan')

    def diff(self,var='x'):
        result = (Constant(2)*self.lhs.diff(var))/(Expression.cos(Constant(2)*self.lhs)+Constant(1))
        return result

class CosNode(Function):
    """Represents the cos function"""
    def __init__(self,lhs):
        super (CosNode,self).__init__(lhs,'cos')

    def diff(self,var='x'):
        result = self.lhs.diff(var)*-Expression.sin(self.lhs)
        return result

class LogNode(Function):
    """Represents the natural logarithm"""
    def __init__(self,lhs):
        super (LogNode,self).__init__(lhs,'log')

    def diff(self,var='x'):
        result = self.lhs.diff(var) / self.lhs
        return result

class ExpNode(Function):
    """Represents the exponent (e^x)"""
    def __init__(self,lhs):
        super (ExpNode,self).__init__(lhs,'exp')

    def diff(self,var='x'):
        result = self.lhs.diff(var)*Expression.exp(self.lhs)
        return result
    
class NegNode(UnaryNode):
    """Represents the negative operator (-)"""
    def __init__(self,lhs):
        super (NegNode,self).__init__(lhs,'-')
 
    def diff(self,var='x'):
        return -self.lhs.diff(var)

if __name__ == '__main__':
    x = Expression.fromString
    d = x('(1+x)*(3*x**2)')
    print(d)
    k = d.diff()
    print(k)
    print(k.simplify())
    #e.visualizeTree()
