from sympy import Symbol
from math import sin,cos,tan,log,exp

precedence = {
        '+' : 2,
        '-' : 2,
        '*' : 3,
        '/' : 3,
        '%' : 3,
        '**': 4,
        '^' : 4,
        '#' : 5,
        }

associativity = {
        '+' : 'Left',
        '-' : 'Left',
        '*' : 'Left',
        '/' : 'Left',
        '%' : 'Left',
        '**': 'Right',
        '^' : 'Right',
        '#' : 'Left',
        }

oplist = ['+','-','*','/','%','**','^','(',')']
flist = ['sin','cos','tan','log','exp']

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
            ans[-1] = ans[-1]
            ans.append(t)
        else:
            ans.append(t)
    #3) classify 
    tokens = []
    prev = None
    for i in ans:
        
        if ((prev != ')' and prev in oplist) or prev == None) and i == '-':
            tokens.append(('neg','#')) #if negation -
        elif len(i)>1 and i in flist:
            tokens.append(('func',i)) #if function
        elif i == '(':
            tokens.append(('leftp',i)) #if parenthesis
        elif i == ')':
            tokens.append(('rightp',i))   #if parenthesis
        elif i in oplist:
            tokens.append(('oper', i)) #if operator
        elif isnumber(i):
            tokens.append(('num', i))   #if constant
        else: 
            tokens.append(('var', i))   #if variable
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


    def inorderRead(self, p=0):
        if type(self) == Constant or type(self) == Variable:
            return str(self.content) #If we have a number, just return the number
        
        elif self.content in flist: #If we have a function, we need to set very low precedence and always have parenthesis
            a = self.content + '(' + self.lhs.inorderRead(-1) + ')'
            return a

        elif self.content == '-' and self.rhs == None: #If we have a negative -, treat it as a function but without parentheses
            a = self.content + self.lhs.inorderRead(5)
            return a
        else:    
            try:
                a = self.lhs.inorderRead(precedence[self.content]) #If we have an operator
                a = a + self.content                               #Read its left and right nodes
                a = a + self.rhs.inorderRead(precedence[self.content]) #In Inorder (Left,self,Right)
            except AttributeError:                                 #If no more nodes exist, nothing more needs to be done. (This may not be neccesary.)
                print("AttributeError. Invalid expression?")
            if precedence[self.content] < p: #Parenthesis should be added if the order of operations
                a = '(' + a + ')' #Does not match the precedence of the operators
            return a
        
    def evaluate(self, d={}):
        for var in d:
            v = var   
            exec("%s = %d" % (v,d[var]))
        return eval(self.inorderRead())     
    
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

            elif token == 'func':
                stack.append((token,value))
            elif token == 'var':
                output.append(Variable(value)) # Append Variables

          #  elif token == 'neg':
          #      stack.append((token,value))
                
            elif token == 'oper' or token == 'neg':
                token1, value1 = token, value
                if stack:
                    while stack[-1][0] == 'oper' or stack[-1][0] == 'neg':   #While there are operators left to process
                        value2 = stack[-1][1] #Copy values from the top of the stack
                        if ((associativity[value1] == 'Left' and (precedence[value1] <= precedence[value2]))
                        or (associativity[value1] == 'Right' and (precedence[value1] < precedence[value2]))):
                            #Evaluate precedence and associativity of operators
                            output.append(stack.pop())
                            if not stack:
                                break
                        else:
                            break
                        
                stack.append((token,value))

            elif token == 'leftp':
                stack.append((token,value))

            elif token == 'rightp':
                while stack[-1][0] != 'leftp':
                    try:
                        output.append(stack.pop())
                    except IndexError:
                        raise 'MismatchedParenthesis'
                stack.pop()
                if len(stack) > 0 and stack[-1][0] == 'func':
                    output.append(stack.pop())

                #TODO: check for function token
            else: 
                raise ValueError('Unknown token: %s' % token)
                    
        while stack:
            token = stack.pop()
            if token == 'leftp' or token == 'rightp':
                raise 'MismatchedParenthesis'

            output.append(token)
        print(output)
        #convert RPN to actual expression tree
        for t in output:
            if type(t) == tuple:
                t = t[1]
            try:       
                if t in oplist:
                    y = stack.pop()
                    x = stack.pop()
                    stack.append(eval('x %s y' % t))
                elif t in flist:
                    x = stack.pop()
                    stack.append(eval('Expression.%s(x)' % t))
                elif t == '#':
                    x = stack.pop()
                    stack.append(eval('-x'))
                    
                else:
                    stack.append(t)
            except TypeError:
                 stack.append(t) 
        return stack[0]    
        
    
class Variable(Expression):
    """Represents variable"""
    def __init__(self, x):
        self.content = Symbol(str(x))
     
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
            
    def __str__(self):
        return self.inorderRead()

class UnaryNode(Expression):

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
        return self.inorderRead()

class Function(Expression):
    def __init__(self,lhs,content):
        self.lhs = lhs
        self.content = content
        self.rhs = None

    def __str__(self):
        return self.inorderRead()

    
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
        result = self.lhs.diff(var)*self.rhs+self.rhs.diff(var)*self.lhs
        return result        
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/')

    def diff(self,var='x'):
        result = (self.lhs.diff(var)*self.rhs+self.rhs.diff(var)*self.lhs)/(self.rhs**2)
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
        result = f**(g-Variable(1))*(g*df+f*Expression.log(f)*dg)
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

class TanNode(Function):
    """Represents the tan function"""
    def __init__(self,lhs):
        super (TanNode,self).__init__(lhs,'tan')

class CosNode(Function):
    """Represents the cos function"""
    def __init__(self,lhs):
        super (CosNode,self).__init__(lhs,'cos')

class LogNode(Function):
    """Represents the natural logarithm"""
    def __init__(self,lhs):
        super (LogNode,self).__init__(lhs,'log')


class ExpNode(Function):
    """Represents the exponent (e^x)"""
    def __init__(self,lhs):
        super (ExpNode,self).__init__(lhs,'exp')
    
        
class NegNode(UnaryNode):
    """Represents the negative operator (-)"""
    def __init__(self,lhs):
        super (NegNode,self).__init__(lhs,'-')





c = Expression.fromString('(sin(7) * x) + (exp(y)**2)')
x = Expression.fromString
d = x('x**2**x')
e = d.diff()


#expr2 = Expression.fromString('1+2+3')
#expr3 = Expression.fromString('1+2+4')
