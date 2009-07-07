# -*- coding: utf8 -*-

# Copyright 2009 Jaap Karssenberg <pardus@cpan.org>

from tests import TestCase

from zim.parsing import *

class TestParsing(TestCase):

	def testSplitWords(self):
		'''Test parsing quoted strings'''
		string = r'''"foo bar", "\"foooo bar\"" dusss ja'''
		list = ['foo bar', ',', '"foooo bar"', 'dusss', 'ja']
		result = split_quoted_strings(string)
		self.assertEquals(result, list)
		list = ['"foo bar"', ',', r'"\"foooo bar\""', 'dusss', 'ja']
		result = split_quoted_strings(string, unescape=False)
		self.assertEquals(result, list)

	def testRe(self):
		'''Test parsing Re class'''
		string = 'foo bar baz';
		re = Re('f(oo)\s*(bar)')
		if re.match(string):
			self.assertEquals(len(re), 3)
			self.assertEquals(re[0], 'foo bar')
			self.assertEquals(re[1], 'oo')
			self.assertEquals(re[2], 'bar')
		else:
			assert False, 'fail'

	def testTextBuffer(self):
		'''Test parsing TextBuffer class'''
		buffer = TextBuffer()
		buffer += ['test 123\n test !', 'fooo bar\n', 'duss']
		self.assertEqual(
			buffer.get_lines(),
			['test 123\n', ' test !fooo bar\n', 'duss\n'] )