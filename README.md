# SciLab XBlock

## Installation

### Try Out on devstack/fullstack

1. Install Package 

   installing manually for evaluation and testing:

   -  ``sudo su - edxapp -s /bin/bash``
   -  ``. edxapp_env``
   -  ``pip install -e git+https://de.ifmo.ru/scm/git/ifmo-xblock-scilab@v9.0#egg=ifmo-xblock-scilab==9.0``

2. Add edx\_sga to installed Django apps

   - In ``/edx/app/edxapp/lms.env.json`` and ``/edx/app/edxapp/cms.env.json``, add 

	 .. code:: javascript

	     "ADDL_INSTALLED_APPS": ["ifmo_xblock_scilab"],

     on the second line right after ``{``

   - In ``/edx/app/edxapp/cms.envs.json``, add

	 .. code:: javascript

          "ALLOW_ALL_ADVANCED_COMPONENTS": true,

     to the list of ``FEATURES``

3. Configure file storage

   For file storage, ScilabXBlock uses the same file storage configuration as other
   applications in edX, such as the comments server. If you change these
   settings to ScilabXBlock it will also affect those other applications.

   devstack defaults to local storage, but fullstack defaults to
   S3. To configure local storage:
   
   1. Use local storage (useful for evaluation and testing)
   
      In ``/edx/app/edxapp/edx-platform/lms/envs/aws.py`` change:
      
      .. code:: sh

          DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
      
      to:
      
      .. code:: sh

          DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
          MEDIA_ROOT = '/edx/var/edxapp/uploads'

### Production Installation

Create a branch of edx-platform to commit a few minor changes:

1. Add ScilabXBlock to the platform requirements
	
   - In ``/edx/app/edxapp/edx-platform/requirements/edx/github.txt``, add:
   
     .. code:: sh
   
          -e git+https://de.ifmo.ru/scm/git/ifmo-xblock-scilab@master#egg=ifmo-xblock-scilab

3. Enable the SGA component in LMS and Studio (CMS).

   -  In ``/edx/app/edxapp/edx-platform/cms/envs/common.py``, add ``'ifmo_xblock_scilab',`` to ``ADVANCED_COMPONENT_TYPES``: