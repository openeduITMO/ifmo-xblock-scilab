function SubmissionModal(runtime, xblock, element)
{
    var templates = {
        submissions: _.template($(element).find('.submissions-list-template').text())
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
                    //console.log(data);
                    $modal.find('.staff-info-container').html(templates.submissions(data));
                }
            });
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