from xblock.fields import Scope, Integer, String, Float


class ScilabXBlockFields(object):

    display_name = String(
        display_name="Display name",
        default='Scilab Assignment',
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings
    )

    description = String(
        display_name="Description",
        scope=Scope.settings
    )

    weight = Float(
        display_name="Max score",
        scope=Scope.settings,
        default=0,
    )

    points = Float(
        scope=Scope.user_state,
        default=0,
    )

    instructor_filename = String(
        display_name="Instructor file name",
        scope=Scope.settings
    )

    celery_task_id = String(
        scope=Scope.user_state
    )