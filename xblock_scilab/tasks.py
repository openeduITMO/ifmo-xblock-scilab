# -*- coding=utf-8 *-*

from django.core.files.storage import default_storage
from ifmo_celery_grader.tasks.helpers import GraderTaskBase


import shutil
import json
import zipfile
import logging
from path import path

import requests

from xblock_scilab.executable import spawn_scilab
from cStringIO import StringIO

logger = logging.getLogger(__name__)

SCILAB_EXEC = path("/opt/scilab-5.5.2/bin/scilab-adv-cli")
#SCILAB_EXEC = path("/ifmo/app/scilab-5.5.2/bin/scilab-adv-cli")
SCILAB_STUDENT_SCRIPT = "solution.sce"
SCILAB_INSTRUCTOR_SCRIPT = "checker.sce"
SCILAB_EXEC_SCRIPT = "chdir(\"%s\"); exec(\"%s\");"
# SCILAB_EXEC_SCRIPT = "disp(1); exit(0);"
SCILAB_HOME = path("/ifmo/app/scilab-5.5.2")
TMP_PATH = path('/tmp/xblock_scilab/')


class ScilabSubmissionGrade(GraderTaskBase):

    def grade_old(self, student_input, grader_payload):
        """

        :param student_input:
        :param grader_payload:
        :return:
        """

        def _cleanup():
            full_path.rmtree_p()

        def _result(msg=None, grade=0., cleanup=False):
            if cleanup:
                _cleanup()
            return {
                'msg': msg,
                'grade': grade,
            }

        # Относительное имя файла студента, <course_id>/<module>/<file_sha>.zip
        student_filename = path(student_input.get('filename'))
        instructor_filename = grader_payload.get('filename')

        # Проверка на то, что это действительно zip
        if not student_filename.ext != '.zip':
            raise Exception('NZ: Загруженный файл должен быть .zip.')

        # Полный рабочий путь в системе, со временной директорией, сразу вычистим
        full_path = TMP_PATH / student_filename.stripext()
        _cleanup()

        # Получаем архивы
        student_archive = zipfile.ZipFile(default_storage.open(student_filename))
        instructor_archive = zipfile.ZipFile(default_storage.open(instructor_filename))

        # Извлекаем архив студента
        try:
            student_archive.extractall(full_path)
        except Exception:
            return _result(msg='SAE: Не удалось открыть архив с ответом.')

        # Процессу разрешено выполняться только 2 секунды
        filename = full_path / SCILAB_STUDENT_SCRIPT
        student_code = spawn_scilab(filename, timeout=40)
        if student_code.get('return_code') == -1:
            return _result(msg='TL: Превышен лимит времени')

        try:
            instructor_archive.extractall(full_path)
        except Exception:
            return _result(msg='IAE: Не удалось открыть архив инструктора.')

        filename = full_path / SCILAB_INSTRUCTOR_SCRIPT
        checker_code = spawn_scilab(filename, timeout=40)
        if checker_code.get('return_code') == -1:
            return _result(msg='ITL: Превышен лимит времени инструктором')

        try:
            f = open(full_path + '/checker_output')
            result_grade = float(f.readline().strip())
            result_message = f.readline().strip()
        except IOError:
            return _result(
                msg='COE: Не удалось определить результат проверки.'
            )

        return _result(msg=result_message, grade=result_grade)

    def grade_success(self, student_input, grader_payload, system_payload, system, response):

        module = system.get('module')

        module.max_grade = 1.0
        module.score = response.get('grade')

        state = json.loads(module.state)
        state['message'] = response.get('msg')
        state['points'] = module.score
        module.state = json.dumps(state)

        module.save()

    #=========================================================================================================

    def grade(self, student_input, grader_payload):

        filename = student_input.get('filename')
        instructor_filename = grader_payload.get('filename')
        files = {
            'student_file': default_storage.open(filename),
            'instructor_file': default_storage.open(instructor_filename),
        }
        data = {
            'student_input': json.dumps(student_input),
            'grader_payload': json.dumps(grader_payload),
        }
        r = requests.post('http://192.168.10.13:8003', data=data, files=files)
        try:
            result = r.json()
            return {
                'grade': result.get('grade'),
                'msg': result.get('msg'),
            }
        except Exception as e:
            return {
                'grade': 0,
                'msg': e.message,
            }

