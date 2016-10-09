#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Optimises a set of profiles for Cura.

For usage instructions, run the script without parameters.
"""

def get_input_from_parameters():
	raise Exception("Not implemented yet.")

def get_output_from_parameters():
	raise Exception("Not implemented yet.")

def optimise():
	raise Exception("Not implemented yet.")

def show_instructions():
	raise Exception("Not implemented yet.")

if __name__ == "__main__":
	input_dir = get_input_from_parameters()
	output_dir = get_output_from_parameters()
	if input_dir == output_dir:
		show_instructions()
	optimise(input_dir, output_dir)