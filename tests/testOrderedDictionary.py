# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.OrderedDictionary import OrderedDictionary

class OrderedDictionaryTests(unittest.TestCase):
    """Tests for OrderedDictionary"""

    def testAddRemoveItems(self):
        """Make sure items can be added and removed in the right order"""

        # This tests __init__(), __setitem__(), __delitem__()
        # keys(), items(), update()
        # __getitem__ is defined in UserDict and not overriden, and
        # therefore not tested.
        dict = OrderedDictionary()
        dict.update( {'k1': 'i1'})
        dict['k2'] = 'i2'
        dict['k3'] = 'i3'
        dict['k4'] = 'i4'
        dict.update( {'k5': 'i5'})

        self.failUnless(dict.keys() == ['k1', 'k2','k3', 'k4', 'k5' ], \
                        'Keys were not added correctly' )
        self.failUnless(dict.items() ==  [('k1', 'i1'), ('k2', 'i2'), \
                                          ('k3', 'i3'), ('k4','i4'), \
                                          ('k5', 'i5')], \
                        'Items were not added correctly' )
        del dict['k2']
        self.failUnless(dict.keys() == ['k1', 'k3', 'k4', 'k5' ], \
                        'Removal of second key failed')
        self.failUnless(dict.items() ==  [('k1', 'i1'), ('k3', 'i3'), \
                                          ('k4','i4'), ('k5', 'i5')], \
                        'Removal of second item failed')
        del dict['k1']
        self.failUnless(dict.keys() == ['k3', \
                                        'k4', 'k5' ], \
                        'Removal of first key failed')
        self.failUnless(dict.items() ==  [('k3', 'i3'), ('k4','i4'), \
                                          ('k5', 'i5')], \
                        'Removal of first item failed')
        del dict['k5']
        self.failUnless(dict.keys() == ['k3', 'k4'], \
                        'Removal of last key failed')
        self.failUnless(dict.items() ==  [('k3', 'i3'), ('k4','i4')], \
                        'Removal of last item failed')
        del dict['k4']
        del dict['k3']
        self.failUnless(dict.keys() == [], 'Emptying keys failed')
        self.failUnless(dict.items() ==  [], 'Emptying items failed')

    def testClear(self):
        """Testing clear()"""
        dict = OrderedDictionary({'k1': 'i1'})
        dict['k2'] = 'i2'
        dict['k3'] = 'i3'
        dict.clear()
        self.failUnless(len(dict) == 0, 'Clear() failed')

    def testPopItem(self):
        """Popitem should pop from end"""
        dict = OrderedDictionary({'k1': 'i1'})
        dict['k2'] = 'i2'
        dict['k3'] = 'i3'
        self.failUnless(dict.popitem() == ('k3', 'i3'), \
                        'Popitem() returned incorrect values')
        self.failUnless(dict.popitem() == ('k2', 'i2'), \
                        'Popitem() returned incorrect values')
        self.failUnless(dict.popitem() == ('k1', 'i1'), \
                        'Popitem() returned incorrect values')

    def testUpdate(self):
        """Make sure updates work as defined"""
        dict = OrderedDictionary()
        dict['k1'] = 'nope'
        dict['k1'] = 'i1'
        self.failUnless(dict['k1'] == 'i1')
        self.failUnless(dict.setdefault('k1', 'nope') == 'i1', \
                        'Setdefault overrides existing values')


    def testReorderitems(self):
        """Reordering items"""
        dict = OrderedDictionary({'k1': 'i1'})
        dict['k2'] = 'i2'
        dict['k3'] = 'i3'
        dict['k4'] = 'i4'
        dict['k5'] = 'i5'

        self.failUnless(dict.keys() == ['k1', 'k2', 'k3', 'k4', 'k5' ], \
                        'Items were not added correctly' )
        dict.order('k4', -1)
        self.failUnless(dict.keys() == ['k1', 'k2', 'k3', 'k5', 'k4' ], \
                        'Set order to last failed' )
        dict.order('k2', 6)
        self.failUnless(dict.keys() == ['k1', 'k3', 'k5', 'k4', 'k2' ], \
                        'Set order to after last failed' )
        dict.order('k4', 2)
        self.failUnless(dict.keys() == ['k1', 'k3', 'k4', 'k5', 'k2' ], \
                        'Set order to third failed' )
        dict.order('k4', 0)
        self.failUnless(dict.keys() == ['k4', 'k1', 'k3', 'k5', 'k2' ], \
                        'Set order to first failed' )
        dict.order('k4', -3)
        self.failUnless(dict.keys() == ['k1', 'k3', 'k4', 'k5', 'k2' ], \
                        'Set order to -3 failed' )
        dict.order('k4', -8)
        self.failUnless(dict.keys() == ['k4', 'k1', 'k3', 'k5', 'k2' ], \
                        'Set order to very negative failed' )
        dict.move('k5', 0)
        self.failUnless(dict.keys() == ['k4', 'k1', 'k3', 'k5', 'k2' ], \
                        'Move 0 failed' )
        dict.move('k5', -2)
        self.failUnless(dict.keys() == ['k4', 'k5', 'k1', 'k3', 'k2' ], \
                        'Negative move failed' )
        dict.move('k1', 2)
        self.failUnless(dict.keys() == ['k4', 'k5', 'k3', 'k2', 'k1' ], \
                        'Positive moveitem failed' )
        dict.move('k4', 7)
        self.failUnless(dict.keys() == ['k5', 'k3', 'k2', 'k1', 'k4' ], \
                        'Move beyond end failed' )
        dict.move('k2', -7)
        self.failUnless(dict.keys() == ['k2', 'k5', 'k3', 'k1', 'k4' ], \
                        'Move beyond beginning failed' )
        # Lastly check that values() follows keys() and that index() works
        # for all keys.
        self.failUnless(dict.values() == ['i2', 'i5', 'i3', 'i1', 'i4' ], \
                        'Values() does not have the same order as keys()')
        indexes = [dict.index('k1'), dict.index('k2'), dict.index('k3'), \
                   dict.index('k4'), dict.index('k5')]
        self.failUnless(indexes == [3,0,2,4,1], 'Index() does not follow internal order')

    def testReorderNonExistingitems(self):
        """Reordering items that does not exist should raise errors"""
        dict = OrderedDictionary({'k1': 'i1'})
        dict['k2'] = 'i2'
        self.assertRaises(ValueError, dict.order, 'k3', 7)
        self.assertRaises(ValueError, dict.move, 'k3', -2)

    def testCopy(self):
        """Perform copy"""
        dict = OrderedDictionary({'k1': 'i1'})
        dict['k2'] = 'i2'
        dict['k3'] = 'i3'
        dict['k4'] = 'i4'
        dict['k5'] = 'i5'
        copy = dict.copy()
        self.failUnless(dict == copy, 'Copy failed')
        dict['k6'] = 'i5'
        self.failIf(dict == copy, 'Copy was too shallow')


def test_suite():
    return unittest.makeSuite(OrderedDictionaryTests)

if __name__=="__main__":
    unittest.main(defaultTest)
