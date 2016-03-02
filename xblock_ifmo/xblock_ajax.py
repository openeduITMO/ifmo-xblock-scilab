# -*- coding=utf-8 -*-


from xqueue_api.xsubmission import XSubmissionResult


class AjaxHandlerMixin(object):
    """
    Когда приходит callback от xqueue, вызывается метод handle_ajax. Однако,
    метод XBlock.handle_ajax не имеет никакого отношения к реализации этого
    метода, поэтому обычные XBlock-и не имеют такого атрибута в принципе. Чтобы
    ловить хендлеры от xqueue, нужно его реализовать. Этот миксин несёт
    минимальную реализацию, которая позволит просто замаскировать методы под
    хендлеры.
    """

    @staticmethod
    def pseudo_ajax_handler(func):
        assert hasattr(func, '__call__') and hasattr(func, 'func_name')
        func._is_pseudo_ajax_handler = True
        return func

    @staticmethod
    def xqueue_callback(func):
        assert hasattr(func, '__call__') and hasattr(func, 'func_name')
        func._is_xqueue_callback = True
        return func

    def handle_ajax(self, dispatch, data):

        method = getattr(self, dispatch, None)
        if getattr(method, '_is_pseudo_ajax_handler', False):
            method(data)

        elif getattr(method, '_is_xqueue_callback', False):
            submission_result = XSubmissionResult(data)
            method(submission_result)

        else:
            raise AttributeError("Attribute %s not found" % dispatch)

        self.save()


