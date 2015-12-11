# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.files.base import File
from django.core.files.storage import default_storage
from ifmo_celery_grader.models import GraderTask
from ifmo_celery_grader.tasks.helpers import reserve_task, submit_task_grade
from webob.response import Response
from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock_ifmo.xblock_ifmo import IfmoXBlock
from xblock_scilab.models import ScilabSubmission
from xblock_scilab.tasks import ScilabSubmissionGrade
from xblock_scilab.utils import get_sha1, file_storage_path


from .fields import ScilabXBlockFields

import json
import mimetypes


class ScilabXBlock(ScilabXBlockFields, IfmoXBlock):

    package = __package__

    # Use this unless submissions api is used
    always_recalculate_grades = True

    def student_view(self, context):

        if context is None:
            context = dict()

        context.update(self._get_student_context())

        fragment = Fragment()
        fragment.add_content(self.load_template('xblock_scilab/student_view.html', context))
        fragment.add_css(self.load_css('student_view.css'))
        fragment.add_javascript(self.load_js('student_view.js'))
        fragment.initialize_js('ScilabXBlockStudentView')

        return super(ScilabXBlock, self).student_view_base(fragment)

    def studio_view(self, context):

        if context is None:
            context = dict()

        context.update(self._get_instructor_context())

        fragment = Fragment()
        fragment.add_content(self.load_template('xblock_scilab/studio_view.html', context))
        fragment.add_css(self.load_css('studio_view.css'))
        fragment.add_javascript(self.load_js('studio_view.js'))
        fragment.initialize_js('ScilabXBlockStudioView')
        return fragment

    #==================================================================================================================#

    def _get_student_context(self, user=None):
        response = {
            'id': self.scope_ids.usage_id.block_id,
            'student_state': json.dumps(
                {
                    'meta': {
                        'name': self.display_name,
                        'text': self.description,
                    },
                    'score': {
                        'earned': self.points * self.weight,
                        'max': self.weight,
                        'string': self._get_score_string(),
                    },
                    'task_status': self.task_state,
                }
            ),
            'is_staff': getattr(self.xmodule_runtime, 'user_is_staff', False),

            # This is probably studio, find out some more ways to determine this
            'is_studio': self.scope_ids.user_id is None,

            'do_accept_submissions': True if self.due is None or self._now() > self.due else False,
            'due': self.due,

            'message': '',
            'message_type': '',
        }
        return response

    def _get_instructor_context(self):
        return {
            'id': self.scope_ids.usage_id,
            'metadata': json.dumps({
                'display_name': self.display_name,
                'description': self.description,
                'weight': self.weight,
            }),
        }

    #==================================================================================================================#

    @XBlock.json_handler
    def save_settings(self, data, suffix):
        result = super(ScilabXBlock, self).save_settings_base(data)
        return json.dumps(result)

    @XBlock.json_handler
    def reset_celery_task_id(self, data, suffix):
        self.celery_task_id = None
        self.task_state = ScilabSubmission.STATUS_IDLE
        return self._get_student_context()

    @XBlock.json_handler
    def user_state(self, data, suffix=''):
        pass

    @XBlock.handler
    def upload_submission(self, request, suffix):

        def _return_response(response_update):
            response = self._get_student_context()
            response.update(response_update)
            return Response(json_body=response)

        if self.celery_task_id is not None:
            task = GraderTask.objects.get(task_id=self.celery_task_id)
            if task.task_state not in ScilabSubmission.IDLE_STATUSES:
                return _return_response({
                    'message': 'Another task is already running or scheduled.',
                    'message_type': 'error',
                })

        try:
            upload = request.params['submission']
            uploaded_file = File(upload.file)
            uploaded_sha1 = get_sha1(upload.file)

            real_path = file_storage_path(
                self.location,
                uploaded_sha1,
                upload.file.name
            )

            instructor_real_path = file_storage_path(
                self.location,
                'instructor_checker',
                'instructor_checker.zip'
            )

            submission = ScilabSubmission.objects.create(
                user=User.objects.get(id=self.scope_ids.user_id),
                filename=upload.file.name,
                mimetype=mimetypes.guess_type(upload.file.name)[0],
                sha_1=uploaded_sha1,
                course=unicode(self.course_id),
                module=unicode(self.location),
                size=uploaded_file.size,
                real_filename=real_path,
                status=ScilabSubmission.STATUS_QUEUED
            )

            if default_storage.exists(real_path):
                default_storage.delete(real_path)
            default_storage.save(real_path, uploaded_file)

            task = reserve_task(
                self,
                grader_payload=self._get_grader_payload(instructor_real_path),
                system_payload=self._get_system_payload(),
                student_input=self._get_student_input(submission),
                task_type='SCILAB_CHECK',
                save=True,
            )
            submit_task_grade(ScilabSubmissionGrade, task)

        except Exception as e:
            return _return_response({
                'message': 'Error occurred while scheduling your submission: ' + e.message,
                'message_type': 'error',
            })

        return _return_response({
            'message': 'Your submission has been scheduled.',
            'message_type': 'info',
        })

    @XBlock.handler
    def upload_instructor_checker(self, request, suffix):

        upload = request.params['instructor_checker']
        uploaded_file = File(upload.file)

        real_path = file_storage_path(
            self.location,
            'instructor_checker',
            upload.file.name
        )

        if default_storage.exists(real_path):
            default_storage.delete(real_path)
        default_storage.save(real_path, uploaded_file)

        return Response(json_body={})

    def _get_grader_payload(self, instructor_checker):
        """
        Данные, завясящие исключительно от модуля, но не возволяющие идентифицировать сам модуль.
        :return:
        """
        return {
            'filename': instructor_checker,
        }

    def _get_system_payload(self):
        """
        Данные, позволяющие идентифицировать сам модуль.
        :return:
        """
        return {
            'user_id': self.scope_ids.user_id,
            'course_id': unicode(self.course_id),
            'module_id': unicode(self.location),
            'max_score': self.weight,
        }

    def _get_student_input(self, submission):
        return {
            'filename': submission.real_filename,
        }