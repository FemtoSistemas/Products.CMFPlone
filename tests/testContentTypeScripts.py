#
# Tests the content type scripts
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

AddPortalTopics = 'Add portal topics'
from DateTime import DateTime
from Products.CMFPlone import LargePloneFolder


#XXX NOTE
#    document, link, and newsitem edit's are now validated
#    so we must pass in fields that the validators need
#    such as title on a favorite's link_edit

class TestContentTypeScripts(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.discussion = self.portal.portal_discussion
        self.request = self.app.REQUEST

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDiscussionReply(self):
        self.folder.invokeFactory('Document', id='doc')
        # Create the talkback object
        self.discussion.overrideDiscussionFor(self.folder.doc, 1)
        self.discussion.getDiscussionFor(self.folder.doc)
        # Now test it
        self.folder.doc.discussion_reply('Foo', 'blah')
        talkback = self.discussion.getDiscussionFor(self.folder.doc)
        reply = talkback.objectValues()[0]
        self.assertEqual(reply.Title(), 'Foo')
        self.assertEqual(reply.EditableBody(), 'blah')

    def testDocumentCreate(self):
        self.folder.invokeFactory('Document', id='doc', text='data')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/plain')

    def testDocumentEdit(self):
        self.folder.invokeFactory('Document', id='doc')
        self.folder.doc.document_edit('html', 'data', title='Foo')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/html')
        self.assertEqual(self.folder.doc.Title(), 'Foo')

    def testEventCreate(self):
        self.folder.invokeFactory('Event', id='event',
                                  title = 'Foo',
                                  start_date='2003-09-18',
                                  end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.assertEqual(self.folder.event.start().ISO(), '2003-09-18 00:00:00')
        self.assertEqual(self.folder.event.end().ISO(), '2003-09-19 00:00:00')

    def testEventEdit(self):
        self.folder.invokeFactory('Event', id='event')
        self.folder.event.event_edit(title='Foo',
                                     start_date='2003-09-18',
                                     end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.assertEqual(self.folder.event.start().ISO(), '2003-09-18 00:00:00')
        self.assertEqual(self.folder.event.end().ISO(), '2003-09-19 00:00:00')

    def testFavoriteCreate(self):
        # Ugh, addFavorite traverses to remote_url, so make sure it can.
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', id='bar')
        self.portal.bar.invokeFactory('Document', id='baz.html')
        self.setRoles(['Member'])
        # back to normal
        self.folder.invokeFactory('Favorite', id='favorite',
                                  remote_url='bar/baz.html',
                                  title='Foo')
        self.assertEqual(self.folder.favorite.getRemoteUrl(),
                         '%s/bar/baz.html' % self.portal.portal_url())
        self.assertEqual(self.folder.favorite.Title(), 'Foo')

    def testFavoriteEdit(self):
        # Note: link_edit does not traverse to remote_url
        self.folder.invokeFactory('Favorite', id='favorite')
        self.folder.favorite.link_edit('bar/baz.html', title='Foo')
        self.assertEqual(self.folder.favorite.getRemoteUrl(),
                         '%s/bar/baz.html' % self.portal.portal_url())
        self.assertEqual(self.folder.favorite.Title(), 'Foo')

    def testFileCreate(self):
        self.folder.invokeFactory('File', id='file', file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testFileEdit(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.file_edit(file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageCreate(self):
        self.folder.invokeFactory('Image', id='image', file=dummy.File())
        self.assertEqual(str(self.folder.image.data), dummy.TEXT)

    def testImageEdit(self):
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.image_edit(file=dummy.File())
        self.assertEqual(str(self.folder.image.data), dummy.TEXT)

    def testFolderCreate(self):
        self.folder.invokeFactory('Folder', id='folder', title='Foo', description='Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')

    def testFolderEdit(self):
        self.folder.invokeFactory('Folder', id='folder')
        self.folder.folder.folder_edit('Foo', 'Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')

    def testLargePloneFolderCreate(self):
        LargePloneFolder.addLargePloneFolder(self.folder, id='lpf', title='Foo', description='Bar')
        self.assertEqual(self.folder.lpf.Title(), 'Foo')
        self.assertEqual(self.folder.lpf.Description(), 'Bar')

    def testLargePloneFolderEdit(self):
        LargePloneFolder.addLargePloneFolder(self.folder, id='lpf')
        self.folder.lpf.folder_edit('Foo', 'Bar')
        self.assertEqual(self.folder.lpf.Title(), 'Foo')
        self.assertEqual(self.folder.lpf.Description(), 'Bar')

    def testLinkCreate(self):
        self.folder.invokeFactory('Link', id='link', remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testLinkEdit(self):
        self.folder.invokeFactory('Link', id='link')
        self.folder.link.link_edit('http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemCreate(self):
        self.folder.invokeFactory('News Item', id='newsitem', text='data', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    def testNewsItemEdit(self):
        self.folder.invokeFactory('News Item', id='newsitem')
        self.folder.newsitem.newsitem_edit('data', 'plain', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    def testTopicCreate(self):
        self.folder.invokeFactory('Topic', id='topic', title='Foo')
        self.assertEqual(self.folder.topic.Title(), 'Foo')

    def testTopicEditTopic(self):
        self.folder.invokeFactory('Topic', id='topic')
        self.folder.topic.topic_editTopic(1, 'topic', title='Foo')
        self.assertEqual(self.folder.topic.Title(), 'Foo')

    #def testTopicEditCriteria(self):
    #    self.folder.invokeFactory('Topic', id='topic')
    #    # TODO: Analyze that funky data structure

    # Bug tests

    def testClearImageTitle(self):
        # Test for http://plone.org/collector/3303
        # Should be able to clear Image title
        self.folder.invokeFactory('Image', id='image', title='Foo', file=dummy.Image())
        self.assertEqual(self.folder.image.Title(), 'Foo')
        self.folder.image.image_edit(title='')
        self.assertEqual(self.folder.image.Title(), '')
 

class TestEditShortName(PloneTestCase.PloneTestCase):
    # Test fix for http://plone.org/collector/2246
    # Short name should be editable without specifying a file.

    def afterSetUp(self):
        self.folder.invokeFactory('File', id='file', file=dummy.File())
        self.folder.invokeFactory('Image', id='image', file=dummy.File())

    def testFileEditNone(self):
        self.folder.file.file_edit(file=None, title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageEditNone(self):
        self.folder.image.image_edit(file=None, title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.image.data), dummy.TEXT)

    def testFileEditEmptyString(self):
        self.folder.file.file_edit(file='', title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageEditEmptyString(self):
        self.folder.image.image_edit(file='', title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.image.data), dummy.TEXT)

    def testFileEditString(self):
        self.folder.file.file_edit(file='foo')
        self.assertEqual(str(self.folder.file), 'foo')

    def testImageEditString(self):
        self.folder.image.image_edit(file='foo')
        self.assertEqual(str(self.folder.image.data), 'foo')

    def testFileEditShortName(self):
        get_transaction().commit(1) # make rename work
        self.folder.file.file_edit(id='fred')
        self.failUnless('fred' in self.folder.objectIds())

    def testImageEditShortName(self):
        get_transaction().commit(1) # make rename work
        self.folder.image.image_edit(id='fred')
        self.failUnless('fred' in self.folder.objectIds())


class TestEditFileKeepsMimeType(PloneTestCase.PloneTestCase):
    # Tests covering http://plone.org/collector/2792
    # Editing a file should not change MIME type

    def afterSetUp(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.file_edit(file=dummy.File('foo.pdf'))
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.image_edit(file=dummy.File('foo.gif'))

    def testFileMimeType(self):
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.content_type, 'application/pdf')

    def testImageMimeType(self):
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')

    def testFileEditKeepsMimeType(self):
        self.folder.file.file_edit(title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.content_type, 'application/pdf')

    def testImageEditKeepsMimeType(self):
        self.folder.image.image_edit(title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')

    def testFileRenameKeepsMimeType(self):
        get_transaction().commit(1) # make rename work
        self.folder.file.file_edit(id='foo')
        self.assertEqual(self.folder.foo.Format(), 'application/pdf')
        self.assertEqual(self.folder.foo.content_type, 'application/pdf')

    def testImageRenameKeepsMimeType(self):
        get_transaction().commit(1) # make rename work
        self.folder.image.image_edit(id='foo')
        self.assertEqual(self.folder.foo.Format(), 'image/gif')
        self.assertEqual(self.folder.foo.content_type, 'image/gif')


class TestFileURL(PloneTestCase.PloneTestCase):
    # Tests covering http://plone.org/collector/3296
    # file:// URLs should contain correct number of slashes
    # NOTABUG: This is how urlparse.urlparse() works.

    def testFileURLWithHost(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://foo.com/baz.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file://foo.com/baz.txt')

    def testFileURLNoHost(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file:///foo.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:///foo.txt')

    def testFileURLFourSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file:////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file://foo.com/baz.txt')

    def testFileURLFiveSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://///foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:///foo.com/baz.txt')

    def testFileURLSixSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:////foo.com/baz.txt')


class TestFileExtensions(PloneTestCase.PloneTestCase):

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def afterSetUp(self):
        self.folder.invokeFactory('File', id=self.file_id)
        self.folder.invokeFactory('Image', id=self.image_id)
        get_transaction().commit(1) # make rename work

    def testUploadFile(self):
        self.folder[self.file_id].file_edit(file=dummy.File('fred.txt'))
        self.failUnless('fred.txt' in self.folder.objectIds())

    def testUploadImage(self):
        self.folder[self.image_id].image_edit(file=dummy.File('fred.gif'))
        self.failUnless('fred.gif' in self.folder.objectIds())

    def DISABLED_testFileRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.folder[self.file_id].file_edit(id='barney')
        self.failUnless('barney.txt' in self.folder.objectIds())

    def DISABLED_testImageRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.folder[self.image_id].image_edit(id='barney')
        self.failUnless('barney.gif' in self.folder.objectIds())


class TestBadFileIds(PloneTestCase.PloneTestCase):

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def afterSetUp(self):
        self.folder.invokeFactory('File', id=self.file_id)
        self.folder.invokeFactory('Image', id=self.image_id)
        get_transaction().commit(1) # make rename work

    def testUploadBadFile(self):
        # http://plone.org/collector/3416
        self.folder[self.file_id].file_edit(file=dummy.File('fred%.txt'))
        self.failIf('fred%.txt' in self.folder.objectIds())

    def testUploadBadImage(self):
        # http://plone.org/collector/3518
        self.folder[self.image_id].image_edit(file=dummy.File('fred%.gif'))
        self.failIf('fred%.gif' in self.folder.objectIds())

    # XXX: Dang! No easy way to get at the validator state...


class TestGetObjSize(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ob = dummy.SizedItem()

    def getSize(self):
        return self.portal.getObjSize(obj=self.ob)

    def testZeroSize(self):
        self.ob.set_size(0)
        size = self.getSize()
        self.assertEquals(size, '0 kB')

    def testBytesSize(self):
        self.ob.set_size(884)
        size = self.getSize()
        self.assertEquals(size, '1 kB')

    def testKBytesSize(self):
        self.ob.set_size(1348)
        size = self.getSize()
        self.assertEquals(size, '1.3 kB')

    def testMBytesSize(self):
        self.ob.set_size(1024*1024+1024*687)
        size = self.getSize()
        self.assertEquals(size, '1.7 MB')

    def testGBytesSize(self):
        self.ob.set_size(1024*1024*1024+1024*1024*107)
        size = self.getSize()
        self.assertEquals(size, '1.1 GB')

    def testGBytesSizeFloat(self):
        # Size can be a float when files are large
        self.ob.set_size(float(1024*1024*1024+1024*1024*107))
        size = self.getSize()
        self.assertEquals(size, '1.1 GB')


class TestDefaultPage(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ob = dummy.DefaultPage()
        sp = self.portal.portal_properties.site_properties
        self.default = sp.getProperty('default_page', [])

    def getDefault(self):
        return self.portal.plone_utils.browserDefault(self.ob)

    def testDefaultPageSetting(self):
        self.assertEquals(self.default, ('index_html', 'index.html',
                                         'index.htm', 'FrontPage'))

    def testDefaultPageStringExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageStringNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))

    def testDefaultPageSequenceExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageSequenceNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))
        self.ob.keys = ['index.html']
        self.assertEquals(self.getDefault(), (self.ob, ['index.html']))
        self.ob.keys = ['index.htm']
        self.assertEquals(self.getDefault(), (self.ob, ['index.htm']))
        self.ob.keys = ['FrontPage']
        self.assertEquals(self.getDefault(), (self.ob, ['FrontPage']))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentTypeScripts))
    suite.addTest(makeSuite(TestEditShortName))
    suite.addTest(makeSuite(TestEditFileKeepsMimeType))
    suite.addTest(makeSuite(TestFileExtensions))
    suite.addTest(makeSuite(TestBadFileIds))
    suite.addTest(makeSuite(TestGetObjSize))
    suite.addTest(makeSuite(TestDefaultPage))

    # urlparse.urlparse() of Python2.1 is borked
    try:
        True
    except NameError:
        pass
    else:
        suite.addTest(makeSuite(TestFileURL))

    return suite

if __name__ == '__main__':
    framework()
