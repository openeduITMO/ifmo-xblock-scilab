function SubmissionModal(runtime, xblock, element, hooks, helpers)
{
    var templates = {
        submissions: _.template($(element).find('.submissions-list-template').text()),
        annotation: _.template($(element).find('.annotation-template').text()),
        server_error: _.template($(element).find('.server-error-template').text()),
        default_answer: _.template($(element).find('.annotation-default-answer-template').text()),
        default_annotation: _.template($(element).find('.annotation-default-annotation-template').text())
    };
    var handlers = {
        get_submission_info: function(e) {
            var $modal = e.data.modal;
            var ajax_data = {
                submission_id: $modal.find("[name='submission_id']").val()
            };
            $.ajax(handlers.urls.get_submission_info, {
                data: JSON.stringify(ajax_data),
                type: "POST",
                success: function(data) {
                    console.debug(data);
                    if (!data.success) {
                        handlers.error($modal, data.message);
                    } else if (data.type == "submissions") {
                        handlers.get_submissions_list($modal, data.message);
                    } else if (data.type == "annotation") {
                        handlers.get_annotation($modal, data.message);
                    } else {
                        handlers.error($modal, 'Received unknown data of type ' + data.type);
                        console.warn('Received unknown data of type ' + data.type);
                    }
                },
                error: handlers.server_error($modal)
            });
        },
        get_submissions_list: function($modal, data) {
            $modal.find('.staff-info-container').html(templates.submissions(data));
            $modal.find('.submission-element').click(function(e) {
                var $tr = $(e.delegateTarget);
                $modal.find("[name='submission_id']").val($tr.data('submission-id'));
                $modal.find(".staff-get-submission-info-btn").click();
            });
        },
        get_annotation: function($modal, data) {
            console.log(data);
            if('render_student_answer' in hooks) {
                data.rendered_answer = hooks.render_student_answer(data.submission.answer);
            } else {
                data.rendered_answer = templates.default_answer({answer: data.submission.answer})
            }
            if('render_annotation' in hooks) {
                data.rendered_annotation = hooks.render_annotation({annotation: data.annotation});
            } else {
                data.rendered_annotation = templates.default_annotation({annotation: data.annotation})
            }
            $modal.find('.staff-info-container').html(templates.annotation(data));
            $modal.find('.submissions-all').click(function(e){
               var $btn = $(e.delegateTarget);
                $modal.find("[name='submission_id']").val($btn.data('username'));
                $modal.find(".staff-get-submission-info-btn").click();
            });
        },
        server_error: function($modal) {
            return function(request, status, message){
                $modal.find('.staff-info-container').html(templates.server_error({status: status, message: message}));
            };
        },
        error: function($modal, message) {
            handlers.server_error($modal)(null, '', message);
        },
        urls: {
            get_submission_info: runtime.handlerUrl(xblock, 'get_submissions_data')
        }
    };

    var init = function ($, _)
    {
        console.log("SubmissionModal initialization");
        var $modal = $(element);
        var id = $modal.data("id");

        $modal.find(".staff-get-submission-info-btn").on(
            "click",
            {modal: $modal},
            handlers.get_submission_info
        );
    };

    $(function(){
        init($, _);
    });
}