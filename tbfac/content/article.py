from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective import dexteritytextindexer

from tbfac.content import MessageFactory as _
from tbfac.content.info import IInfo
from Products.CMFCore.utils import getToolByName

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from plone.indexer import indexer

#for Captcha
from plone import api
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from tbfac.newcontent.profile import IProfile


"""
def constraintAuthor(value):
    if value is not None and != ''
        return True
    elif not api.user.is_anonymous():
        return True
    elif value is None or value == '':
        raise Invalid(_(u"Please fill in author name"))
"""
def back_references(source_object, attribute_name):
    """Return back references from source object on specified attribute_name.
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    result = []
    for rel in catalog.findRelations(
                   dict(to_id=intids.getId(aq_inner(source_object)),
                        from_attribute=attribute_name)
               ):
        obj = intids.queryObject(rel.from_id)
        if obj is not None and checkPermission('zope2.View', obj):
            result.append(obj)
    return result


class CaptchaError(Invalid):
    __doc__ = _(u"Captcha error, plaease try again.")

class IArticle(form.Schema, IImageScaleTraversable):
    """
    TBFAC Article Type
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/article.xml to define the content type
    # and add directives here as necessary.
    
    #form.model("models/article.xml")

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"Title"),
    )


### related profile
#    form.widget(info_ref=AutocompleteMultiFieldWidget)
    form.mode(relatedProfile="hidden")
    relatedProfile = RelationChoice(
        title=_(u"Related Profile"),
        source=ObjPathSourceBinder(
            object_provides=IProfile.__identifier__,
            ),
        required=False,
    )


    dexteritytextindexer.searchable('author')
#    dexterity.read_permission(author='cmf.ManagePortal') Add portal member
#    dexterity.write_permission(author=checkAnonymous)
    author = schema.TextLine(
        title=_(u"Author"),
        default=_(u"author name"),
        required=False,
#        constraint=constraintAuthor,
    )

    form.widget(info_ref=AutocompleteMultiFieldWidget)
    info_ref = RelationList(
        title=_(u"Referenced Info"),
        description=_(u"If no referenced Info items to select, please manually fill them in the next field."),
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                object_provides=IInfo.__identifier__,
            ),
        ),
        required=False,
    )

    info_rvw = schema.TextLine(
        title=_(u"Reviewed Info"),
        description=_(u"Use comma to separate multiple Info data."),
        required=False,
    )

    dexteritytextindexer.searchable('text')
    text = RichText(
        title=_(u"Body"),
        required=False,
    )


    @invariant
    def validateCaptcha(data):
        portal = api.portal.get()
        if "++add++tbfac.Article" in str(portal.REQUEST.URL):
            if not portal.restrictedTraverse('@@captcha').verify():
                raise CaptchaError(_(u"Captcha error, plaease try again."))


##### use updateWidgets to turn hidden/display
from z3c.form.interfaces import HIDDEN_MODE
class AddForm(DefaultAddForm):
    template = ViewPageTemplateFile('macrosForArticle.pt')

    def update(self):
        DefaultAddForm.update(self)

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        if not api.user.is_anonymous() and 'Manager' not in api.user.get_roles():
            self.widgets['author'].mode = HIDDEN_MODE


class AddView(DefaultAddView):
    form = AddForm



# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Article(dexterity.Item):
    grok.implements(IArticle)
    
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# article_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(grok.View):
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('view')

    def author_name(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.context.owner_info()['id'] == 'admin':
            return None
        brain = catalog({'Type':'Profile', 'Creator':self.context.owner_info()['id']})
        if not brain:
            return None
        return brain[0].Title        
    

    def update(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            self.request.set('disable_border', True)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context, domain='plonelocales')

    def relatedInfos(self):
        infos = []
        if self.context.info_ref is not None:
            for ref in self.context.info_ref:
                obj = ref.to_object
                infos.append({
                    'title': obj.title,
                })
        return infos

    def findBackReferences(self):
        backReferences = list()
        if self.context.info_ref is None:
            return backReferences
        for i in range(len(self.context.info_ref)):
            backReferences += back_references(self.context.info_ref[i].to_object, 'info_ref')
        backReferences = list(set(backReferences))
        for i in range(len(backReferences)-1, -1, -1):
            if self.context == backReferences[i]:
                backReferences.pop(i)
        return backReferences


@indexer(IArticle)
def authorName_indexer(obj):
    authorName = obj.getOwner().getProperty('fullname')
    return authorName
grok.global_adapter(authorName_indexer, name='authorName')
