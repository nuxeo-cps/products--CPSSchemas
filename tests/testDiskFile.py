import unittest
import os, sys, stat

from Products.CPSSchemas.DiskFile import DiskFile

test_data = 'A text string for testing'

class TestDiskFile(unittest.TestCase):

    def setUp(self):
        self.testdir = os.path.join(os.path.split(__file__)[0], 'diskfiletests')
        if not os.path.exists(self.testdir):
            os.mkdir(self.testdir)

    def tearDown(self):
        scories = os.listdir(self.testdir)
        for sc in scories:
            try:
                os.unlink(os.path.join(self.testdir, sc))
            except OSError:
                sys.stderr.write("Could not remove %s in testdir\n", sc)
        try:
            os.rmdir(self.testdir)
        except OSError:
            pass

    def testUploadAndAbort(self):
        df = DiskFile('id','title', storage_path=self.testdir)
        # Should return 0 before data is uploaded
        self.failUnlessEqual(df.get_size(), 0)

        # Should return file size afterwards
        df.update_data(test_data)
        self.failUnlessEqual(df.get_size(), len(test_data))
        self.failUnlessEqual(df.getData(), test_data)

        df._abort() # To remove the temporary files

    def testUploadAndRemove(self):
        df = DiskFile('id','title', storage_path=self.testdir)
        df.update_data('first write')
        name1 = df._v_tmp_filename
        df.update_data(test_data)
        newname = df._v_tmp_filename
        self.failIfEqual(newname, name1)
        self.failIf(os.path.exists(df.getFullFilename(name1)))
        self.failUnless(os.path.exists(df.getFullFilename(newname)))
        # getFullFilename always provides the current file
        self.assertEquals(df.getFullFilename(newname), df.getFullFilename())

        # passed (id, title) have been (Zope id ie field id, filename)
        # since [32951]
        self.assertEquals(df._filename, 'title')

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

        # test getData
        self.assertEquals(df.getData(), test_data)
        # This should be text/plain, so str dumps the beginning of data
        self.assertEquals(str(df), test_data)

        # Remove the file:
        df.manage_beforeDelete(None,None)
        self.failIf(os.path.exists(df.getFullFilename()))

    def test_getNewFilename(self):
        df = DiskFile('id','thesong.mp3', storage_path=self.testdir)
        df.update_data(test_data)
        newname = df._v_tmp_filename
        self.failUnless(newname.endswith('.mp3'))
        # still true after commit
        df._finish()
        self.failUnless(df.getFullFilename().endswith('.mp3'))

        # test of str.
        # could be smarter in the future. Then test should be updated
        self.assertEquals(df.content_type, 'audio/mpeg')
        self.assertEquals(str(df), "audio/mpeg content")

    def test_finish(self):
        # See #1801, second point
        df = DiskFile('id','free name', storage_path=self.testdir)
        # In the meanwhile, some other thread creates a file with exact same id
        wrong_target = os.path.join(self.testdir, 'free name')
        f = open(wrong_target, 'w')
        f.write('Some other data')
        f.close()
        # filename is computed at the end of update_data.
        # that's the best we can do, since _finish is after ZODB write
        df.update_data(test_data)

        # now our transaction comes to an end
        df._finish()
        target = df.getFullFilename()
        # our data is ok
        self.failUnlessEqual(os.stat(target)[stat.ST_SIZE], len(test_data))
        # other thread data is untouched
        f = open(wrong_target, 'r')
        self.assertEquals(f.read(), 'Some other data')
        f.close()

    def test_update(self):
        # Lower level than an user reuploading a file
        df = DiskFile('id','title', storage_path=self.testdir, file=test_data)
        df._finish()
        self.failIf(df._v_new_file)
        first_filename = df.getFullFilename()
        df.update_data('Some new data')
        df._finish()
        self.assertEquals(df.getFullFilename(), first_filename)
        f = open(os.path.join(self.testdir, first_filename))
        self.assertEquals(f.read(), 'Some new data')
        f.close()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDiskFile))
    return suite

