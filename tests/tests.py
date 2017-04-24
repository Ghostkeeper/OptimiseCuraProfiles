#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a metaclass for test cases that allows us to write parametrised tests.
"""

import functools #To pre-fill parameters of parametrised methods and return a partial function.

class TestMeta(type):
	"""
	Metaclass to capture all parametrised tests and duplicate them for each of
	their parameter sets.
	"""

	def __new__(mcs, name, bases, members):
		"""
		Defines a new TestCase class.

		This intercepts all tests that are parametrised and duplicates them for
		each of the sets of parameters they need to be called with.
		:param name: The name of the TestCase class.
		:param bases: The superclasses of the TestCase class.
		:param members: The members of the TestCase class, including functions.
		:return: A new TestCase class, modified for parametrised tests.
		"""
		members_copy = dict(members)
		for member in members_copy:
			if callable(members_copy[member]) and hasattr(members_copy[member], "parameters"): #It's a function that's marked with the @parametrise annotation.
				for test_name, parameters in members_copy[member].parameters.items(): #Copy the function for each set of parameters.
					new_function = functools.partialmethod(members_copy[member], **parameters) #Fill in only the parameters. The rest is filled in at calling (such as "self").
					members[member + "_" + test_name] = new_function #Store the filled-in function along with the test name to make it unique.
				del members[member] #Delete the original parametrised function.
		return type.__new__(mcs, name, bases, members)

def parametrise(parameters):
	"""
	Causes a test to run multiple times with different parameters.

	This only works for functions inside a `TestCase` class.
	:param parameters: A dictionary containing individual tests. The keys in the
	dictionary act as a name for the test, which is appended to the function
	name. The values of the dictionary are dictionaries themselves. These act as
	the parameters that are filled into the function.
	:return: A parametrised test case.
	"""
	def parametrise_decorator(original_function):
		"""
		Adds the parameters with which the test must be run to the function.
		:param original_function: The function to parametrise.
		:return: A function with the parameters attached.
		"""
		original_function.parameters = parameters
		return original_function
	return parametrise_decorator