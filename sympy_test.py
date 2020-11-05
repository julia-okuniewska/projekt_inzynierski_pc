from sympy import *
# Declare symbolic variables. (I also use r for sqrt(3))
# r = sqrt(3)
# m = 1/4(1 - (L/l_0)**2)
x, y, z, sa, sb, m, r, L = symbols('x, y, z, sa, sb, m, r, L')


equation_13 = sa**2-r*(sa+sb)*x-sb**2-(sa-sb)*y

equation_17 = x**2 + y**2 + z**2-L**2+sa**2-sa*(r*x+y)-m*(sa**2+sb*sa+sb**2)


finale = equation_17 - equation_13
# print(idiff(equation_13, sa, x))
# print(idiff(equation_17, sa, x))
# print(idiff(finale, sa, x))

JS = [[idiff(finale, sa, x), idiff(finale, sa, y), idiff(finale, sa, z)],
      [idiff(finale, sb, x), idiff(finale, sb, y), idiff(finale, sb, z)]]

print(JS)
# JS_i_finale = [[          (r*sb + 2*x)/(2*m*sa + m*sb + 4*sa),           (-sb + 2*y)/(2*m*sa + m*sb + 4*sa),           2*z/(2*m*sa + m*sb + 4*sa)],
#               [(r*sb + 2*x)/(m*sa + 2*m*sb - r*x - 2*sb + y), (-sb + 2*y)/(m*sa + 2*m*sb - r*x - 2*sb + y), 2*z/(m*sa + 2*m*sb - r*x - 2*sb + y)]]


JS = [[idiff(equation_17, sa, x), idiff(equation_17, sa, y), idiff(equation_17, sa, z)],
      [idiff(equation_17, sb, x), idiff(equation_17, sb, y), idiff(equation_17, sb, z)]]

print(JS)
# JS_i_equation_17 = [[(-r*sa + 2*x)/(2*m*sa + m*sb + r*x + 2*sa + y), (-sa + 2*y)/(2*m*sa + m*sb + r*x + 2*sa + y), 2*z/(2*m*sa + m*sb + r*x + 2*sa + y)], [(-r*sa + 2*x)/(m*(sa + 2*sb)), (-sa + 2*y)/(m*(sa + 2*sb)), 2*z/(m*(sa + 2*sb))]]

