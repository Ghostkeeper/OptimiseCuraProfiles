#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import configparser #To generate custom profiles and initialise them with a configparser.
import os.path #To get a directory with test files.
import tempfile #To create a temporary empty directory. You can't have empty directory in Git.
import unittest #The testing suite.

import optimise #The module we're testing.
import tests.tests #To allow parametrised tests.

class TestOptimise(unittest.TestCase, metaclass=tests.tests.TestMeta):
	"""
	Tests the components of the optimise script.
	"""

	data_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_data")
	"""
	A data directory to load test files from.
	"""

	def test_get_profiles_filepath(self):
		"""
		Tests whether the file path is stored correctly in the profiles.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(profile.filepath, os.path.join(input_directory, "simple_tree.inst.cfg"), "The file is in simple_tree/simple_tree.inst.cfg.")

	def test_get_profiles_children(self):
		"""
		Tests whether the children are properly found when loading profiles.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(len(profile.subprofiles), 1, "There is only one child, 'subdirectory'.")
		self.assertEqual(profile.subprofiles[0].filepath, os.path.join(input_directory, "subdirectory", "subdirectory.inst.cfg"), "The child is in the test_data/subdirectory/subdirectory.inst.cfg file.")

	def test_get_profiles_grandchildren(self):
		"""
		Tests whether the grandchildren are properly found when loading
		profiles.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(len(profile.subprofiles[0].subprofiles), 2, "There are two grandchildren under the 'subdirectory' directory.")
		self.assertEqual(profile.subprofiles[0].subprofiles[0].filepath, os.path.join(input_directory, "subdirectory", "leaf1.inst.cfg"), "The first grandchild is leaf1. It must be sorted.")
		self.assertEqual(profile.subprofiles[0].subprofiles[1].filepath, os.path.join(input_directory, "subdirectory", "leaf2.inst.cfg"), "The second grandchild is leaf2. It must be sorted.")

	def test_get_profiles_weight(self):
		"""
		Tests whether loaded profiles get assigned the correct weights.

		The weight of a profile should indicate the number of profiles it
		encompasses.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(profile.weight, 4, "There is the root test data, the subdirectory, leaf1 and leaf2.")
		self.assertEqual(profile.subprofiles[0].weight, 3, "There is the subdirectory, leaf1 and leaf2.")
		self.assertEqual(profile.subprofiles[0].subprofiles[0].weight, 1, "Just leaf1.")
		self.assertEqual(profile.subprofiles[0].subprofiles[1].weight, 1, "Just leaf2.")

	def test_get_profiles_settings(self):
		"""
		Tests whether loaded profiles have the correct settings.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(profile.settings["apples"], "3", "Apples is set to 3 in simple_tree.inst.cfg.")
		self.assertEqual(profile.settings["oranges"], "5", "Oranges is set to 5 in simple_tree.inst.cfg.")
		self.assertEqual(profile.settings["bananas"], "-1", "Bananas is set to -1 in simple_tree.inst.cfg.")
		self.assertEqual(profile.subprofiles[0].settings["apples"], "4", "Apples is overridden to 4 in subprofile.inst.cfg.")
		self.assertEqual(profile.subprofiles[0].subprofiles[0].settings["apples"], "5", "Apples is overridden to 5 in leaf1.inst.cfg.")
		self.assertEqual(profile.subprofiles[0].subprofiles[1].settings["apples"], "6", "Apples is overridden to 6 in leaf2.inst.cfg.")

	def test_get_profiles_empty_directory(self):
		"""
		Tests getting profiles from a directory that is empty.
		"""
		temporary_directory = tempfile.TemporaryDirectory()
		with self.assertRaises(FileNotFoundError):
			optimise.get_profiles(temporary_directory.name) #Because it's an empty directory.

	def test_flatten_profiles_empty(self):
		"""
		Tests flattening an empty profile.
		"""
		profile = optimise.Profile(filepath="<string>", settings={}, subprofiles=set(), baseconfig=configparser.ConfigParser(), weight=1) #Nothing in it.
		optimise.flatten_profiles(profile) #No parent.
		self.assertDictEqual(profile.settings, {}, "Flattened settings must still be empty.")

	def test_flatten_profiles_merge(self):
		"""
		Tests flattening a profile that inherits one setting from a parent but
		overwrites another setting.
		"""
		child = optimise.Profile(filepath="<string>", settings={"apples": 4}, subprofiles=set(), baseconfig=configparser.ConfigParser(), weight=1)
		parent = optimise.Profile(filepath="<string>", settings={"apples": 3, "pears": 8}, subprofiles={child}, baseconfig=configparser.ConfigParser(), weight=2)
		optimise.flatten_profiles(parent)
		self.assertDictEqual(child.settings, {"apples": 4, "pears": 8}, "The apples are overwritten but the pears are inheriting from the parent.")

	def test_flatten_profiles_override(self):
		"""
		Tests flattening a profile that overrides all its parent's settings.

		The result is that the profile is unchanged, since it was already flat.
		"""
		child = optimise.Profile(filepath="<string>", settings={"apples": 4}, subprofiles=set(), baseconfig=configparser.ConfigParser(), weight=1)
		parent = optimise.Profile(filepath="<string>", settings={"apples": 3}, subprofiles={child}, baseconfig=configparser.ConfigParser(), weight=2)
		optimise.flatten_profiles(parent)
		self.assertDictEqual(child.settings, {"apples": 4}, "The child profile must retain its overwriting value for apples=4.")

	def test_flatten_profiles_root(self):
		"""
		Tests flattening a profile that is already the root.

		It shouldn't change the profile in any way, then.
		"""
		subprofile = optimise.Profile(filepath="<string>", settings={"apples": 3}, subprofiles=set(), baseconfig=configparser.ConfigParser(), weight=1)
		profile = optimise.Profile(filepath="<string>", settings={"foo": "bar"}, subprofiles={subprofile}, baseconfig=configparser.ConfigParser(), weight=2)
		optimise.flatten_profiles(profile)
		self.assertDictEqual(profile.settings, {"foo": "bar"}, "The root profile must not be altered.")

	def test_flatten_profiles_transparent(self):
		"""
		Tests flattening an empty profile with a parent that's not empty.

		All settings of the parent must be included in the originally empty
		profile.
		"""
		empty_profile = optimise.Profile(filepath="<string>", settings={}, subprofiles=set(), baseconfig=configparser.ConfigParser(), weight=1)
		parent_profile = optimise.Profile(filepath="<string>", settings={"foo": "bar"}, subprofiles={empty_profile}, baseconfig=configparser.ConfigParser(), weight=2)
		optimise.flatten_profiles(parent_profile)
		self.assertDictEqual(empty_profile.settings, {"foo": "bar"}, "Flattened profile must now have all settings from its parents.")

	@tests.tests.parametrise({
		"empty": {
			"json_file": "empty.def.json",
			"settings": {}
		},
		"just_setting_values": {
			"json_file": "just_setting_values.def.json",
			"settings": {"foo": "=3", "bar": "='bar'", "is_giraffe": "=True"} #Should add = before each value.
		},
		"just_setting_defaults": {
			"json_file": "just_setting_defaults.def.json",
			"settings": {"foo": "3", "bar": "bar", "is_giraffe": "True"}
		},
		"just_overrides": {
			"json_file": "just_overrides.def.json",
			"settings": {"bla": "=8", "sla": "3.14"}
		},
		"settings_and_overrides": {
			"json_file": "settings_and_overrides.def.json",
			"settings": {"foo": "=3", "bar": "=1"}
		},
		"colliding_settings_overrides": {
			"json_file": "colliding_settings_overrides.def.json",
			"settings": {"foo": "=1"} #Overrides wins.
		},
		"children": {
			"json_file": "children.def.json",
			"settings": {"grandparent": "=102", "parent": "=75", "child": "=39", "grandchild": "=12"} #All flattened.
		},
		"weird_names": {
			"json_file": "weird_names.def.json",
			"settings": {"value": "3", "default_value": "4", "": "5", " ": "6", "hè?": "7"}
		}
	})
	def test_parse_json(self, json_file, settings):
		"""
		Tests whether JSON files are correctly parsed.
		:param json_file: The file to test parsing, relative to the test data
		directory.
		:param settings: A dictionary that specifies for each key that should be
		found what value should be found.
		"""
		json_file = os.path.join(self.data_directory, json_file)
		profile = optimise.parse_json(json_file)
		self.assertDictEqual(profile.settings, settings)

	@tests.tests.parametrise({
		"empty": {
			"cfg_file": "empty.inst.cfg",
			"settings": {} #Should not give an error that the 'values' section could not be found!
		},
		"simple": {
			"cfg_file": "simple.inst.cfg",
			"settings": {"foo": "bar"}
		},
		"multiple": {
			"cfg_file": "multiple.inst.cfg",
			"settings": {"foo": "3", "bar": "4"}
		}
	})
	def test_parse_cfg(self, cfg_file, settings):
		"""
		Tests whether CFG files are correctly parsed.
		:param cfg_file: The file to test parsing, relative to the test data
		directory.
		:param settings: A dictionary that specifies for each key that should be
		found what value should be found.
		"""
		cfg_file = os.path.join(self.data_directory, cfg_file)
		profile = optimise.parse_cfg(cfg_file)
		self.assertDictEqual(profile.settings, settings)