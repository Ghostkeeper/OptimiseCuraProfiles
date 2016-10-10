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
import configparser #To parse and write .cfg files.
import json #To parse .json files.
import logging
import os #To get the current working directory as defaults for input and output, and for file path operations.

#Global configuration stuff.
logging.basicConfig(level=logging.DEBUG)
Profile = collections.namedtuple("Profile", "filepath settings subprofiles baseconfig") #Filepath is a path string. Settings is a dictionary of settings. Subprofiles is a set of other Profile instances. Baseconfig is a configparser instance without the settings filled in.

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
	flatten_profiles(profile_root)
	bubble_common_values(profile_root)
	remove_redundancies(profile_root)
	write_profiles(output_dir, profile_root)

#################################MAIN STAGES####################################

def get_profiles(input_dir):
	"""
	Gets the profile structure described in the input directory.

	Each profile is completely flat, meaning that its settings contain every key
	known in the input directory.
	:param input_dir: The root of the input directory structure.
	:return: The root profile of the profile structure in the input directory.
	"""
	logging.info("Reading profiles.")
	call_stack = collections.deque()
	for directory, subdirectories, files in os.walk(input_dir):
		depth = len(os.path.split(directory))
		while(len(call_stack)) > depth:
			call_stack.pop()
		if subdirectories: #Not a leaf node. Look for a file that is named like the folder.
			this_directory = os.path.split(directory)[-1]
			for file in files:
				if file.split(".")[0] == this_directory: #Named similarly.
					directory_node = parse(os.path.join(directory, file))
					break
			else: #There was no common file for this directory.
				directory_node = Profile(
					filepath=os.path.join(directory, this_directory + ".inst.cfg"),
					settings={},
					subprofiles=[],
					baseconfig=configparser.ConfigParser()
				)
			if len(call_stack) > 0:
				call_stack[-1].subprofiles.append(directory_node)
			call_stack.append(directory_node)
		else: #Leaf node. Find all the rest of the profiles.
			for file in files:
				profile = parse(os.path.join(directory, file))
				if len(call_stack) > 0:
					call_stack[-1].subprofiles.append(profile)
				else:
					call_stack.append(profile) #TODO: If the root directory is a leaf file, this only returns the first file.
	return call_stack[0]

def flatten_profiles(profile, parent=None):
	"""
	Flattens a profile, instantiating all settings that it inherits from its
	parents.

	After flattening it, it will proceed to flatten all its subprofiles.
	:param profile: The profile to flatten.
	:param parent: The parent of this profile. If not provided, a copy of the
	input file is returned.
	"""
	logging.info("Flattening {file}.".format(file=profile.filepath))
	if parent:
		for key, value in parent.settings.items():
			if key not in profile.settings: #Only inherit settings that are not specified in the profile itself.
				profile.settings[key] = value

	for subprofile in profile.subprofiles:
		flatten_profiles(subprofile, profile)

def bubble_common_values(profile):
	"""
	Finds the common denominator of the profiles in each subgroup, and bubbles
	them up.

	This makes sure that as many settings as possible have the same value as the
	setting in the parent profile. That then results in the maximum amount of
	redundancies to be removed in the ``remove_redundancies`` function.

	The provided root profile is modified to this end.
	:param profile: The root profile, containing all profiles as
	subprofiles.
	"""
	#First tail-recursively bubble all subprofiles.
	for subprofile in profile.subprofiles:
		bubble_common_values(subprofile)
	logging.info("Finding common denominators of {file}.".format(file=profile.filepath))
	#Edge case: No subprofiles.
	if not profile.subprofiles:
		return #We are already the common denominator then.

	#For every key, find the most common value among its children.
	for key in profile.settings:
		value_counts = {}
		for subprofile in profile.subprofiles:
			value = subprofile.settings[key]
			if value not in value_counts:
				value_counts[value] = 0
			value_counts[value] += 1
		most_common_value = None
		highest_count = -1
		for value, count in value_counts.items():
			if count > highest_count:
				most_common_value = value
		profile.settings[key] = most_common_value

def remove_redundancies(profile, parent=None):
	"""
	Removes the settings in each profile that have the same value as its parent.

	The provided root profile is modified to this end.
	:param profile: The profile to remove redundancies from, containing all
	profiles as subprofiles.
	:param parent: The parent profile of the specified profile, if any.
	"""
	#First tail-recursively remove redundancies of all subprofiles.
	for subprofile in profile.subprofiles:
		remove_redundancies(subprofile, parent=profile)
	logging.info("Removing redundancies of {file}.".format(file=profile.filepath))
	#Edge case: Root file has no redundancies.
	if not parent:
		return

	#Remove settings that are the same as the parent.
	redundancies = set()
	for key in profile.settings:
		if profile.settings[key] == parent.settings[key]:
			redundancies.add(key)
	for key in redundancies:
		del profile.settings[key]

