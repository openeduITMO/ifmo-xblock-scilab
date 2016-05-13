function StudentStateModal(runtime, xblock, element, hooks, helpers) {

    var urls = {
        get_state: runtime.handlerUrl(xblock, 'get_user_state'),
        reset_state: runtime.handlerUrl(xblock, 'reset_user_state')
    };

    var init = function ($, _)
    {
        console.log("StudentStateModal initialization");
        var $modal = $(element);
        var id = $modal.data("id");

        $(element).find('.staff-get-state-btn').off('click').on('click', function(e) {
            helpers.disable_controllers(element);
            var data = {
                'user_login': $(element).find('input[name="user"]').val()
            };
            $.ajax({
                url: urls.get_state,
                type: "POST",
                data: JSON.stringify(data),
                success: function(data){
                    var state = helpers.deplainify(data);
                    $(element).find('.staff-info-container').html('<pre>' + JSON.stringify(state, null, '  ') + '</pre>');
                },
                complete: function(data) {
                    console.info('staff-get-state-btn', data);
                    helpers.enable_controllers(element);
                }
            });
        });

        $(element).find('.staff-reset-state-btn').off('click').on('click', function(e) {
            //if (!confirm('Do you really want to reset state?')) {
            //    return;
            //}
            helpers.disable_controllers(element);
            var data = {
                'user_login': $(element).find('input[name="user"]').val()
            };
            $.ajax({
                url: urls.reset_state,
                type: "POST",
                data: JSON.stringify(data),
                success: function(data) {
                    var state = helpers.deplainify(data);
                    $(element).find('.staff-info-container').html('<pre>' + JSON.stringify(state, null, '  ') + '</pre>');
                },
                complete: function(data){
                    console.info('staff-reset-state-btn', data);
                    helpers.enable_controllers(element);
            }});
        });

    };

    $(function(){
        init($, _);
    });

}