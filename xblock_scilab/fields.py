from xblock.fields import Scope, Integer, String, Float, Boolean
from xblock_ifmo.xblock_ifmo_fields import IfmoXBlockFields


class ScilabXBlockFields(IfmoXBlockFields):

    instructor_filename = String(
        display_name="Instructor file name",
        scope=Scope.settings
    )

    celery_task_id = String(
        scope=Scope.user_state
    )

    task_state = String(
        scope=Scope.user_state,
        default='IDLE',
    )

    message = String(
        scope=Scope.user_state,
        default=None,
    )

    need_generate = Boolean(
        default=False,
        scope=Scope.settings,
        display_name="",
        help=""
    )

    pregenerated = String(
        default=None,
        scope=Scope.user_state,
    )
