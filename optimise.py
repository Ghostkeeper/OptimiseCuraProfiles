#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Optimises a set of profiles for Cura.

For usage instructions, run the script with the "--help" parameter.
"""

import argparse #To parse the input and output directories.
import configparser #To parse and write .cfg files.
import json #To parse .json files.
import logging
import os #To get the current working directory as defaults for input and output, and for file path operations.

#Global configuration stuff.
bubble_from_depth = 0
track_setting = ""
logging.basicConfig(level=logging.DEBUG)
class Profile:
	def __init__(self, filepath="Unknown", settings=None, subprofiles=None, baseconfig=None, weight=1): #The `None` are sentry values.
		if not settings:
			settings = {}
		if not subprofiles:
			subprofiles = []
		if not baseconfig:
			baseconfig = configparser.ConfigParser()
		self.filepath = filepath #Path string.
		self.settings = settings #Dictionary of settings.
		self.subprofiles = subprofiles #Set of other Profile instances.
		self.baseconfig = baseconfig #ConfigParser instance without all the settings filled in.
		self.weight = weight #How much the profile counts in the decision which is the most common value.

material_profiles = {"PLA", "ABS", "CPE", "Nylon", "PVA", "CPEP", "PC", "TPU"} #Material profiles can only have material settings. TODO: Don't hard-code these, but get them based on XML input.
material_settings = {
	"default_material_print_temperature": "print temperature",
	"material_bed_temperature": "heated bed temperature",
	"material_standby_temperature": "standby temperature",
	"material_flow_temp_graph": "processing temperature graph",
	"cool_fan_speed": "print cooling",
	"retraction_amount": "retraction amount",
	"retraction_speed": "retraction speed"
}
per_extruder_warning_settings = {"support_enable",
                                 "adhesion_extruder_nr", "support_extruder_nr", "support_infill_extruder_nr", "support_roof_extruder_nr", "support_bottom_extruder_nr", "support_extruder_nr_layer_0",
                                 "prime_tower_position_x", "prime_tower_position_y",
                                 "print_sequence",
                                 "draft_shield_enabled",
                                 "wireframe_enabled", #TODO: Wireframe
                                 #TODO: Machine settings.
                                }

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
	bubble_common_values(profile_root, bubble_from_depth)
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
	logging.info("Reading profiles in {directory}.".format(directory=input_dir))

	files = [file for file in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, file))]
	files.sort()
	directories = [directory for directory in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, directory))]
	directories.sort()

	if not files and not directories:
		raise FileNotFoundError("Input directory is empty. This is probably not what you intended.")

	#Find the base file.
	this_directory = os.path.split(input_dir)[-1]
	for file in files:
		if file.split(".")[0] == this_directory: #Named similarly.
			base_profile = parse(os.path.join(input_dir, file))
			break
	else: #There was no common file for this directory.
		base_profile = Profile(filepath=os.path.join(input_dir, this_directory + ".inst.cfg"), weight=0)

	if directories: #Not a leaf node.
		for directory in directories:
			subprofile = get_profiles(os.path.join(input_dir, directory))
			base_profile.subprofiles.append(subprofile)
			base_profile.weight += subprofile.weight
	else: #Leaf node.
		for file in files:
			if file.split(".")[0] == this_directory: #This is the parent file.
				continue
			profile = parse(os.path.join(input_dir, file)) #Act as if every file is in its own subdirectory.
			base_profile.subprofiles.append(profile)
			base_profile.weight += profile.weight

	return base_profile

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
				if key == track_setting:
					logging.debug("Flattening adds {key}.".format(key=key))
				profile.settings[key] = value

	for subprofile in profile.subprofiles:
		flatten_profiles(subprofile, profile)

def bubble_common_values(profile, bubble_from_depth):
	"""
	Finds the common denominator of the profiles in each subgroup, and bubbles
	them up.

	This makes sure that as many settings as possible have the same value as the
	setting in the parent profile. That then results in the maximum amount of
	redundancies to be removed in the ``remove_redundancies`` function.

	The provided root profile is modified to this end.
	:param profile: The root profile, containing all profiles as
	subprofiles.
	:param bubble_from_depth: How many layers of profiles below this one should
	not get bubbled.
	:param except_root: Whether we should prevent making changes to the root of
	the profile tree.
	"""
	#First tail-recursively bubble all subprofiles.
	for subprofile in profile.subprofiles:
		bubble_common_values(subprofile, bubble_from_depth - 1)
	if bubble_from_depth > 0: #We want to exempt this level from bubbling.
		return
	logging.info("Finding common denominators of {file}.".format(file=profile.filepath))
	#Edge case: No subprofiles.
	if not profile.subprofiles:
		return #We are already the common denominator then.

	#For every key, find the most common value among its children.
	for key in profile.settings:
		value_counts = {}
		if key in material_settings:
			for subprofile in profile.subprofiles:
				value = subprofile.settings[key]
				if value not in value_counts:
					value_counts[value] = 0
				value_counts[value] += subprofile.weight
		else: #Setting may not occur in a material profile. Skip all material profiles in the bubbling.
			if is_material(profile): #We can't store the setting in this profile, so don't update the profile.
				continue
			for subprofile in profile.subprofiles:
				if is_material(subprofile): #This is a material profile.
					for subsubprofile in subprofile.subprofiles: #Look in all its grandchildren. TODO: Make it possible to have multiple material profiles in the chain.
						value = subsubprofile.settings[key]
						if value not in value_counts:
							value_counts[value] = 0
						value_counts[value] += subsubprofile.weight
				else:
					value = subprofile.settings[key]
					if value not in value_counts:
						value_counts[value] = 0
					value_counts[value] += subprofile.weight
		most_common_value = None
		highest_count = -1
		for value, count in value_counts.items():
			if count > highest_count:
				most_common_value = value
				highest_count = count
			elif count == highest_count: #We have a tie.
				if value < most_common_value: #Just to make it deterministic.
					most_common_value = value
		if profile.settings[key] != most_common_value and key == track_setting:
			logging.debug("Bubbling set {key} to {value}.".format(key=key, value=most_common_value))
		profile.settings[key] = most_common_value

def remove_redundancies(profile, parent=None, grandparent=None):
	"""
	Removes the settings in each profile that have the same value as its parent.

	The provided root profile is modified to this end.
	:param profile: The profile to remove redundancies from, containing all
	profiles as subprofiles.
	:param parent: The parent profile of the specified profile, if any.
	:param grandparent: The grandparent profile of the specified profile, if
	any.
	"""
	#First tail-recursively remove redundancies of all subprofiles.
	for subprofile in profile.subprofiles:
		remove_redundancies(subprofile, parent=profile, grandparent=parent)
	logging.info("Removing redundancies of {file}.".format(file=profile.filepath))
	#Edge case: Root file has no redundancies.
	if not parent:
		return

	#Remove settings that are the same as the parent.
	redundancies = set()
	for key in profile.settings:
		temp_parent = parent
		if key not in material_settings and is_material(parent) and grandparent:
			temp_parent = grandparent
		if key not in material_settings and is_material(profile):
			if key == track_setting:
				logging.debug("Removed redundant {key} (non-material setting).".format(key=key))
			redundancies.add(key)
			continue
		if profile.settings[key] == temp_parent.settings[key]:
			if key == track_setting:
				logging.debug("Removed redundant {key} (same as parent: {value} vs {parent_value})".format(key=key, value=profile.settings[key], parent_value=temp_parent.settings[key]))
			redundancies.add(key)
			continue
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

def is_material(profile):
	"""
	Determines whether a profile is a material profile.
	:param profile: The profile to check.
	:return: True if the profile is a material profile, or False if it isn't.
	"""
	return os.path.split(profile.filepath)[-1].split(".")[0] in material_profiles

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
	if extension == ".fdm_material":
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
	result = Profile(filepath=file) #An empty profile.

	data = configparser.ConfigParser() #Input file.
	data.read(file)
	if data.has_section("general"): #Copy over all metadata.
		result.baseconfig["general"] = data["general"]
	if data.has_section("metadata"):
		result.baseconfig["metadata"] = data["metadata"]
	if data.has_section("values"): #Put the settings in the settings dict for further processing later.
		for key, value in data["values"].items():
			if key == track_setting:
				logging.debug("Loading {key} from {file}: {value}.".format(key=key, value=value, file=file))
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
	result = Profile(filepath=file) #An empty profile.
	with open(file) as json_file:
		data = json.load(json_file)

	if "settings" in data:
		for key, value in parse_json_setting(data["settings"]):
			if key == track_setting:
				logging.debug("Loading {key} from {file}: {value}.".format(key=key, value=value, file=file))
			result.settings[key] = value
	if "overrides" in data:
		for key, value in parse_json_setting(data["overrides"]):
			if key == track_setting:
				logging.debug("Loading {key} from {file}: {value}.".format(key=key, value=value, file=file))
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
		if "value" in subdict:
			yield key, "=" + str(subdict["value"])
		elif "default_value" in subdict: #default_value overrides value.
			yield key, str(subdict["default_value"])

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

	if config.has_section("metadata") and config["metadata"]["type"] == "quality":
		warning_settings = per_extruder_warning_settings & profile.settings.keys()
		if warning_settings:
			logging.warning("These settings may give problems in the profile {profile}: {settings}".format(profile=profile.filepath, settings=warning_settings))

	config.add_section("values")
	for key in sorted(profile.settings): #Serialise the settings to the config.
		if key in material_settings and is_material(profile):
			config["values"][material_settings[key]] = profile.settings[key]
		else:
			config["values"][key] = profile.settings[key]

	if not os.path.exists(os.path.dirname(os.path.join(output_dir, profile.filepath))):
		os.makedirs(os.path.dirname(os.path.join(output_dir, profile.filepath)))
	with open(os.path.join(output_dir, profile.filepath), "w") as config_file: #Write the config file itself.
		config.write(config_file)

if __name__ == "__main__":
	argument_parser = argparse.ArgumentParser(description="Optimise a set of profiles for Cura.")
	argument_parser.add_argument("-i", dest="input_dir", help="Root directory of input profile structure.", default=os.getcwd())
	argument_parser.add_argument("-o", dest="output_dir", help="Root directory of output profile structure.", default=os.getcwd())
	argument_parser.add_argument("-b", dest="bubble_from_depth", help="How many levels of profiles to retain. These levels will remain unmodified by bubbling. Set to 0 to bubble settings all the way up to fdmprinter, or 1 to exclude just fdmprinter. Set it very high to prevent bubbling at all.", default="1")
	argument_parser.add_argument("--track", dest="track_setting", help="To debug. Logs messages whenever the specified setting key is touched.", default="")
	arguments = argument_parser.parse_args()
	if arguments.input_dir == arguments.output_dir:
		raise Exception("Input and output directories may not be the same (both were \"{dir}\").".format(dir=arguments.input_dir))
	bubble_from_depth = int(arguments.bubble_from_depth)
	track_setting = arguments.track_setting
	optimise(arguments.input_dir, arguments.output_dir)