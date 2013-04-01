#!/usr/bin/env python

import sys
import unittest
sys.path.append("../")

from server.game_engine import GameEngine

class GameEngineTest(unittest.TestCase):
	"""Tests for GameEngine class"""
	def setUp(self):
		self.conf_file = "conf_test.ini"
		self.map_file = "map_test.hfm"

	def getGE(self):
		return GameEngine().init(self.conf_file, self.map_file)
		
	def test_instanciate(self):
		self.getGE()
	def test_load_config(self):
		ge = self.getGE()
		ge.conf

if __name__ == '__main__':
	unittest.main()