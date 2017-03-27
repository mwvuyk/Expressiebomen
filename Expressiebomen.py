from sympy import Symbol

assoc = {
        '+' : 2,
        '-' : 2,
        '*' : 3,
        '/' : 3,
        '%' : 3,
        '**': 4,
        '^' : 4,
        
        }

prec = {
        '+' : 'Left',
        '-' : 'Left',
        '*' : 'Left',
        '/' : 'Left',
        '%' : 'Left',
        '**': 'Right',
        '^' : 'Right',
        
        }

oplist = ['+','-','*','/','%','**','^','(',')']
flist = ['sin']
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
        if i == '(':
            tokens.append(('leftp',i))
        elif i == ')':
            tokens.append(('rightp',i))   
        elif i in oplist:
            tokens.append(('oper', i)) #if operator
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
        return XorNode(self, other)
        
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
                output.append(Variable(value)) # Append Variables
                
            elif token == 'oper':
                token1, value1 = token, value
                if stack:
                    while stack[-1][0] == 'oper':   #While there are operators left to process
                        value2 = stack[-1][1] #Copy values from the top of the stack
                        if (assoc[value1] == 'Left' and prec[value1] <= prec[value2]) or (assoc[value1] == 'Right' and prec[value1] < prec[value2]):
                            #Evaluate precedence and associativity of operators
                            output.append(stack.pop())
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
                #TODO: check for function token
            else: 
                raise ValueError('Unknown token: %s' % token)
                    
        while stack:
            token = stack.pop()
            if token == 'leftp' or token == 'rightp':
                raise 'MismatchedParenthesis'

            output.append(token)
        
        #convert RPN to actual expression tree
        for t in output:
            if type(t) == tuple:
                t = t[1]
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
        self.content = Symbol(str(x))
     
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.content == other.content
        else:
            return False
        
    def __str__(self):
        return str(self.content)
    

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
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.content = op_symbol
    
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
        return "(%s %s %s)" % (lstring, self.content, rstring)

    
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


        
        
        
        
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.




a = Expression.fromString('( 1 + x ) / 5 ** 6')
b = Expression.fromString('5 * x ** 2')
print(a * b)

#expr2 = Expression.fromString('1+2+3')
#expr3 = Expression.fromString('1+2+4')
