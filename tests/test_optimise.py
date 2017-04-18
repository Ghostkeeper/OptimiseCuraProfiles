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

	def test_get_profiles_filepath(self):
		"""
		Tests whether the file path is stored correctly in the profiles.
		"""
		profile = optimise.get_profiles(os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_data"))
		assert profile.filepath == os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_data", "test_data.inst.cfg")