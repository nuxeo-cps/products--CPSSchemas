import unittest
import os, sys, stat

from Products.CPSSchemas.DiskFile import DiskFile

test_data = 'A text string for testing'

class TestDiskFile(unittest.TestCase):

    def testUploadAndAbort(self):
        df = DiskFile('id','title', storage_path='.')
        # Should return 0 before data is uploaded
        self.failUnlessEqual(df.get_size(), 0)

        # Should return file size afterwards
        df.update_data(test_data)
        self.failUnlessEqual(df.get_size(), len(test_data))

        df._abort() # To remove the temporary files

    def testUploadAndRemove(self):
        df = DiskFile('id','title', storage_path='.')
        df.update_data(test_data)
        newname = df._new_filename
        self.failUnless(os.path.exists(df.getFullFilename(newname)))

        # Transaction ends sucessfully:
        df._finish()
        # Make sure file is deleted
        self.failIf(os.path.exists(df.getFullFilename(newname)))
        # And that the correct file now exists
        self.failUnless(os.path.exists(df.getFullFilename()))
        # And has the right size (we assume that that means
        # the correct data is written to disk)
        self.failUnlessEqual(os.stat(df.getFullFilename())[stat.ST_SIZE],
            len(test_data))
        self.failUnlessEqual(df.getSize(), len(test_data))

        # And that the correct size is returned
        self.failUnlessEqual(df.get_size(), len(test_data))

        # Remove the file:
        df.manage_beforeDelete(None,None)
        self.failIf(os.path.exists(df.getFullFilename()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDiskFile))
    return suite

