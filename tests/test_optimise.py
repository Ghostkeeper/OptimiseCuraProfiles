#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import os.path #To get a directory with test files.
import unittest #The testing suite.

import optimise #The module we're testing.

class TestOptimise(unittest.TestCase):
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
		profile = optimise.get_profiles(self.data_directory)
		assert profile.filepath == os.path.join(self.data_directory, "test_data.inst.cfg")

	def test_get_profiles_children(self):
		"""
		Tests whether the children are properly found when loading profiles.
		"""
		profile = optimise.get_profiles(self.data_directory)
		assert len(profile.subprofiles) == 1 #One child called 'subdirectory'.
		assert profile.subprofiles[0].filepath == os.path.join(self.data_directory, "subdirectory", "subdirectory.inst.cfg")

	def test_get_profiles_grandchildren(self):
		"""
		Tests whether the grandchildren are properly found when loading
		profiles.
		"""
		profile = optimise.get_profiles(self.data_directory)
		assert len(profile.subprofiles[0].subprofiles) == 2
		assert profile.subprofiles[0].subprofiles[0].filepath == os.path.join(self.data_directory, "subdirectory", "leaf1.inst.cfg")
		assert profile.subprofiles[0].subprofiles[1].filepath == os.path.join(self.data_directory, "subdirectory", "leaf2.inst.cfg") #Should also be sorted!

	def test_get_profiles_weight(self):
		"""
		Tests whether loaded profiles get assigned the correct weights.

		The weight of a profile should indicate the number of profiles it
		encompasses.
		"""
		profile = optimise.get_profiles(self.data_directory)
		assert profile.weight == 4 #test_data, subdirectory, leaf1 and leaf2.
		assert profile.subprofiles[0].weight == 3 #subdirectory, leaf1 and leaf2.
		assert profile.subprofiles[0].subprofiles[0].weight == 1 #Just leaf1.
		assert profile.subprofiles[0].subprofiles[1].weight == 1 #Just leaf2.

	def test_get_profiles_settings(self):
		"""
		Tests whether loaded profiles have the correct settings.
		"""
		profile = optimise.get_profiles(self.data_directory)
		assert profile.settings["apples"] == "3"
		assert profile.settings["oranges"] == "5"
		assert profile.settings["bananas"] == "-1"
		assert profile.subprofiles[0].settings["apples"] == "4"
		assert profile.subprofiles[0].subprofiles[0].settings["apples"] == "5"
		assert profile.subprofiles[0].subprofiles[1].settings["apples"] == "6"