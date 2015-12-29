# -*- coding=utf-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import logging
import sys
from cgi import FieldStorage
import json
from cStringIO import StringIO
from path import path
import zipfile

from xblock_scilab.executable import spawn_scilab

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

PORT = 8003

SCILAB_STUDENT_SCRIPT = "solution.sce"
SCILAB_INSTRUCTOR_SCRIPT = "checker.sce"
TMP_PATH = path('/tmp/xblock_scilab/')


class ScilabServer(BaseHTTPRequestHandler):

    def do_POST(self):

        def _cleanup(cwd):
            cwd.rmtree_p()

        def _result(msg=None, grade=0., cleanup=False):
            return {
                'msg': msg,
                'grade': grade,
            }

        data = FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"}
        )

        def do():

            result = {}

            # Dicts
            student_input = json.loads(data.getfirst('student_input'))
            grader_payload = json.loads(data.getfirst('grader_payload'))

            # Archives
            student_file = StringIO(data.getfirst('student_file'))
            instructor_file = StringIO(data.getfirst('instructor_file'))

            # Относительное имя файла студента, <course_id>/<module>/<file_sha>.zip
            student_filename = path(student_input.get('filename'))
            instructor_filename = grader_payload.get('filename')

            # Проверка на то, что это действительно zip
            if student_filename.ext != '.zip':
                raise Exception('NZ: Загруженный файл должен быть .zip.')

            # Полный рабочий путь в системе, со временной директорией, сразу вычистим
            full_path = TMP_PATH / student_filename.stripext()
            _cleanup(cwd=full_path)

            # Получаем архивы
            student_archive = zipfile.ZipFile(student_file)
            instructor_archive = zipfile.ZipFile(instructor_file)

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

        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        res = do()
        self.wfile.write(json.dumps(res))


def main():
    print ("Start listening on port %s" % PORT)
    server = HTTPServer(("", PORT), ScilabServer)
    server.serve_forever()

if __name__ == "__main__":
    main()