def write_profiles(output_dir, profile):
	"""
	Writes a profile structure to file.

	All profiles are written as the CFG file format. No other file format has
	yet been implemented due to time constraints.
	:param output_dir: The root directory to write the file structure to.
	:param profile: The root profile, containing all profiles as
	subprofiles.
	"""
	logging.info("Writing optimised profile: {file}".format(file=profile.filepath))
	write_cfg(profile, output_dir)
	for subprofile in profile.subprofiles:
		write_profiles(output_dir, subprofile)

#################################SUBROUTINES####################################

def parse(file):
	"""
	Parses one file, creating a Profile instance with all settings from the
	file.
	:param file: The file path of the file to parse.
	:return: A Profile instance, instantiated with all the settings from the
	file.
	"""
	extension = os.path.splitext(file)[1]
	if extension == ".cfg":
		return parse_cfg(file)
	if extension == ".json":
		return parse_json(file)
	if extension == ".xml":
		return parse_xml(file)
	raise Exception("Unknown file extension \"{extension}\".".format(extension=extension))

def parse_cfg(file):
	"""
	Parses a CFG file, creating a Profile instance with all settings from the
	file.
	:param file: The file path of the file to parse.
	:return: A Profile instance, instantiated with all the settings from the
	file.
	"""
	result = Profile( #An empty profile.
		filepath=file,
		settings={},
		subprofiles=[],
		baseconfig=configparser.ConfigParser()
	)

	data = configparser.ConfigParser() #Input file.
	data.read(file)
	if data.has_section("general"): #Copy over all metadata.
		result.baseconfig["general"] = data["general"]
	if data.has_section("metadata"):
		result.baseconfig["metadata"] = data["metadata"]
	if data.has_section("values"): #Put the settings in the settings dict for further processing later.
		for key, value in data["values"].items():
			result.settings[key] = value
	return result

def parse_json(file):
	"""
	Parses a JSON file, creating a Profile instance with all settings from the
	file.
	:param file: The file path of the file to parse.
	:return: A Profile instance, instantiated with all the settings from the
	file.
	"""
	result = Profile( #An empty profile.
		filepath=file,
		settings={},
		subprofiles=[],
		baseconfig=configparser.ConfigParser() #TODO: Make this base config a basic JSON file if we're going to be writing JSON as well.
	)
	with open(file) as json_file:
		data = json.load(json_file)

	if "settings" in data:
		for key, value in parse_json_setting(data["settings"]):
			result.settings[key] = value

	return result

def parse_json_setting(setting_dict):
	"""
	Parses a setting in a JSON file.
	:param setting_dict: A dictionary representing the setting as it appears in
	the JSON file.
	:return: A generator over all key-value pairs in the setting and its
	subsettings.
	"""
	for key, subdict in setting_dict.items():
		if "default_value" in subdict:
			yield key, str(subdict["default_value"])
		elif "value" in subdict: #default_value overrides value.
			yield key, str(subdict["value"])
		if "children" in subdict: #Recursively yield from child settings.
			yield from parse_json_setting(subdict["children"])

def parse_xml(file):
	"""
	Parses an XML file, creating a Profile instance with all settings from the
	file.
	:param file: The file path of the file to parse.
	:return: A Profile instance, instantiated with all the settings from the
	file.
	"""
	raise Exception("Not implemented yet.")

def write_cfg(profile, output_dir):
	"""
	Writes a CFG file from a profile.

	The file is written to the filepath specified in the profile.
	:param profile: The profile to write to a file.
	:param output_dir: The root of the output directory to write the profiles
	to.
	"""
	config = profile.baseconfig #Use the base config as starting point.
	config.add_section("values")
	for key, value in profile.settings.items(): #Serialise the settings to the config.
		config["values"][key] = value

	if not os.path.exists(os.path.dirname(os.path.join(output_dir, profile.filepath))):
		os.makedirs(os.path.dirname(os.path.join(output_dir, profile.filepath)))
	with open(os.path.join(output_dir, profile.filepath), "w") as config_file: #Write the config file itself.
		config.write(config_file)

if __name__ == "__main__":
	argument_parser = argparse.ArgumentParser(description="Optimise a set of profiles for Cura.")
	argument_parser.add_argument("-i", dest="input_dir", help="Root directory of input profile structure.", default=os.getcwd())
	argument_parser.add_argument("-o", dest="output_dir", help="Root directory of output profile structure.", default=os.getcwd())
	arguments = argument_parser.parse_args()
	if arguments.input_dir == arguments.output_dir:
		raise Exception("Input and output directories may not be the same (both were '{dir}').".format(dir=arguments.input_dir))
	optimise(arguments.input_dir, arguments.output_dir)