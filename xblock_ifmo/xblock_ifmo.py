# -*- coding=utf-8 -*-

import json
import logging

from courseware.models import StudentModule
from django.contrib.auth.models import User
from path import path
from xblock.core import XBlock
from xblock.fragment import Fragment
from xqueue_api.utils import deep_update
from webob.response import Response

from .fragment import FragmentMakoChain
from .utils import require
from .xblock_ifmo_fields import IfmoXBlockFields
from .xblock_ifmo_resources import IfmoXBlockResources


logger = logging.getLogger(__name__)


class IfmoXBlock(IfmoXBlockFields, IfmoXBlockResources, XBlock):

    has_score = True
    icon_class = 'problem'

    __template_dirs = [path(__file__).dirname().abspath() / "resources" / "templates"]

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

    def save_settings(self, data):
        """
        Не является обработчиком сам по себе, однако, его могут (и должны)
        использовать дочерние обработчики, когда требуется сохранение
        настроек.

        :param data:
        :return:
        """
        parent = super(IfmoXBlock, self)
        if hasattr(parent, 'save_settings'):
            parent.save_settings(data)

        self.display_name = data.get('display_name')
        self.description = data.get('description')
        self.weight = data.get('weight')
        self.attempts = data.get('attempts')
        return {}

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
                result = '(%s/%s баллов)' % (self.points * self.weight, self.weight,)
            # else:
            #     result = '(%s points possible)' % (self.weight,)
        return result

    @XBlock.json_handler
    def reset_user_state(self, data, suffix=''):
        require(self._is_staff())
        module = self.get_module(data.get('user_login'))
        if module is not None:
            module.state = '{}'
            module.max_grade = None
            module.grade = None
            module.save()
            return {
                'state': "Состояние пользователя сброшено.",
            }
        else:
            return {
                'state': "Модуль для указанного пользователя не существует."
            }

    @XBlock.json_handler
    def get_user_state(self, data, suffix=''):
        require(self._is_staff())
        module = self.get_module(data.get('user_login'))
        if module is not None:
            return {'state': module.state}
        else:
            return {
                'state': "Модуль для указанного пользователя не существует."
            }

    @XBlock.json_handler
    def get_user_data(self, data, suffix=''):
        context = self.get_student_context_base()
        context.update(self.get_student_context())
        return context

    def student_view(self, context=None):

        if context is None:
            context = {}

        deep_update(context, {'render_context': self.get_student_context()})

        # Use init, instead of add_content, otherwise it will be re-rendered each time
        fragment = FragmentMakoChain(lookup_dirs=self.__template_dirs,
                                     content=self.load_template('student_view.mako', package='xblock_ifmo'))
        fragment.add_javascript(self.load_js('init-modals.js', package='xblock_ifmo'))
        fragment.add_javascript(self.load_js('state-modal.js', package='xblock_ifmo'))
        fragment.add_css(self.load_css('modal.css', package='xblock_ifmo'))

        return fragment

    def get_student_context(self, user=None):
        return self.get_student_context_base(user)

    def get_student_context_base(self, user=None):
        return {
            'meta': {
                'location': str(self.scope_ids.usage_id),
                'id': self.scope_ids.usage_id.block_id,
                'name': self.display_name,
                'text': self.description or "",
                'due': self.due,
                'attempts': self.attempts,
            },
            'student_state': {
                'score': {
                    'earned': self.points * self.weight,
                    'max': self.weight,
                    'string': self._get_score_string(),
                },
                'is_staff': self._is_staff(),

                # This is probably studio, find out some more ways to determine this
                'is_studio': self._is_studio(),
            },
        }

    def _is_staff(self):
        return getattr(self.xmodule_runtime, 'user_is_staff', False)

    def _is_studio(self):
        return self.runtime.get_real_user is None

    def get_response_user_state(self, additional):
        context = self.get_student_context_base()
        context.update(additional)
        return Response(json_body=context)

    def get_module(self, user=None):
        try:
            if isinstance(user, User):
                return StudentModule.objects.get(student=user,
                                                 module_state_key=self.location)
            elif isinstance(user, (basestring, unicode)):
                return StudentModule.objects.get(student__username=user,
                                                 module_state_key=self.location)
            else:
                return None
        except StudentModule.DoesNotExist:
            return None
