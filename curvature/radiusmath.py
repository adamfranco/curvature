import math

def circum_circle_radius(a, b, c):
  # Circumcircle radius calculation from http://www.mathopenref.com/trianglecircumcircle.html
  if a > 0 and b > 0 and c > 0:
    try:
      divider = math.sqrt(math.fabs((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)))
      return (a * b * c) / divider
    except ZeroDivisionError:
      return 10000
  else:
    return 10000
