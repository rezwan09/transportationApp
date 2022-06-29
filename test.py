
from functions import *

a = "Cu Boulder"
b = "Safeway, 3325 28th St"
points = [(40.02534240131319, -105.25837419409055)]

# fastest

print("Calculating fastest route..")

fastest = calc_fastest_routes(
    a,
    b,
    reported_points=points,
    n_search_points=10)


for leg in fastest[0]['legs']:
    for step in leg['steps']:
        print(step["html_instructions"])


# safest

print("\nCalculating safest route..")

safest = calc_fastest_routes(
    a,
    b,
    reported_points=points,
    n_search_points=10, 
    preference='safest')

for leg in safest['legs']:
    for step in leg['steps']:
        print(step["html_instructions"])