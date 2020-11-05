import sympy as sp
# Declare symbolic variables. (I also use r for sqrt(3))
x, y, z, s, sa, sb, m, r = sp.symbols('x, y, z, s, sa, sb, m, r')
A = sp.Matrix([[                 2*sa - r*x - y,    -2*sb - r*x + y],
               [-2*sa + r*x + y + 2*m*sa + m*sb,     m*sa + 2*m*sb]])
B = sp.Matrix([[r*sa + r*sb,    sa - sb,   0],
               [ 2*x - r*sa,   2*y - sa, 2*z]])
Ainv = sp.Matrix.inv(A)
res = Ainv.multiply(B)
J = res.subs({sa: s, sb: s, x: 0}) # do the substitution

for i in range(0,2):
    for j in range(0,3):
        result = sp.simplify(J[3*i + j])
        print(result)


#print("hello")