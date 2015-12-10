# -*- coding=utf-8 *-*

from django.core.files.storage import default_storage
from ifmo_celery_grader.tasks.helpers import GraderTaskBase
from subprocess import Popen, PIPE

import shutil
import json
import time
import zipfile
import os
import pwd
import logging
from path import path

logger = logging.getLogger(__name__)

SCILAB_EXEC = "/ifmo/app/scilab-5.5.2/bin/scilab-adv-cli"
SCILAB_STUDENT_CMD = "%s/solution.sce"
SCILAB_INSTRUCTOR_CMD = "%s/checker.sce"
SCILAB_EXEC_SCRIPT = "chdir('%s'); exec('%s'); exit;"


class ScilabSubmissionGrade(GraderTaskBase):

    @staticmethod
    def _demote(user_uid=os.geteuid(), user_gid=os.getegid()):
        def result():
            os.seteuid(user_uid)
            os.setegid(user_gid)
        return result

    def _spawn_scilab(self, filename, cwd=None, timeout=None, extra_env=None):
        """
        Запускает инстанс scilab'а с указанным файлом и параметрами. Возвращает
        результат выполнения.

        :param filename: Имя файла для исполнения
        :param cwd: Рабочая директория, по умолчанию является директориией, где
                    располагается скрипт для исполнения
        :param timeout: Время на исполнение в секундах
        :param extra_env: Дополнительные переменные окружения
        :return: Результат выполнения
        """

        # Устанавливаем рабочую директорию, если необходимо
        if cwd is None:
            cwd = path(filename).dirname()
            logger.warning("No cwd specified for scilab_spawn, "
                           "default is used: %s", cwd)

        # Устанавливаем окружение
        env = os.environ.copy()
        if isinstance(extra_env, dict):
            env.update(extra_env)

        # Запускаем процесс
        process = Popen([SCILAB_EXEC, '-e', SCILAB_EXEC_SCRIPT % filename],
                        cwd=cwd, env=env,
                        preexec_fn=ScilabSubmissionGrade._demote())

        # Убиваем по таймауту или ждём окончания исполнения, если он не задан
        if timeout is None:
            process.wait()
        else:
            time.sleep(timeout)
            process.kill()

        # Возвращаем результат исполнения
        return {
            'code': process.returncode,
            # 'stdout': process.stdout.read(),
        }

    def grade(self, student_input, grader_payload):
        """

        :param student_input:
        :param grader_payload:
        :return:
        """

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
        filename = SCILAB_STUDENT_CMD % full_path
        student_code = self._spawn_scilab(filename, timeout=2)

        instructor_filename = grader_payload.get('filename')

        try:
            f = default_storage.open(instructor_filename)
            instructor_archive = zipfile.ZipFile(f)
            instructor_archive.extractall(full_path)
        except:
            default_grade['msg'] = 'INSTRUCTOR UNPACK ERROR'
            return default_grade

        filename = SCILAB_INSTRUCTOR_CMD % full_path
        checker_code = self._spawn_scilab(filename, timeout=2)

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
