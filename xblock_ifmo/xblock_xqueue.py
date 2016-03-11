# -*- coding=utf-8 -*-

from xblock.core import XBlock
from xqueue_api.utils import now, make_hashkey, create_student_info
from xblock.fields import Scope, String, Dict
import json
from .xblock_ajax import AjaxHandlerMixin
from .utils import reify


class XBlockXQueueMixin(AjaxHandlerMixin, XBlock):

    queue_name = String(
        scope=Scope.settings,
        default="",
        help="Queue name."
    )

    queue_state = String(
        scope=Scope.user_state
    )

    queue_details = Dict(
        scope=Scope.user_state,
        default=dict(),
    )

    @reify
    def queue_interface(self):
        return self.xmodule_runtime.xqueue['interface']

    @reify
    def queue_key(self):
        return make_hashkey(str(self.xmodule_runtime.seed) + self.queue_time + self.runtime.anonymous_student_id)

    @reify
    def queue_student_info(self):
        return create_student_info(anonymous_student_id=self.xmodule_runtime.anonymous_student_id,
                                   submission_time=self.queue_time)

    @reify
    def queue_time(self):
        return now()

    def save_settings(self, data):

        parent = super(XBlockXQueueMixin, self)
        if hasattr(parent, 'save_settings'):
            parent.save_settings(data)

        self.queue_name = data.get('queue_name')
        return {}

    def get_dispatched_url(self, dispatch='score_update'):
        return self.xmodule_runtime.xqueue['construct_callback'](dispatch)

    def get_submission_header(self, dispatch='score_update', access_key_prefix=''):
        return json.dumps({
            'lms_callback_url': self.get_dispatched_url(dispatch),
            'lms_key': "+".join([access_key_prefix, self.queue_key]),
            'queue_name': self.queue_name,
        })

    def send_to_queue(self, header=None, body=None):
        self.queue_details = {
            'key': self.queue_key,
            'time': self.queue_time
        }
        self.queue_interface.send_to_queue(header=header, body=body)

    @AjaxHandlerMixin.xqueue_callback
    def score_update(self, submission_result):

        parent = super(XBlockXQueueMixin, self)
        if hasattr(parent, 'score_update'):
            parent.score_update(submission_result)


