# -*- coding: utf-8 -*-

from base64 import b64encode
from zipfile import ZipFile

import json
import mimetypes
import re

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from functools import partial
from ifmo_submissions import api as ifmo_submissions_api
from submissions import api as submissions_api
from xblock.core import XBlock
from xblock_ifmo.core import IfmoXBlock, XQueueMixin, SubmissionsMixin
from xblock_ifmo import FragmentMakoChain, xqueue_callback, now, reify_f
from xblock_ifmo import get_sha1, file_storage_path
from xmodule.util.duedate import get_extended_due_date
from xqueue_api.utils import deep_update
from xqueue_api.xblocksubmission import XBlockSubmissionResult
from webob.response import Response

from .fields import ScilabXBlockFields

BLOCK_SIZE = 8 * 1024


@XBlock.needs("user")
@IfmoXBlock.register_resource_dir()
class ScilabXBlock(ScilabXBlockFields, XQueueMixin, SubmissionsMixin, IfmoXBlock):

    xqueue_sender_name = 'ifmo_xblock_scilab'
    submission_type = "scilab_xblock"

    # Use this unless submissions api is used
    # always_recalculate_grades = True

    def student_view(self, context=None):

        if not self._is_studio() and self.need_generate \
                and not self.queue_details and not self.pregenerated:
            self.do_generate()

        if context is None:
            context = dict()

        deep_update(context, {'render_context': self.get_student_context()})

        fragment = FragmentMakoChain(base=super(ScilabXBlock, self).student_view(),
                                     lookup_dirs=self.get_template_dirs())
        fragment.add_content(self.load_template('xblock_scilab/student_view.mako'))
        fragment.add_context(context)
        fragment.add_css(self.load_css('student_view.css'))
        fragment.add_javascript(self.load_js('student_view.js'))
        fragment.initialize_js('ScilabXBlockStudentView')

        return fragment

    def studio_view(self, context=None):

        if context is None:
            context = dict()

        deep_update(context, {'render_context': self.get_settings_context()})

        fragment = FragmentMakoChain(base=super(ScilabXBlock, self).studio_view(),
                                     lookup_dirs=self.get_template_dirs())
        fragment.add_content(self.load_template('xblock_scilab/settings_view.mako'))
        fragment.add_context(context)
        fragment.add_css(self.load_css('settings_view.css'))
        fragment.add_javascript(self.load_js('settings_view.js'))
        fragment.initialize_js('ScilabXBlockSettingsView')
        return fragment

    # ================================================================================================================ #

    @reify_f
    def get_student_context(self, user=None):

        parent = super(ScilabXBlock, self)
        if hasattr(parent, 'get_student_context'):
            context = parent.get_student_context(user)
        else:
            context = {}

        # TODO: Parents should declare what they provide for student context

        # Получение пользовательского контектса и отрендеренного фрагмента не
        # очень очевидно, так как собирается в обратном порядке. По хорошему,
        # нужно переписать это под ноль.
        # С связи с этим нельзя перезаписать текст задания (он устанавливается
        # контекстом выше). Именно для этого мы заводим отдельный параметр в
        # в контексте здесь.
        context['need_generate'] = False
        pregenerated = None
        if self.need_generate:
            context['need_generate'] = True
            try:
                if self.pregenerated:
                    pregenerated = self.pregenerated.split("\n")
            except TypeError:
                pass

        context.update({
            'allow_submissions': True if (self.due is None) or (now() < get_extended_due_date(self)) else False,
            'task_status': self.queue_details.get('state', 'IDLE'),
            'pregenerated': pregenerated,
            'need_show_interface': self._is_studio() or not self.need_generate or self.pregenerated,
        })
        if self.message is not None:
            context.update({
                'message': {
                    'text': self.message,
                    'type': 'info',
                }
            })

        if self._is_staff():
            context.update({
                'instructor_archive': self.instructor_archive_meta,
            })

        return context

    def get_settings_context(self):

        context = super(ScilabXBlock, self).get_settings_context()
        deep_update(context, {
            'metadata': {
                'time_limit_generate': self.time_limit_generate,
                'time_limit_execute': self.time_limit_execute,
                'time_limit_check': self.time_limit_check,
                'instructor_archive': self.instructor_archive_meta,
            },
        })

        return context

    # ================================================================================================================ #

    @XBlock.json_handler
    def save_settings(self, data, suffix):
        result = super(ScilabXBlock, self).save_settings(data)
        self.time_limit_generate = data.get('time_limit_generate')
        self.time_limit_execute = data.get('time_limit_execute')
        self.time_limit_check = data.get('time_limit_check')

        # Извлекаем информацию об оригинальном архиве и драфте
        fs_path = self.instructor_archive_meta.get('fs_path')
        draft_fs_path = self.instructor_archive_meta.get('draft', {}).get('fs_path')

        # Сейчас оригинального файла может не существовать, поэтому вычислим его расположение

        # Перемещать нам нужно файл только если в драфте что-то есть
        storage = default_storage
        if draft_fs_path and storage.exists(draft_fs_path):

            # Удаляем существующий оригинальный файл
            # if fs_path and storage.exists(fs_path):
            #     storage.delete(fs_path)

            # Вычисляем новый адрес архива
            new_fs_path = draft_fs_path[:-len(".~draft")]

            # Сохраняем из драфта, операции move нет, поэтому только open...
            storage.save(new_fs_path, storage.open(draft_fs_path))

            # Подчищаем draft
            storage.delete(draft_fs_path)

            # Сохраняем мета-информацию о драфте
            self.instructor_archive_meta = self.instructor_archive_meta['draft']
            self.instructor_archive_meta['fs_path'] = new_fs_path

        return result

    @XBlock.json_handler
    def user_state(self, data, suffix=''):
        # TODO: Do user_state more like save_settings
        return self.get_response_user_state(self.get_student_context())

    @XBlock.handler
    def upload_submission(self, request, suffix):

        def _return_response(response_update=None):
            if response_update is None:
                response_update = {}
            response = self.get_student_context()
            response.update(response_update)
            return self.get_response_user_state(response)

        if self.queue_details:
            return _return_response({
                'message': {
                    'text': 'Проверка другого решения уже запущена.',
                    'type': 'error',
                }
            })

        try:

            self.message = None

            # Извлечение данных о загруженном файле
            upload = request.params['submission']
            uploaded_file = File(upload.file)
            uploaded_filename = upload.file.name
            uploaded_sha1 = get_sha1(upload.file)
            uploaded_mimetype = mimetypes.guess_type(upload.file.name)[0]

            # Реальные названия файлов в ФС
            fs_path = file_storage_path(self.location, uploaded_sha1)
            instructor_fs_path = self.get_instructor_path()

            # Сохраняем данные о решении
            student_id = self.student_submission_dict()
            student_answer = {
                "sha1": uploaded_sha1,
                "filename": uploaded_filename,
                "mimetype": uploaded_mimetype,
                "real_path": fs_path,
                "instructor_real_path": instructor_fs_path,
            }
            submission = submissions_api.create_submission(student_id, student_answer)

            # Сохраняем файл с решением
            if default_storage.exists(fs_path):
                default_storage.delete(fs_path)
            default_storage.save(fs_path, uploaded_file)

            payload = {
                'method': 'check',
                'student_info': self.queue_student_info,
                'grader_payload': json.dumps({
                    'pregenerated': self.pregenerated if self.need_generate else None,
                    'time_limit_execute': self.time_limit_execute,
                    'time_limit_check': self.time_limit_check,
                }),
                'student_response': self.get_queue_student_response(submission),
            }

            self.send_to_queue(
                header=self.get_submission_header(
                    access_key_prefix=submission.get('uuid'),
                ),
                body=json.dumps(payload)
            )

        except Exception as e:
            return _return_response({
                'message': {
                    'text': 'Ошибка при попытке поставить проверку решения в очередь: ' + e.message,
                    'type': 'error',
                }
            })

        return _return_response()

    @XBlock.handler
    def upload_instructor_archive(self, request, suffix):
        """
        Обработчик загрузки архива инструктора.

        Вызывается, когда в студии инструктор нажимает кнопку "Загрузить"
        напротив поля "Архив инструктора".

        Проводит валидацию архива и временно сохраняет его. Позднее, он может
        быт восстановлен обработчиком "save_settings". Защиты от параллельной
        загрузки несколькими инструкторами (или в нескольких окнах браузера)
        не предусмотрено.

        :param request:
        :param suffix:
        :return:
        """

        def get_archive_signature(archive):
            """
            Формирует подпись архива (файла) на основании sha1 и текущего времени

            :param archive: file-object
            :return: tuple(sha1, signature)
            """
            import hashlib
            import datetime
            sha1 = get_sha1(archive)
            md5 = hashlib.md5()
            md5.update(sha1)
            md5.update(datetime.datetime.isoformat(datetime.datetime.now()))
            return sha1, md5.hexdigest()

        upload = request.params['instructor_archive']

        self.validate_instructor_archive(upload.file)

        uploaded_file = File(upload.file)

        archive_sha1, archive_signature = get_archive_signature(uploaded_file)
        archive_name = "instructor.{signature}.~draft".format(name=upload.file.name, signature=archive_signature)
        fs_path = file_storage_path(self.location, archive_name)

        # Сохраняем временную информацию до того как нажата кнопка "Save"
        self.instructor_archive_meta['draft'] = {
            'filename': upload.file.name,
            'sha1': get_sha1(uploaded_file),
            'upload_at': None,
            'upload_by': None,
            'fs_path': fs_path,
        }

        if default_storage.exists(fs_path):
            default_storage.delete(fs_path)
        default_storage.save(fs_path, uploaded_file)

        return Response(json_body={})

    def _get_grader_payload(self, instructor_archive):
        """
        Данные, завясящие исключительно от модуля, но не возволяющие идентифицировать сам модуль.
        :return:
        """
        return {
            'filename': instructor_archive,
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

        instructor_fs_path = self.get_instructor_path()

        response = {
            'instructor_archive_name': instructor_fs_path,
            'instructor_archive': get_64_contents(instructor_fs_path),
        }

        if suffix:
            user_id = self.student_submission_dict(anon_student_id=suffix)
            submission = submissions_api.get_submission(user_id.get('student_id'))
            answer = submission['answer']
            response.update({
                'user_archive_name': answer.get('real_path'),
                'user_archive': get_64_contents(answer.get('real_path')),
            })

        return Response(json_body=response)

    def get_queue_student_response(self, submission=None, dump=True):
        # TODO: Protect this with hash
        # TODO: Вынести формирование адреса для xqueue в обобщенный интерфейс

        # В некоторых случаях грейдер должен обратиться к LMS за дополнительными данными, при этом адрес LMS для
        # грейдера может отличаться от того, который предназначен для пользователя. Например, для внешних соединений
        # адрес представляет доменное имя с https, а грейдер внутри сети может обратиться к LMS по http/ip.

        # Полный адрес обработчика с указанием протокола
        base_url = self.runtime.handler_url(self, 'get_submitted_archives', thirdparty=True)

        # Получаем из настроет callback_url для xqueue
        callback_url = settings.XQUEUE_INTERFACE.get("callback_url")

        # Если он задан, перезаписываем полный адрес обработчика
        if callback_url:

            # SITENAME содержит исключительно доменное имя или ip без указания протокола
            # Заменяем найденный в полном адресе обработчике SITENAME на callback_url
            # TODO: Корректно обрабатывать https, если он указан в настройках
            base_url = re.sub("http.?//%s" % settings.SITE_NAME, callback_url, base_url)

        if submission is None:
            submission = {}
        result = {
            'archive_64_url': base_url + '/' + submission.get('uuid', ''),
        }
        if dump:
            result = json.dumps(result)
        return result

    @xqueue_callback(XBlockSubmissionResult)
    def score_update(self, submission_result):

        parent = super(ScilabXBlock, self)
        if hasattr(parent, 'score_update'):
            parent.score_update(submission_result)

        submission_uid, validation_key = submission_result.lms_key.split('+')

        # TODO: Validate submission
        # submission = submissions_api.get_submission(submission_uid)

        submissions_api.set_score(submission_uid, int(100*submission_result.score), 100,
                                  annotation_reason=submission_result.msg,
                                  annotation_creator='xblock_scilab',
                                  annotation_type='check')

        self.points = submission_result.score
        self.runtime.publish(self, 'grade', {
                'value': submission_result.score * self.max_score(),
                'max_value': self.max_score()
        })

        annotation = ifmo_submissions_api.get_annotation(self.student_submission_dict())
        self.message = None
        try:
            message = (json.loads(annotation.get('reason'))['message']).strip()
            if message:
                self.message = u"<b>Результат последней проверки:</b> %s" % message
        except (ValueError, KeyError):
            pass

    def validate_instructor_archive(self, uploaded_file):

        instructor_file = ZipFile(uploaded_file)
        file_list = instructor_file.namelist()

        self.need_generate = "generate.sce" in file_list
        assert "check.sce" in file_list, "No check.sce in instructor archive."

    def do_generate(self):

        self.pregenerated = None

        header = self.get_submission_header(dispatch='set_pregenerated')
        body = self.get_queue_student_response(dump=False)
        deep_update(body, {
            'method': 'generate',
            'grader_payload': json.dumps({
                'time_limit_generate': self.time_limit_generate,
            }),
        })

        self.send_to_queue(header=header, body=json.dumps(body), state='GENERATING')

    def get_instructor_path(self):
        return self.instructor_archive_meta.get('fs_path')

    @xqueue_callback
    def set_pregenerated(self, pregenerated):

        parent = super(ScilabXBlock, self)
        if hasattr(parent, 'set_pregenerated'):
            parent.set_pregenerated(pregenerated)

        body = json.loads(pregenerated.body)
        if body['success']:
            self.pregenerated = body['content']
            self.message = None
        else:
            self.pregenerated = None
            self.message = "При генерации задания произошла ошибка. Пожалуйста, обновите страницу."

    @XBlock.handler
    def download_archive(self, request, suffix):
        """
        Обработчик скачивания архивов.

        Вызывается в тот момент, когда инструктор нажимает на ссылку "Скачать архив".
        В результате может быть скачан инструкторский архив с проверяющим кодом или
        архив-ответ студента.

        В данный момент подразумевается, что система оперирует исключительно zip-архивами.

        Если suffix=='instructor', скачивается архив инструктора.

        Если suffix=='student', скачивается архив студента, предоставленный как ответ,
        sha1 которого содержится в request.querystring.

        :param request:
        :param suffix: 'instructor' or 'student'
        :return: webob.Response
        """

        def download(fs_path, filename, content_type='application/zip'):
            try:
                file_descriptor = default_storage.open(fs_path)
                app_iter = iter(partial(file_descriptor.read, BLOCK_SIZE), '')
                return Response(
                    app_iter=app_iter,
                    content_type=content_type,
                    content_disposition="attachment; filename=" + filename.encode('utf-8'),
                )
            except IOError:
                return Response(
                    "File {filename} not found".format(filename=filename),
                    status=404,
                )

        if suffix == 'instructor':
            return download(
                self.instructor_archive_meta.get('fs_path'),
                self.instructor_archive_meta.get('filename')
            )

        elif suffix == 'student':

            return download(
                file_storage_path(self.location, request.query_string),
                request.query_string + '.zip'
            )

        elif suffix == 'instructor_prev':

            # Скачать архив инструктора, которым было проверено определённое
            # решение студента. Поскольку мы не сохраняем историю инструкторских
            # архивов (тольки их сами), то и их имён у нас нет.

            return download(
                file_storage_path(self.location, request.query_string),
                request.query_string + '.zip'
            )

        else:
            return Response("Bad request", status=400)
