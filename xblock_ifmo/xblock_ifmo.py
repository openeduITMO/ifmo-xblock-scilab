# -*- coding=utf-8 -*-

from courseware.models import StudentModule
from datetime import datetime
from django.db import transaction
from xblock.core import XBlock
from xblock.fragment import Fragment

import json
import logging
import pytz

from .xblock_ifmo_fields import IfmoXBlockFields
from .xblock_ifmo_resources import IfmoXBlockResources

logger = logging.getLogger(__name__)


class IfmoXBlock(IfmoXBlockFields, IfmoXBlockResources, XBlock):

    has_score = True
    icon_class = 'problem'

    @transaction.autocommit
    def save_now(self):
        """
        Большинство блоков используют celery на сервере, поэтому нужно
        сохранять ссылки на задачи сразу, как они были зарезервированы.

        :return:
        """
        self.save()

    def get_score(self):
        return {
            'score': self.points * self.weight,
            'total': self.weight,
        }

    def max_score(self):
        return self.weight

    def save_settings_base(self, data):
        """
        Не является обработчиком сам по себе, однако, его могут (и должны)
        использовать дочерние обработчики, когда требуется сохранение
        настроек.

        :param data:
        :return:
        """
        self.display_name = data.get('display_name')
        self.description = data.get('description')
        self.weight = data.get('weight')
        return {}

    @staticmethod
    def _now():
        """
        Текущее время в UTC, tz-aware.

        :return: Время в UTC
        """
        return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    def _get_score_string(self):
        """
        Строка, отображающая баллы пользователя, рядом с заголовком (названием
        юнита).

        :return: Строка с баллами
        """
        result = ''
        # Отображается только в том случае, если за работу начисляются баллы
        if self.weight is not None and self.weight != 0:
            # if self.attempts > 0:
                result = '(%s/%s points)' % (self.points * self.weight, self.weight,)
            # else:
            #     result = '(%s points possible)' % (self.weight,)
        return result

    @XBlock.json_handler
    def reset_user_data(self, data, suffix=''):
        assert self._is_staff()
        user_login = data.get('user_login')
        try:
            module = StudentModule.objects.get(module_state_key=self.location,
                                               student__username=user_login)
            module.state = '{}'
            module.max_grade = None
            module.grade = None
            module.save()
            return {
                'state': "Состояние пользователя сброшено.",
            }
        except StudentModule.DoesNotExist:
            return {
                'state': "Модуль для указанного пользователя не существует."
            }

    def student_view_base(self, fragment, context=None):
        """
        Изменяем фрагмент xblock'а. Оборачиваем весь шаблон в дополнительный.
        Все ресурсы оставляем без именений.

        :param fragment: Исходный фрагмент
        :return: Изменённый фрагмент
        """

        # Создаём новый фрагмент и копируем туда ресурсы
        result = Fragment()
        result.add_frag_resources(fragment)
        result.initialize_js(fragment.js_init_fn, fragment.json_init_args)

        # Используем исходный контекст, но добавим тело
        if context is None:
            context = {}
        context.update({'body': fragment.body_html()})

        # Тело оборачиваем отдельно
        result.add_content(self.load_template(
            'student_view.html',
            context=context,
            package='xblock_ifmo'
        ))
        return result

    def get_student_context(self):
        return {
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
                }
            ),
            'is_staff': getattr(self.xmodule_runtime, 'user_is_staff', False),

            # This is probably studio, find out some more ways to determine this
            'is_studio': self.scope_ids.user_id is None,

            'due': self.due,
        }

    def _is_staff(self):
        return getattr(self.xmodule_runtime, 'user_is_staff', False)