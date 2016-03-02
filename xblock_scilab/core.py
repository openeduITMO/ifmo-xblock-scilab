# -*- coding: utf-8 -*-

from django.core.files.base import File
from django.core.files.storage import default_storage
from ifmo_celery_grader.models import GraderTask
from webob.response import Response
from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock_ifmo.utils import now
from xblock_ifmo.xblock_ifmo import IfmoXBlock
from xblock_ifmo.xblock_xqueue import XBlockXQueueMixin
from xblock_ifmo.xblock_ajax import AjaxHandlerMixin
from xblock_scilab.models import ScilabSubmission
from xblock_scilab.utils import get_sha1, file_storage_path
from submissions import api as submissions_api
from base64 import b64encode


from .fields import ScilabXBlockFields



import json
import mimetypes


class ScilabXBlock(ScilabXBlockFields, XBlockXQueueMixin, IfmoXBlock):

    package = __package__

    # Use this unless submissions api is used
    # always_recalculate_grades = True

    def student_view(self, context):

        if context is None:
            context = dict()

        student_context = self.get_student_context()

        fragment = Fragment()
        fragment.add_content(self.load_template('xblock_scilab/student_view.html', student_context))
        fragment.add_css(self.load_css('student_view.css'))
        fragment.add_javascript(self.load_js('student_view.js'))
        fragment.initialize_js('ScilabXBlockStudentView')

        return super(ScilabXBlock, self).student_view_base(fragment, context, student_context)

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

    def get_student_context(self, user=None):
        # TODO: Parents should declare what they provide for student context
        context = {
            'allow_submissions': True if self.due is None or now() > self.due else False,
            'task_status': self.task_state,
        }
        if self.message is not None:
            context.update({
                'message': {
                    'text': self.message,
                    'type': 'info',
                }
            })
        return context

    def _get_instructor_context(self):
        # TODO: Parents should declare what they provide for instructor context
        return {
            'id': self.scope_ids.usage_id,
            'metadata': json.dumps({
                'display_name': self.display_name,
                'description': self.description,
                'weight': self.weight,
                'attempts': self.attempts,
                'queue_name': self.queue_name,
            }),
        }

    #==================================================================================================================#

    @XBlock.json_handler
    def save_settings(self, data, suffix):
        result = super(ScilabXBlock, self).save_settings(data)
        return result

    @XBlock.json_handler
    def user_state(self, data, suffix=''):
        # TODO: Do user_state more like save_settings
        return self.get_response_user_state(self.get_student_context())

    def student_submission_id(self, submission_id=None):
        # pylint: disable=no-member
        """
        Returns dict required by the submissions app for creating and
        retrieving submissions for a particular student.
        """
        if submission_id is None:
            submission_id = self.xmodule_runtime.anonymous_student_id
            assert submission_id != (
                'MOCK', "Forgot to call 'personalize' in test."
            )
        return {
            "student_id": submission_id,
            "course_id": self.course_id,
            "item_id": self.location.block_id,
            "item_type": 'scilab_xblock',  # ???
        }

    @XBlock.handler
    def upload_submission(self, request, suffix):

        def _return_response(response_update):
            response = self.get_student_context()
            response.update(response_update)
            return self.get_response_user_state(response)

        if self.celery_task_id is not None:
            task = GraderTask.objects.get(task_id=self.celery_task_id)
            if task.task_state not in ScilabSubmission.IDLE_STATUSES:
                return _return_response({
                    'message': {
                        'text': 'Проверка другого решения уже запущена.',
                        'type': 'error',
                    }
                })

        try:
            # Извлечение данных о загруженном файле
            upload = request.params['submission']
            uploaded_file = File(upload.file)
            uploaded_filename = upload.file.name
            uploaded_sha1 = get_sha1(upload.file)
            uploaded_mimetype = mimetypes.guess_type(upload.file.name)[0]

            # Реальные названия файлов в ФС
            real_path = file_storage_path(self.location, uploaded_sha1, uploaded_filename)
            instructor_real_path = file_storage_path(self.location, 'instructor_checker', 'instructor_checker.zip')

            # Сохраняем данные о решении
            student_id = self.student_submission_id()
            student_answer = {
                "sha1": uploaded_sha1,
                "filename": uploaded_filename,
                "mimetype": uploaded_mimetype,
                "real_path": real_path,
                "instructor_real_path": instructor_real_path,
            }
            submission = submissions_api.create_submission(student_id, student_answer)

            # Сохраняем файл с решением
            if default_storage.exists(real_path):
                default_storage.delete(real_path)
            default_storage.save(real_path, uploaded_file)

            # Отправляем решение в очередь
            self.task_state = 'QUEUED'

            payload = {
                'student_info': self.get_queue_student_info(),
                'grader_payload': '',
                'student_response': self.get_queue_student_response(submission),
            }

            qinterface = self.get_queue_interface()
            qinterface.send_to_queue(header=self.get_submission_header(prefix=submission.get('uuid')),
                                     body=json.dumps(payload),)

            # task = reserve_task(
            #     self,
            #     grader_payload=self._get_grader_payload(instructor_real_path),
            #     system_payload=self._get_system_payload(),
            #     student_input=self._get_student_input(submission),
            #     task_type='SCILAB_CHECK',
            #     save=True,
            # )
            # submit_task_grade(ScilabSubmissionGrade, task)

        except Exception as e:
            return _return_response({
                'message': {
                    'text': 'Ошибка при попытке поставить проверку решения в очередь: ' + e.message,
                    'type': 'error',
                }
            })

        return _return_response({
            'message': {
                'text': 'Решение поставлено в очередь на проверку.',
                'type': 'info',
            }
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

    @XBlock.handler
    def get_submitted_archives(self, request, suffix):

        def get_64_contents(filename):
            with default_storage.open(filename, 'r') as f:
                return b64encode(f.read())

        # user_id = request.params['anonymous_user_id']
        user_id = suffix
        user_id = self.student_submission_id(submission_id=user_id)
        submission = submissions_api.get_submission(user_id.get('student_id'))
        answer = submission['answer']
        return Response(json_body={
            'user_archive_name': answer.get('real_path'),
            'user_archive': get_64_contents(answer.get('real_path')),
            'instructor_archive_name': answer.get('instructor_real_path'),
            'instructor_archive': get_64_contents(answer.get('instructor_real_path')),
        })

    def get_queue_student_response(self, submission):
        # TODO: Protect this with hash
        base_url = self.runtime.handler_url(self, 'get_submitted_archives', thirdparty=True)
        return json.dumps({
            'archive_64_url': base_url + '/' + submission.get('uuid'),
        })

    @AjaxHandlerMixin.xqueue_callback
    def score_update(self, submission_result):

        parent = super(ScilabXBlock, self)
        if hasattr(parent, 'score_update'):
            parent.score_update(submission_result)

        submission_uid, validation_key = submission_result.lms_key.split('+')

        # TODO: Validate submission
        # submission = submissions_api.get_submission(submission_uid)

        submissions_api.set_score(submission_uid, int(100*submission_result.score), 100)

        self.points = submission_result.score
        self.task_state = 'IDLE'
        self.runtime.publish(self, 'grade', {
                'value': submission_result.score * self.max_score(),
                'max_value': self.max_score()
        })
