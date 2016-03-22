function SubmissionModal(runtime, element)
{
    var handlers = {
      get_submission_info: function(e) {
          console.log("staff-get-submission-info-btn clicked");
      }
    };

    var init = function ($, _)
    {
        console.log("SubmissionModal initialization");
        var $modal = $(element);
        var id = $modal.data("id");

        $modal.find(".staff-get-submission-info-btn").on("click", handlers.get_submission_info);
    };

    $(function(){
        init($, _);
    });
}