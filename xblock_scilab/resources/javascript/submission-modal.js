function SubmissionModal(runtime, xblock, element)
{
    var templates = {
        submissions: _.template($(element).find('.submissions-list-template').text()),
        server_error: _.template($(element).find('.server-error-template').text())
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
                        handlers.get_submissions_list($modal, data);
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