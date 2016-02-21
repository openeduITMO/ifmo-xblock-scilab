# -*- coding=utf-8 -*-

from xblock.core import XBlock
from xqueue_api.utils import now, make_hashkey
from xblock.fields import Scope, String


class XBlockXQueueMixin(XBlock):

    queue_name = String(
        scope=Scope.settings,
        default="",
        help="Queue name."
    )

    def save_settings(self, data):

        parent = super(XBlockXQueueMixin, self)
        if hasattr(parent, 'save_settings_base'):
            parent.save_settings(data)

        self.queue_name = data.get('queue_name')
        return {}

    def get_queue_interface(self):
        return self.xmodule_runtime.xqueue['interface']

    def get_queue_key(self, qtime=None):

        if qtime is None:
            qtime = now()

        make_hashkey(str(self.xmodule_runtime.seed) + qtime + self.runtime.anonymous_student_id)

    def get_dispatched_url(self, dispatch='score_update'):
        return self.xmodule_runtime.xqueue['construct_callback'](dispatch)
