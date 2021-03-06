#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

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

	def test_bubble_common_values_1v1(self):
		"""
		Tests bubbling with two children, each saying something different.

		This results in a tie, so the parent should get the value that sorts
		earliest as a tie breaker.
		"""
		child1 = optimise.Profile(settings={"apples": 3})
		child2 = optimise.Profile(settings={"apples": 2})
		parent = optimise.Profile(settings={"apples": 1}, subprofiles=[child1, child2], weight=2)
		optimise.bubble_common_values(parent, 0)
		self.assertDictEqual(parent.settings, {"apples": 2}, "It's a tie between apples=2 and apples=3. The lexicographical sorting says we should pick apples=2 then.")

	def test_bubble_common_values_2v1(self):
		"""
		Tests bubbling with three children, of which two have the same value.

		Since the value of the two are more common than the value of the last
		one, the parent should take the value of the two.
		"""
		child1 = optimise.Profile(settings={"apples": 3})
		child2 = optimise.Profile(settings={"apples": 4})
		child3 = optimise.Profile(settings={"apples": 3})
		parent = optimise.Profile(settings={"apples": 2}, subprofiles=[child1, child2, child3], weight=3)
		optimise.bubble_common_values(parent, 0)
		self.assertDictEqual(parent.settings, {"apples": 3}, "The apples=3 setting is more common among its children.")

	def test_bubble_common_values_dont_include_parent(self):
		"""
		Tests whether bubbling counts the parent among the most common values.

		The parent should not be counted to determine which values are most
		common. 
		"""
		child1 = optimise.Profile(settings={"apples": 3})
		child2 = optimise.Profile(settings={"apples": 2})
		parent = optimise.Profile(settings={"apples": 3}, subprofiles=[child1, child2], weight=2)
		optimise.bubble_common_values(parent, 0)
		self.assertDictEqual(parent.settings, {"apples": 2}, "The apples=2 setting is just as common as apples=3 if you don't count the parent, and apples=2 sorts earlier.")

	def test_bubble_common_values_empty(self):
		"""
		Tests bubbling common values through profiles that are empty.

		That should obviously have no effect.
		"""
		child1 = optimise.Profile()
		child2 = optimise.Profile()
		parent = optimise.Profile(subprofiles=[child1, child2])
		optimise.bubble_common_values(parent, 0)
		self.assertDictEqual(parent.settings, {}, "The settings should still be empty after bubbling.")

	def test_bubble_common_values_materials(self):
		"""
		Tests whether bubbling skips material profiles for non-material
		settings.
		"""
		quality = optimise.Profile(settings={"material_bed_temperature": 70, "layer_height": 0.1337})
		material = optimise.Profile(settings={"material_bed_temperature": 60, "layer_height": 0.2337}, filepath="/path/to/PLA.inst.cfg", subprofiles=[quality]) #Is a material, because the file is called "PLA".
		variant = optimise.Profile(settings={"material_bed_temperature": 50, "layer_height": 0.3337}, subprofiles=[material])
		optimise.bubble_common_values(variant, 0)
		self.assertDictEqual(variant.settings, {"material_bed_temperature": 70, "layer_height": 0.1337}, "The variant should bubble all values from above.")
		self.assertDictEqual(material.settings, {"material_bed_temperature": 70, "layer_height": 0.2337}, "The material should bubble only material settings (bed temperature, not layer height).")

	def test_bubble_common_values_skip(self):
		"""
		Tests skipping up until some level of profiles.
		"""
		grandchild = optimise.Profile(settings={"apples": 3})
		child = optimise.Profile(settings={"apples": 2}, subprofiles=[grandchild])
		parent = optimise.Profile(settings={"apples": 1}, subprofiles=[child])
		optimise.bubble_common_values(parent, 1)
		self.assertDictEqual(parent.settings, {"apples": 1}, "The profile at level 0 should not be bubbled to.")
		self.assertDictEqual(child.settings, {"apples": 3}, "The profile at level 1 should be bubbled to.")

	def test_bubble_common_values_weighted(self):
		"""
		Tests whether bubbling properly takes weights of profiles into account.
		"""
		child1 = optimise.Profile(settings={"apples": 3})
		child2 = optimise.Profile(settings={"apples": 3})
		child3 = optimise.Profile(settings={"apples": 4}, weight = 3) #This is the fat kid that bullies the other ones all the time.
		parent = optimise.Profile(settings={"apples": 2}, subprofiles=[child1, child2, child3], weight=5)
		optimise.bubble_common_values(parent, 0)
		self.assertDictEqual(parent.settings, {"apples": 4}, "The profile that says that apples=4 weighs more than the other child profiles together.")

	def test_flatten_profiles_empty(self):
		"""
		Tests flattening an empty profile.
		"""
		profile = optimise.Profile()
		optimise.flatten_profiles(profile) #No parent.
		self.assertDictEqual(profile.settings, {}, "Flattened settings must still be empty.")

	def test_flatten_profiles_grandchildren(self):
		"""
		Tests whether flattening a profile has an effect through multiple layers
		of profiles.
		"""
		grandchild = optimise.Profile()
		child = optimise.Profile(subprofiles=[grandchild])
		parent = optimise.Profile(settings={"foo": "bar"}, subprofiles={child})
		optimise.flatten_profiles(parent)
		self.assertDictEqual(grandchild.settings, {"foo": "bar"}, "The foo setting must've been inherited via the child to the grandchild.")

	def test_flatten_profiles_merge(self):
		"""
		Tests flattening a profile that inherits one setting from a parent but
		overwrites another setting.
		"""
		child = optimise.Profile(settings={"apples": 4})
		parent = optimise.Profile(settings={"apples": 3, "pears": 8}, subprofiles={child})
		optimise.flatten_profiles(parent)
		self.assertDictEqual(child.settings, {"apples": 4, "pears": 8}, "The apples are overwritten but the pears are inheriting from the parent.")

	def test_flatten_profiles_override(self):
		"""
		Tests flattening a profile that overrides all its parent's settings.

		The result is that the profile is unchanged, since it was already flat.
		"""
		child = optimise.Profile(settings={"apples": 4})
		parent = optimise.Profile(settings={"apples": 3}, subprofiles={child})
		optimise.flatten_profiles(parent)
		self.assertDictEqual(child.settings, {"apples": 4}, "The child profile must retain its overwriting value for apples=4.")

	def test_flatten_profiles_root(self):
		"""
		Tests flattening a profile that is already the root.

		It shouldn't change the profile in any way, then.
		"""
		subprofile = optimise.Profile(settings={"apples": 3})
		profile = optimise.Profile(settings={"foo": "bar"}, subprofiles={subprofile})
		optimise.flatten_profiles(profile)
		self.assertDictEqual(profile.settings, {"foo": "bar"}, "The root profile must not be altered.")

	def test_flatten_profiles_transparent(self):
		"""
		Tests flattening an empty profile with a parent that's not empty.

		All settings of the parent must be included in the originally empty
		profile.
		"""
		empty_profile = optimise.Profile()
		parent_profile = optimise.Profile(settings={"foo": "bar"}, subprofiles={empty_profile})
		optimise.flatten_profiles(parent_profile)
		self.assertDictEqual(empty_profile.settings, {"foo": "bar"}, "Flattened profile must now have all settings from its parents.")

	def test_get_profiles_children(self):
		"""
		Tests whether the children are properly found when loading profiles.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(len(profile.subprofiles), 1, "There is only one child, 'subdirectory'.")
		self.assertEqual(profile.subprofiles[0].filepath, os.path.join(input_directory, "subdirectory", "subdirectory.inst.cfg"), "The child is in the test_data/subdirectory/subdirectory.inst.cfg file.")

	def test_get_profiles_empty_directory(self):
		"""
		Tests getting profiles from a directory that is empty.
		"""
		temporary_directory = tempfile.TemporaryDirectory()
		with self.assertRaises(FileNotFoundError):
			optimise.get_profiles(temporary_directory.name) #Because it's an empty directory.

	def test_get_profiles_filepath(self):
		"""
		Tests whether the file path is stored correctly in the profiles.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(profile.filepath, os.path.join(input_directory, "simple_tree.inst.cfg"), "The file is in simple_tree/simple_tree.inst.cfg.")

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

	def test_get_profiles_weight(self):
		"""
		Tests whether loaded profiles get assigned the correct weights.

		The weight of a profile should indicate the number of leaf profiles it
		encompasses.
		"""
		input_directory = os.path.join(self.data_directory, "simple_tree")
		profile = optimise.get_profiles(input_directory)
		self.assertEqual(profile.weight, 2, "Has both leaf1 and leaf2.")
		self.assertEqual(profile.subprofiles[0].weight, 2, "Still has both leaf1 and leaf2.")
		self.assertEqual(profile.subprofiles[0].subprofiles[0].weight, 1, "Just leaf1.")
		self.assertEqual(profile.subprofiles[0].subprofiles[1].weight, 1, "Just leaf2.")

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

	def test_remove_redundancies_empty(self):
		"""
		Tests removing redundant settings with empty profiles.
		"""
		child = optimise.Profile()
		parent = optimise.Profile(subprofiles=[child])
		optimise.remove_redundancies(parent)
		self.assertDictEqual(child.settings, {}, "The profile should still be empty.")

	def test_remove_redundancies_material_settings(self):
		"""
		Tests whether non-material settings ignore material profiles for
		redundancy checks.
		"""
		quality = optimise.Profile(settings={"material_bed_temperature": 60, "layer_height": 0.1337})
		material = optimise.Profile(settings={"material_bed_temperature": 70, "layer_height": 0.2337}, filepath="/path/to/PLA.inst.cfg", subprofiles=[quality])
		variant = optimise.Profile(settings={"material_bed_temperature": 60, "layer_height": 0.1337}, subprofiles=[material])
		optimise.remove_redundancies(variant)
		self.assertDictEqual(quality.settings, {"material_bed_temperature": 60}, "Bed temperature is a material setting so it should override the material. Layer height is not a material setting so it should ignore the value in the material.")

	def test_remove_redundancies_nonmaterial_settings(self):
		"""
		Tests whether non-material settings are properly removed from material
		profiles.
		"""
		material = optimise.Profile(settings={"material_bed_temperature": 60, "layer_height": 0.1337}, filepath="/path/to/PLA.inst.cfg")
		variant = optimise.Profile(settings={"material_bed_temperature": 70, "layer_height": 0.2337}, subprofiles=[material])
		optimise.remove_redundancies(variant)
		self.assertDictEqual(material.settings, {"material_bed_temperature": 60}, "Material profiles should only contain material settings.")

	def test_remove_redundancies_grandchildren(self):
		"""
		Tests removing redundant settings through multiple layers.

		If the setting gets removed in the child, that should not influence
		removing redundant settings in the grandchild.
		"""
		grandchild = optimise.Profile(settings={"apples": 3})
		child = optimise.Profile(settings={"apples": 3}, subprofiles=[grandchild])
		parent = optimise.Profile(settings={"apples": 3}, subprofiles=[child])
		optimise.remove_redundancies(parent)
		self.assertDictEqual(grandchild.settings, {}, "The grandchild apples=3 was the same as the child apples=3, even though the child setting was removed due to redundancy.")
		self.assertDictEqual(child.settings, {}, "The child apples=3 was the same as parent apples=3.")

	def test_remove_redundancies_mixed(self):
		"""
		Tests removing redundancies where only part of the settings are
		redundant.

		It shouldn't remove all of them or none, since the settings are
		redundant, not the profiles.
		"""
		child = optimise.Profile(settings={"apples": 4, "pears": 8})
		parent = optimise.Profile(settings={"apples": 3, "pears": 8}, subprofiles=[child])
		optimise.remove_redundancies(parent)
		self.assertDictEqual(child.settings, {"apples": 4}, "Apples overrides its parent, but pears was the same as its parent so pears was redundant.")

	def test_remove_redundancies_not_redundant(self):
		"""
		Tests whether it properly retains settings that are not redundant.

		The setting is not equal to the parent setting.
		"""
		child = optimise.Profile(settings={"apples": 4})
		parent = optimise.Profile(settings={"apples": 3}, subprofiles=[child])
		optimise.remove_redundancies(parent)
		self.assertDictEqual(child.settings, {"apples": 4}, "The child setting differs from its parent, so it's not redundant.")

	def test_remove_redundancies_redundant(self):
		"""
		Tests whether it removes settings that are equal to the parent setting.
		"""
		child = optimise.Profile(settings={"apples": 3})
		parent = optimise.Profile(settings={"apples": 3}, subprofiles=[child])
		optimise.remove_redundancies(parent)
		self.assertDictEqual(child.settings, {}, "The child setting is equal to its parent, so it's redundant and should be removed.")
		self.assertDictEqual(parent.settings, {"apples": 3}, "The parent setting should not get removed, since the child depends on it.")

	def test_remove_redundancies_root(self):
		"""
		Tests removing redundant settings of the root profile.

		In the root profile, no settings are redundant.
		"""
		root = optimise.Profile(settings={"foo": "bar"})
		optimise.remove_redundancies(root)
		self.assertDictEqual(root.settings, {"foo": "bar"}, "The settings of the root should be untouched.")