from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='tbfac.content',
      version=version,
      description="TBFAC Content Types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tbfac'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity [grok, relations]',
          'z3c.jbot',
          # 'plone.app.event [ploneintegration,archetypes,dexterity]',
          'plone.namedfile [blobs]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'collective.geo.bundle',
          'collective.geo.behaviour',
          'simplejson',
          'collective.geo.mapwidget',
          'geopy',
          #'plone.app.kss',
          'collective.dexteritytextindexer'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      # setup_requires=["PasteScript"],
      # paster_plugins = ["ZopeSkel"],

      )
