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
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
import uuid

logger = logging.getLogger(__name__)

SCILAB_EXEC = "/ifmo/app/scilab-5.5.2/bin/scilab-adv-cli"
SCILAB_STUDENT_CMD = "%s/solution.sce"
SCILAB_INSTRUCTOR_CMD = "%s/checker.sce"
SCILAB_EXEC_SCRIPT = "chdir(\"%s\"); exec(\"%s\");"
# SCILAB_EXEC_SCRIPT = "disp(1); exit(0);"
SCILAB_HOME = "/ifmo/app/scilab-5.5.2"


class ScilabSubmissionGrade(GraderTaskBase):

    @staticmethod
    def _demote(user_uid=os.geteuid(), user_gid=os.getegid()):
        """
        Устанавливаем пользователя и группу, необходимо для инициализации
        дочернего процесса.

        :param user_uid: Пользователь
        :param user_gid: Группа
        :return: Инициализирующая функция
        """
        def result():
            os.seteuid(user_uid)
            os.setegid(user_gid)
            os.setpgrp()
        return result

    @staticmethod
    def _read_all(process):
        """
        Читает stdout из процесса. Он должен быть запущен в неблокирующем
        режиме вывода.

        См. http://eyalarubas.com/python-subproc-nonblock.html

        :param process: Процесс
        :return: Вывод процесса
        """
        result = ''
        file_desc = process.stdout.fileno()
        while True:
            try:
                data = read(file_desc, 1024)
                if data == '': break
                result += data
            except OSError:
                break
        return result

    @staticmethod
    def _set_non_block(process):
        """
        Устанавилвает stdout в неблокирующий режим.

        См. http://eyalarubas.com/python-subproc-nonblock.html

        :param process: Процесс
        :return:
        """
        flags = fcntl(process.stdout, F_GETFL)
        fcntl(process.stdout, F_SETFL, flags | O_NONBLOCK)

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
        env['SCIHOME'] = SCILAB_HOME
        # env['DISPLAY'] = ':1'
        if isinstance(extra_env, dict):
            env.update(extra_env)

        # Для опредлеления того, завершился ли скрипт или ушёл в цикл скрипт,
        # будем мониторить вывод
        uid = str(uuid.uuid4())
        script = SCILAB_EXEC_SCRIPT % (cwd, filename)
        script += 'disp("%s");' % uuid

        # Запускаем процесс
        # TODO Найти, как запустить scilab без шелла
        # Если запускать его без шелла, то xcos не может отработать, поскольку
        # что-то ему не даёт подключиться к Xserver'у
        cmd = [SCILAB_EXEC, '-e', SCILAB_EXEC_SCRIPT % (cwd, filename), '-nb']
        logger.debug(" ".join(cmd))
        process = Popen(cmd,
                        cwd=cwd, env=env, stdout=PIPE, bufsize=1,  shell=False,
                        preexec_fn=ScilabSubmissionGrade._demote())
        ScilabSubmissionGrade._set_non_block(process)

        # Убиваем по таймауту или ждём окончания исполнения, если он не задан
        if timeout is None:
            # Скорей всего, в этом случае произойдёт блокировка намертво,
            # поскольку scilab сам не завершится, поэтому timeout нужно задать
            logger.warning('Process timeout is not set. Now being in wait-state...')
            process.wait()
            output = ScilabSubmissionGrade._read_all(process)
            return_code = process.returncode
        else:
            time.sleep(timeout)
            output = ScilabSubmissionGrade._read_all(process)
            process.kill()
            if output.find(uid) != -1:
                return_code = 0
            else:
                return_code = -1

        # Возвращаем результат исполнения
        return {
            'code': return_code,
            'stdout': output,
        }

    def grade(self, student_input, grader_payload):
        """

        :param student_input:
        :param grader_payload:
        :return:
        """

        def _cleanup():
            shutil.rmtree(full_path, ignore_errors=True)

        def _result(msg=None, grade=0., cleanup=False):
            if cleanup:
                _cleanup()
            return {
                'msg': msg,
                'grade': grade,
            }

        filename = student_input.get('filename')
        if not filename.endswith('.zip'):
            raise Exception('Uploaded file is not zip archive.')

        file_path = filename[:-4]
        full_path = '/tmp/xblock_scilab/' + file_path

        _cleanup()

        f = default_storage.open(filename)
        student_archive = zipfile.ZipFile(f)
        student_archive.extractall(full_path)

        # Процессу разрешено выполняться только 2 секунды
        filename = SCILAB_STUDENT_CMD % full_path
        student_code = self._spawn_scilab(filename, timeout=5)
        if student_code.get('return_code') == -1:
            return _result(msg='Timeout')

        instructor_filename = grader_payload.get('filename')

        try:
            f = default_storage.open(instructor_filename)
            instructor_archive = zipfile.ZipFile(f)
            instructor_archive.extractall(full_path)
        except:
            return _result(
                msg='(IAE) Не удалось инициализировать архив инструктора.'
            )

        filename = SCILAB_INSTRUCTOR_CMD % full_path
        checker_code = self._spawn_scilab(filename, timeout=5)
        if checker_code.get('return_code') == -1:
            return _result(msg='Instructor Timeout')

        try:
            f = open(full_path + '/checker_output')
            result_grade = float(f.readline().strip())
            result_message = f.readline().strip()
        except IOError:
            return _result(
                msg='(CORE) Не удалось определить результат проверки.'
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
