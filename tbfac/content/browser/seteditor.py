from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
import logging


logger = logging.getLogger(".SetEditor")


class SetEditor(BrowserView):
    def __call__(self):

       #get facebook's users account
        acl_users = api.portal.get_tool(name='acl_users')
        cs_facebook_users = getattr(acl_users, 'cs-facebook-users', '')
        facebookUsers = cs_facebook_users.enumerateUsers()
        users = list()
        for fbUser in facebookUsers:
            users.append(fbUser['id'])

        for userId in users:
            user = api.user.get(userid=userId)
#            user.setMemberProperties({'wysiwyg_editor': ''})



#        import pdb; pdb.set_trace()
#        members = api.user.get_users()
#        for member in members:
#            import pdb; pdb.set_trace()
#            if len(member.getRoles()) < 2 or 'Member' not in member.getRoles():
#                logger.error('id: %s , has a wrong roles setting.' % member.id)
#                member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
#                continue
#            if len(member.getRoles()) == 2:
#                member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
#            else:
#            member.setMemberProperties({'wysiwyg_editor': 'TinyMCE'})
#            member.wysiwyg_editor = "TinyMCE"
            logger.info('%s : %s : %s\n' % (user.id,
                                            user.getProperty('wysiwyg_editor', None),
                                            str(user.getRoles())))
