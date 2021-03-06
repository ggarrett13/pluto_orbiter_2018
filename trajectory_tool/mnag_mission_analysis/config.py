from poliastro.bodies import Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
from astropy.coordinates import solar_system_ephemeris

solar_system_ephemeris.set("jpl")

factor = {
    'mercury': 1.082,

    'venus': 1.047,

    'earth': 1.048,

    'mars': 1.076,

    'jupiter': 1.6,

    'saturn': 1.342,

    'uranus': 4.19,

    'neptune': 1.181,

    'pluto': 9.34,

}

body_d_domain = {
          'mercury':{
                            'upper':  1.12E5,
                            'lower': factor['mercury'] * 2439.7
  },
      'venus':{
                            'upper': 6.16E5,
                            'lower': factor['venus'] * 6051.8
  },
      'earth':{
                            'upper': 9.25E5,
                            'lower': factor['earth'] * 6371.
  },
      'mars':{
                            'upper': 5.76E5,
                            'lower': factor['mars'] * 3390.
  },
      'jupiter':{
                            'upper': 4.82E7,
                            'lower': factor['jupiter'] * 69911.
  },
      'saturn':{
                            'upper': 5.48E7,
                            'lower': factor['saturn'] * 58232.
  },
      'uranus':{
                            'upper': 5.18E7,
                            'lower': factor['uranus'] * 25362.
  },
      'neptune':{
                            'upper': 8.66E7,
                            'lower': factor['neptune'] * 24622.
  },
      'pluto':{
                            'upper': 3.16E6,
                            'lower': factor['pluto'] * 1188.
  }
}

# BODY OBJECT DICTIONARY FROM NAME
body_list = {
    'mercury': Mercury,
    'venus': Venus,
    'earth': Earth,
    'mars': Mars,
    'jupiter': Jupiter,
    'saturn': Saturn,
    'uranus': Uranus,
    'neptune': Neptune,
    'pluto': Pluto
}
