# -*- coding: UTF-8 -*-
# 
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from trac_captcha.lib.testcase import PythonicTestCase
from trac_captcha.lib.version import Version


class VersionTest(PythonicTestCase):
    
    def test_initialize_version_with_version_numbers(self):
        version = Version(major=1, minor=0, patch_level=3)
        self.assert_equals(1, version.major)
        self.assert_equals(0, version.minor)
        self.assert_equals(3, version.patch_level)
    
    def test_knows_if_two_versions_are_equal(self):
        a_version = Version(major=1, minor=0, patch_level=3)
        self.assert_equals(a_version, a_version)
        self.assert_equals(a_version, Version(major=1, minor=0, patch_level=3))

        self.assert_false(a_version == None)
        self.assert_false(a_version == [])
        self.assert_false(a_version == Version(major=1, minor=2, patch_level=3))
    
    def test_knows_if_two_versions_are_unequal(self):
        a_version = Version(major=1, minor=0, patch_level=3)
        self.assert_false(a_version != Version(major=1, minor=0, patch_level=3))
        
        self.assert_true(a_version != [])
    
    def test_knows_if_a_version_is_older_if_major_is_lower(self):
        # bigger number should be declared first so that the object id is lower
        # otherwise this test gives a false positive
        two_point_o = Version(major=2, minor=0, patch_level=0)
        one_point_o = Version(major=1, minor=0, patch_level=0)
        
        self.assert_false(one_point_o < one_point_o)
        self.assert_false(two_point_o < one_point_o)
        self.assert_true(one_point_o < two_point_o)

        self.assert_false(one_point_o > two_point_o)
    
    def test_knows_if_a_version_is_older_if_only_minor_is_lower(self):
        # bigger number should be declared first so that the object id is lower
        # otherwise this test gives a false positive
        one_point_five = Version(major=1, minor=5, patch_level=0)
        one_point_o = Version(major=1, minor=0, patch_level=0)
        two_point_o  = Version(major=2, minor=0, patch_level=0)
        
        self.assert_false(one_point_o < one_point_o)
        self.assert_false(one_point_five < one_point_o)
        self.assert_true(one_point_o < one_point_five)
        
        self.assert_false(one_point_o > one_point_five)
        self.assert_false(one_point_five > two_point_o)
    
    def test_knows_if_a_version_is_older_if_only_patch_level_is_lower(self):
        # bigger number should be declared first so that the object id is lower
        # otherwise this test gives a false positive
        one_o_one = Version(major=1, minor=0, patch_level=1)
        one_o_two = Version(major=1, minor=0, patch_level=2)
        two_point_o  = Version(major=2, minor=0, patch_level=0)

        self.assert_false(one_o_one < one_o_one)
        self.assert_false(one_o_two < one_o_one)
        self.assert_true(one_o_one < one_o_two)

        self.assert_true(one_o_two > one_o_one)
        self.assert_true(one_o_two < two_point_o)
    
    def test_knows_if_a_version_is_newer(self):
        two_point_o = Version(major=2, minor=0, patch_level=0)
        one_point_o = Version(major=1, minor=0, patch_level=0)
        
        self.assert_false(one_point_o > two_point_o)
        self.assert_true(two_point_o > one_point_o)


