# -*- coding=utf-8 -*-

from subprocess import Popen, PIPE
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
import uuid
import time
import os
import logging
from path import path
import signal

logger = logging.getLogger(__name__)


SCILAB_EXEC = "/opt/scilab-5.5.2/bin/scilab-adv-cli"
#SCILAB_EXEC = "/ifmo/app/scilab-5.5.2/bin/scilab-adv-cli"
SCILAB_EXEC_SCRIPT = "chdir(\"%s\"); exec(\"%s\"); exit();"
SCILAB_HOME = "/opt/scilab-5.5.2"


def demote(user_uid=os.geteuid(), user_gid=os.getegid()):
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


def read_all(process):
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


def set_non_block(process):
    """
    Устанавилвает stdout в неблокирующий режим.

    См. http://eyalarubas.com/python-subproc-nonblock.html

    :param process: Процесс
    :return:
    """
    try:
        flags = fcntl(process.stdout, F_GETFL)
        fcntl(process.stdout, F_SETFL, flags | O_NONBLOCK)
    except IOError:
        logger.warning("Failed to update process flags: I/O")


def spawn_scilab(filename, cwd=None, timeout=None, extra_env=None, use_display=False):
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

    assert isinstance(filename, path)

    # Устанавливаем рабочую директорию, если необходимо
    if cwd is None:
        cwd = filename.dirname()
        logger.warning("No cwd specified for scilab_spawn, "
                       "default is used: %s", cwd)

    # Устанавливаем окружение
    env = os.environ.copy()
    env['SCIHOME'] = SCILAB_HOME

    if use_display is None:
        env['DISPLAY'] = ':99'
    elif isinstance(use_display, basestring):
        env['DISPLAY'] = use_display

    if isinstance(extra_env, dict):
        env.update(extra_env)

    # Для опредлеления того, завершился ли скрипт или ушёл в цикл скрипт,
    # будем мониторить вывод
    uid = str(uuid.uuid4())
    script = SCILAB_EXEC_SCRIPT % (cwd, filename)
    script += 'disp("%s");' % uid

    # Запускаем процесс
    # TODO Найти, как запустить scilab без шелла
    # Если запускать его без шелла, то xcos не может отработать, поскольку
    # что-то ему не даёт подключиться к Xserver'у
    cmd = [SCILAB_EXEC, '-e', script, '-nb']
    # logger.debug(" ".join(cmd))
    print(" ".join(cmd))
    process = Popen(cmd,
                    cwd=cwd, env=env, stdout=PIPE, bufsize=1,  shell=False,
                    preexec_fn=demote())
    set_non_block(process)

    # Убиваем по таймауту или ждём окончания исполнения, если он не задан
    if timeout is None:
        # Скорей всего, в этом случае произойдёт блокировка намертво,
        # поскольку scilab сам не завершится, поэтому timeout нужно задать
        logger.warning('Process timeout is not set. Now being in wait-state...')
        process.wait()
        output = read_all(process)
        return_code = process.returncode
    else:
        time.sleep(timeout)
        output = read_all(process)
        os.killpg(process.pid, signal.SIGTERM)
        if output.find(uid) != -1:
            return_code = 0
        else:
            return_code = -1

    logging.info(output)
    print output

    # Возвращаем результат исполнения
    return {
        'code': return_code,
        'stdout': output,
    }