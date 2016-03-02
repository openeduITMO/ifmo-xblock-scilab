# -*- coding=utf-8 -*-

from xblock.core import XBlock
from xqueue_api.utils import now, make_hashkey, default_time
from xblock.fields import Scope, String
import json
from .xblock_ajax import AjaxHandlerMixin


class XBlockXQueueMixin(AjaxHandlerMixin, XBlock):

    queue_name = String(
        scope=Scope.settings,
        default="",
        help="Queue name."
    )

    def save_settings(self, data):

        parent = super(XBlockXQueueMixin, self)
        if hasattr(parent, 'save_settings'):
            parent.save_settings(data)

        self.queue_name = data.get('queue_name')
        return {}

    def get_queue_interface(self):
        return self.xmodule_runtime.xqueue['interface']

    @default_time
    def get_queue_key(self, qtime=None, prefix=''):
        return "+".join([prefix,
                         make_hashkey(str(self.xmodule_runtime.seed) + qtime + self.runtime.anonymous_student_id)])

    def get_dispatched_url(self, dispatch='score_update'):
        return self.xmodule_runtime.xqueue['construct_callback'](dispatch)

    def get_submission_header(self, dispatch='score_update', prefix=''):
        return json.dumps({
            'lms_callback_url': self.get_dispatched_url(dispatch),
            'lms_key': self.get_queue_key(prefix=prefix),
            'queue_name': self.queue_name,
        })

    @default_time
    def get_queue_student_info(self, qtime=None):
        return json.dumps({
            'anonymous_student_id': self.xmodule_runtime.anonymous_student_id,
            'submission_time': qtime
        })

    @AjaxHandlerMixin.xqueue_callback
    def score_update(self, submission_result):

        parent = super(XBlockXQueueMixin, self)
        if hasattr(parent, 'score_update'):
            parent.score_update(submission_result)

        pass


