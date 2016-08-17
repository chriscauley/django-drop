from setuptools import setup, find_packages
import os
import drop

CLASSIFIERS = [
  'Environment :: Web Environment',
  'Framework :: Django',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: BSD License',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Software Development :: Libraries :: Application Frameworks',
  'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
  author="chriscauley",
  author_email="chris@lablackey.com",
  name='django-drop',
  version=drop.__version__,
  description='An Advanced Django Drop',
  long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
  url='http://github.com/chriscauley/django-drop/',
  license='MIT License',
  platforms=['OS Independent'],
  classifiers=CLASSIFIERS,
  install_requires=[
    'Django>=1.4',
    'django-classy-tags>=0.3.3',
    'django-polymorphic>=0.2',
    'south>=0.7.2',
    'jsonfield>=0.9.6',
    'lablackey'
  ],
  packages=find_packages(exclude=["example", "example.*"]),
  include_package_data=True,
  zip_safe=False,
)
