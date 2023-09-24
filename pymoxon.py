# pymoxon.py -- Python port of BASIC Moxon Antenna calculator by
# L. B. Cebik, W4RNL (SK), http://on5au.be/content/a10/moxon/moxgen.html
#
# Note that my version only outputs dimensions in millimeters

import argparse
import math

def evaluate_polynomial(x, coefficients, order="natural"):
    # If `order` is "natural", assume coefficients go from the highest to the
    # lowest power: coefficients[0]*x**n + coefficients[1]*x**(n-1) etc.
    # (I write polynomials this way, so I considered it "natural".)
    # If `order` is anything else, use the reverse order:
    # coefficients[0]*x**0 + coefficients[1]*x**1 + etc.
    if order=="natural":
        # The calculation uses reverse order!
        coefficients.reverse()
    result = 0.
    for exponent, coefficient in enumerate(coefficients):
        result += coefficient * x**exponent
    return result


parser = argparse.ArgumentParser(description="Generate dimensions for a Moxon Antenna.")
parser.add_argument("frequency", type=float, help="Frequency in MHz")
parser.add_argument("wire_diameter", type=float,
        help="Wire diameter in millimeters")

args = parser.parse_args()

c = 299792 # km/s

wavelength = c / args.frequency

normalized_wire_diameter = args.wire_diameter / wavelength

log_wire_diameter = math.log(normalized_wire_diameter, 10)

if log_wire_diameter < -6 or log_wire_diameter > -2:
    print("Warning: Wire diameter", args.wire_diameter,
            "is outside of model range. Proceed with caution.")

# A is the width of the driven element
# This 2nd order poly models dimension A
poly_A = [-0.0008571428571, -0.009571428571, 0.3398571429]
A = evaluate_polynomial(log_wire_diameter, poly_A)

# B is the length of the driven tails
# It is also modeled using a 2nd order poly
poly_B = [-0.002142857143, -0.02035714286, 0.008285714286]
B = evaluate_polynomial(log_wire_diameter, poly_B)

# C is the gap between the driven element's tails and the reflector tails
# Another 2nd order poly
poly_C = [0.001809523381, 0.01780952381, 0.05164285714]
C = evaluate_polynomial(log_wire_diameter, poly_C)

# D is the length of the reflector tails
# Just a linear equation this time
D = 0.001*log_wire_diameter + 0.07178571429

# E is provided or convenience, it's the overall length of the antenna
E = B + C + D

# Results are relative to the frequency still, let's convert them 
A, B, C, D, E = [wavelength*x for x in [A, B, C, D, E]]

unit = "mm"
for name, dimension in zip("ABCDE", [A, B, C, D, E]):
    print(name, "=", round(dimension), unit)
