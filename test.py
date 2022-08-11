
from functions import *
import time

a = "Cu Boulder"
b = "Safeway, 3325 28th St"
# points = [(40.02534240131319, -105.25837419409055)]
points = []

# fastest

# print("Calculating fastest route..")

# fastest = calc_fastest_routes(
#     a,
#     b,
#     reported_points=points,
#     n_search_points=10)


# for leg in fastest[0]['legs']:
#     for step in leg['steps']:
#         print(step["html_instructions"])


# safest

print("\nCalculating safest route..")

start_time = time.time()

safest = calc_fastest_routes(
    a,
    b,
    reported_points=points,
    n_search_points=10, 
    preference='safest')

for leg in safest['legs']:
    for step in leg['steps']:
        print(step["html_instructions"])
        
print( "Time: %0.3f" % (time.time() - start_time))