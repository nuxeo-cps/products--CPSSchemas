import unittest
from Products.NuxCPS3Document.Fields.BasicField import BasicField


class FieldTests(unittest.TestCase):

    def testCreation(self):
        field = BasicField('the_id')
        self.failUnless(field.id() == 'the_id', 'Id was not set correctly')


    # TODO: Test validation when that is to be implemented.
    # Skins should be implemented too, I don't know what kind of tests
    # can be done on that.

def test_suite():
    return unittest.makeSuite(FieldTests)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
