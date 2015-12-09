# -*- coding=utf-8 *-*

from django.core.files.storage import default_storage
from ifmo_celery_grader.tasks.helpers import GraderTaskBase
from subprocess import Popen, PIPE

import shutil
import json
import time
import zipfile


SCILAB_EXEC = "/ifmo/app/scilab-5.5.2/bin/scilab-adv-cli"
SCILAB_STUDENT_CMD = "exec('%s/solution.sce'); exit;"
SCILAB_INSTRUCTOR_CMD = "exec('%s/checker.sce'); exit;"


class ScilabSubmissionGrade(GraderTaskBase):

    def grade(self, student_input, grader_payload):

        default_grade = {
            'msg': 'UNKNOWN ERROR',
            'grade': 0,
        }

        filename = student_input.get('filename')
        if not filename.endswith('.zip'):
            raise Exception('Uploaded file is not zip archive.')

        file_path = filename[:-4]
        full_path = '/tmp/xblock_scilab/' + file_path

        try:
            shutil.rmtree(full_path)
        except:
            pass

        f = default_storage.open(filename)
        student_archive = zipfile.ZipFile(f)
        student_archive.extractall(full_path)

        # Процессу разрешено выполняться только 2 секунды
        process = Popen([SCILAB_EXEC, '-e', SCILAB_STUDENT_CMD % full_path], cwd=full_path)
        time.sleep(2)
        process.kill()


        instructor_filename = grader_payload.get('filename')

        try:
            f = default_storage.open(instructor_filename)
            instructor_archive = zipfile.ZipFile(f)
            instructor_archive.extractall(full_path)
        except:
            default_grade['msg'] = 'INSTRUCTOR UNPACK ERROR'
            return default_grade

        process = Popen([SCILAB_EXEC, '-e', SCILAB_INSTRUCTOR_CMD % full_path], cwd=full_path)
        time.sleep(2)
        process.kill()

        try:
            f = open(full_path + '/checker_output')
            result = float(f.read().strip())
        except:
            default_grade['msg'] = 'CHECKER OUTPUT READ ERROR'
            return default_grade

        shutil.rmtree(full_path)

        return {
            'msg': 'OK',
            'grade': result,
        }

    def grade_success(self, student_input, grader_payload, system_payload, system, response):

        module = system.get('module')

        module.max_grade = 1.0
        module.score = response.get('grade')

        state = json.loads(module.state)
        state['msg'] = response.get('msg')
        state['points'] = module.score
        module.state = json.dumps(state)

        module.save()
