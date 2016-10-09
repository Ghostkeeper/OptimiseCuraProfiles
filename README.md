# Optimise Cura Profiles
This script is meant to minimise the size of Cura profiles.

You feed it a set of profiles in a certain folder structure. The script will go through the profiles in one leaf folder and derive the common denominator from them. If a majority of the profiles share a certain setting, the setting will be removed from these profiles and put in the profile for the directory. It will then look one directory higher, to see if any subdirectories have a common denominator, and so on. This will then cause the common denominator of all profiles to bubble up as far as it can, in order to make each individual profile as small as possible.

The input files can be either in Cura's JSON format, its XML format or its CFG format. It will output only CFG profiles for now, so if these profiles are meant to be materials or definitions, they will need to be translated by hand.