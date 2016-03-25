from xblock.fields import Boolean, Integer, Scope, String
from xblock_ifmo.xblock_ifmo_fields import IfmoXBlockFields


class ScilabXBlockFields(IfmoXBlockFields):

    instructor_filename = String(
        display_name="Instructor file name",
        scope=Scope.settings
    )

    celery_task_id = String(
        scope=Scope.user_state
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

    time_limit_generate = Integer(
        scope=Scope.settings,
        default=10,
    )

    time_limit_execute = Integer(
        scope=Scope.settings,
        default=10,
    )

    time_limit_check = Integer(
        scope=Scope.settings,
        default=10,
    )
