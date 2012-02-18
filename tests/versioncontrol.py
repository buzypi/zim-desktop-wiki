# -*- coding: utf-8 -*-

# Copyright 2009 Jaap Karssenberg <jaap.karssenberg@gmail.com>

import tests

import os
import tempfile

from zim.fs import File, Dir
from zim.plugins.versioncontrol import VersionControlPlugin, NoChangesError
from zim.plugins.versioncontrol.bzr import BazaarVCS
from zim.plugins.versioncontrol.hg import MercurialVCS
from zim.plugins.versioncontrol.svn import SubversionVCS

import zim.plugins.versioncontrol.bzr
import zim.plugins.versioncontrol.hg


# We define our own tmp dir here instead of using tests.create_tmp_dir
# because sources are probably under change control already - want to
# avoid mixing up the files
def get_tmp_dir(name):
	testtmp = os.environ['TMP']
	del os.environ['TMP']
	dir = Dir(tempfile.gettempdir())
	os.environ['TMP'] = testtmp

	dir = dir.subdir('test_versioncontrol').subdir(name)
	if dir.exists():
		dir.remove_children()
		dir.remove()
	assert not dir.exists()

	return dir


@tests.slowTest
@tests.skipUnless(BazaarVCS.check_dependencies(), 'Missing dependencies')
class TestBazaar(tests.TestCase):

	def setUp(self):
		zim.plugins.versioncontrol.TEST_MODE = False

	def tearDown(self):
		zim.plugins.versioncontrol.TEST_MODE = True

	def runTest(self):
		'''Test Bazaar version control'''
		print '\n!! Some raw output from Bazaar expected here !!'

		root = get_tmp_dir('versioncontrol_TestBazaar')
		vcs = BazaarVCS(root)
		vcs.init()

		#~ for notebookdir in (root, root.subdir('foobar')):
			#~ detected = VersionControlPlugin._detect_vcs(notebookdir)
			#~ self.assertEqual(detected.__class__, BazaarVCS)
			#~ del detected # don't keep multiple instances around

		subdir = root.subdir('foo/bar')
		file = subdir.file('baz.txt')
		file.write('foo\nbar\n')

		self.assertEqual(''.join(vcs.get_status()), '''\
added:
  .bzrignore
  foo/
  foo/bar/
  foo/bar/baz.txt
''' )

		vcs.commit('test 1')
		self.assertRaises(NoChangesError, vcs.commit, 'test 1')

		ignorelines = lambda line: not (line.startswith('+++') or line.startswith('---'))
			# these lines contain time stamps
		diff = vcs.get_diff(versions=(0, 1))
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
=== added file '.bzrignore'
@@ -0,0 +1,1 @@
+**/.zim

=== added directory 'foo'
=== added directory 'foo/bar'
=== added file 'foo/bar/baz.txt'
@@ -0,0 +1,2 @@
+foo
+bar

''' )

		file.write('foo\nbaz\n')
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
=== modified file 'foo/bar/baz.txt'
@@ -1,2 +1,2 @@
 foo
-bar
+baz

''' )

		vcs.revert()
		self.assertEqual(vcs.get_diff(), ['=== No Changes\n'])

		file.write('foo\nbaz\n')
		vcs.commit_async('test 2')
		diff = vcs.get_diff(versions=(1, 2))
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
=== modified file 'foo/bar/baz.txt'
@@ -1,2 +1,2 @@
 foo
-bar
+baz

''' )

		versions = vcs.list_versions()
		#~ print 'VERSIONS>>', versions
		self.assertTrue(len(versions) == 2)
		self.assertTrue(len(versions[0]) == 4)
		self.assertEqual(versions[0][0], 1)
		self.assertEqual(versions[0][3], u'test 1\n')
		self.assertTrue(len(versions[1]) == 4)
		self.assertEqual(versions[1][0], 2)
		self.assertEqual(versions[1][3], u'test 2\n')

		lines = vcs.get_version(file, version=1)
		self.assertEqual(''.join(lines), '''\
foo
bar
''' )

		annotated = vcs.get_annotated(file)
		lines = []
		for line in annotated:
			# get rid of user name
			ann, text = line.split('|')
			lines.append(ann[0]+' |'+text)
		self.assertEqual(''.join(lines), '''\
1 | foo
2 | baz
''' )

		#~ print 'TODO - test moving a file'
		file.rename(root.file('bar.txt'))
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
=== renamed file 'foo/bar/baz.txt' => 'bar.txt'
''' )


@tests.slowTest
@tests.skipUnless(MercurialVCS.check_dependencies(), 'Missing dependencies')
class TestMercurial(tests.TestCase):

	def setUp(self):
		zim.plugins.versioncontrol.TEST_MODE = False

	def tearDown(self):
		zim.plugins.versioncontrol.TEST_MODE = True

	def runTest(self):
		'''Test Bazaar version control'''
		print '\n!! Some raw output from Bazaar expected here !!'

		root = get_tmp_dir('versioncontrol_TestMercurial')
		vcs = MercurialVCS(root)
		vcs.init()

		#~ for notebookdir in (root, root.subdir('foobar')):
			#~ detected = VersionControlPlugin._detect_vcs(notebookdir)
			#~ self.assertEqual(detected.__class__, BazaarVCS)
			#~ del detected # don't keep multiple instances around

		subdir = root.subdir('foo/bar')
		file = subdir.file('baz.txt')
		file.write('foo\nbar\n')

		self.assertEqual(''.join(vcs.get_status()), '''\
A .hgignore
A foo/bar/baz.txt
''' )

		vcs.commit('test 1')
		self.assertRaises(NoChangesError, vcs.commit, 'test 1')

		ignorelines = lambda line: not (line.startswith('+++') or line.startswith('---'))
		# these lines contain time stamps

		file.write('foo\nbaz\n')
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/foo/bar/baz.txt
@@ -1,2 +1,2 @@
 foo
-bar
+baz
''' )

		vcs.revert()
		self.assertEqual(vcs.get_diff(), ['=== No Changes\n'])

		
		file.write('foo\nbaz\n')
		vcs.commit_async('test 2') # The async operation is the same for BZR and HG, so we do not retest commit_async
		diff = vcs.get_diff(versions=(0, 1))
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/foo/bar/baz.txt
@@ -1,2 +1,2 @@
 foo
-bar
+baz
''' )

		versions = vcs.list_versions()
		#~ print 'VERSIONS>>', versions
		self.assertTrue(len(versions) == 2)
		self.assertTrue(len(versions[0]) == 4)
		self.assertEqual(versions[0][0], 0)
		self.assertEqual(versions[0][3], u'test 1\n')
		self.assertTrue(len(versions[1]) == 4)
		self.assertEqual(versions[1][0], 1)
		self.assertEqual(versions[1][3], u'test 2\n')

		
		lines = vcs.get_version(file, version=0)
		self.assertEqual(''.join(lines), '''\
foo
bar
''' )

		annotated = vcs.get_annotated(file)
		lines = []
		for line in annotated:
			# get rid of user name
			ann, text = line.split(':')
			lines.append(ann[0]+':'+text)
		self.assertEqual(''.join(lines), '''\
0: foo
1: baz
''' )

		#~ print 'TODO - test moving a file'
		file.rename(root.file('bar.txt'))
		
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/bar.txt
rename from foo/bar/baz.txt
rename to bar.txt
''' )



