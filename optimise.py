#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Optimises a set of profiles for Cura.

For usage instructions, run the script with the "--help" parameter.
"""

import argparse #To parse the input and output directories.
import collections #For namedtuple.
import logging
import os #To get the current working directory as defaults for input and output, and for file path operations.

#Global configuration stuff.
logging.basicConfig(level=logging.DEBUG)
Profile = collections.namedtuple("Profile", "filepath settings subprofiles")

def optimise(input_dir, output_dir):
	"""
	Performs the optimisation.

	Files are taken from the input directory in its appropriate structure,
	flattened, the common denominator is taken, and everything is then written
	to the output directories.
	:param input_dir: The root directory of the input profile structure.
	:param output_dir: The root directory of the output profile structure.
	"""
	profile_root = get_profiles(input_dir)
	bubble_common_values(profile_root)
	remove_redundancies(profile_root)
	write_profiles(output_dir, profile_root)

def get_profiles(input_dir):
	"""
	Gets the profile structure described in the input directory.

	Each profile is completely flat, meaning that its settings contain every key
	known in the input directory.
	:param input_dir: The root of the input directory structure.
	:return: The root profile of the profile structure in the input directory.
	"""
	logging.info("Reading profiles.")
	raise Exception("Not implemented yet.")

def bubble_common_values(profile_root):
	"""
	Finds the common denominator of the profiles in each subgroup, and bubbles
	them up.

	This makes sure that as many settings as possible have the same value as the
	setting in the parent profile. That then results in the maximum amount of
	redundancies to be removed in the ``remove_redundancies`` function.

	The provided root profile is modified to this end.
	:param profile_root: The root profile, containing all profiles as
	subprofiles.
	"""
	logging.info("Finding common denominators.")
	raise Exception("Not implemented yet.")

def remove_redundancies(profile_root):
	"""
	Removes the settings in each profile that have the same value as its parent.

	The provided root profile is modified to this end.
	:param profile_root: The root profile, containing all profiles as
	subprofiles.
	"""
	logging.info("Removing redundancies.")
	raise Exception("Not implemented yet.")

def write_profiles(output_dir, profile_root):
	"""
	Writes a profile structure to file.

	All profiles are written as the CFG file format. No other file format has
	yet been implemented due to time constraints.
	:param output_dir: The root directory to write the file structure to.
	:param profile_root: The root profile, containing all profiles as
	subprofiles.
	"""
	logging.info("Writing optimised profiles.")
	raise Exception("Not implemented yet.")

if __name__ == "__main__":
	argument_parser = argparse.ArgumentParser(description="Optimise a set of profiles for Cura.")
	argument_parser.add_argument("-i", dest="input_dir", help="Root directory of input profile structure.", default=os.getcwd())
	argument_parser.add_argument("-o", dest="output_dir", help="Root directory of output profile structure.", default=os.getcwd())
	arguments = argument_parser.parse_args()
	if arguments.input_dir == arguments.output_dir:
		raise Exception("Input and output directories may not be the same (both were '{dir}').".format(dir=arguments.input_dir))
	optimise(arguments.input_dir, arguments.output_dir)