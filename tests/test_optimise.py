#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import os.path #To get a directory with test files.
import tempfile #To create a temporary empty directory. You can't have empty directory in Git.
import unittest #The testing suite.

import optimise #The module we're testing.
import tests.test_meta #To allow parametrised tests.

class TestOptimise(unittest.TestCase, metaclass=tests.test_meta.TestMeta):
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