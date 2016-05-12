import math
rad_earth_m = 6373000 # Radius of the earth in meters

class Units(object):
    units = 'm'

    def __init__(self, units):
        if units in ['mi', 'km', 'm']:
            self.units = units
        else:
            raise ValueError("units must be 'mi', 'km', or 'm'")

    def convert(self, value):
        if self.units == 'mi':
            return value / 1609
        elif self.units == 'km':
            return value / 1000
        elif self.units == 'm':
            return value
        else:
            raise ValueError("units must be 'mi', 'km', or 'm'")

def distance_on_earth(lat1, long1, lat2, long2):
    return distance_on_unit_sphere(lat1, long1, lat2, long2) * rad_earth_m

# From http://www.johndcook.com/python_longitude_latitude.html
def distance_on_unit_sphere(lat1, long1, lat2, long2):
	if lat1 == lat2	 and long1 == long2:
		return 0

	# Convert latitude and longitude to
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0

	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians

	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians

	# Compute spherical distance from spherical coordinates.

	# For two locations in spherical coordinates
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) =
	#	 sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length

	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
		   math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )

	# Remember to multiply arc by the radius of the earth
	# in your favorite set of units to get length.
	return arc
