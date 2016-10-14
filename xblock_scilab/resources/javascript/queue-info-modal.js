function QueueInfoModal(runtime, xblock, element, hooks, helpers)
{
    var templates = {
        server_error: _.template($(element).find('.server-error-template').text())
    };
    var handlers = {
        get_user_queue_info: function(e) {
            var $modal = e.data.modal;
            var ajax_data = {
                username: $modal.find("[name='username']").val()
            };
            $.ajax(handlers.urls.get_user_queue_status, {
                data: JSON.stringify(ajax_data),
                type: "POST",
                success: function(data) {
                    console.debug(data);
                    handlers.display_info($modal, data);
                },
                // this will not show any error message yet, copy-paste from submissions-modal
                error: handlers.server_error($modal)
            });
        },
        reset_active_status: function(e) {
            var $modal = e.data.modal;
            var ajax_data = {
                username: $modal.find("[name='username']").val()
            };
            if(!confirm('Сбросить активное состояние в очереди для пользователя ' + ajax_data.username + '? Отменить это действие будет невозможно!'))
                return;
            $.ajax(handlers.urls.reset_active_status, {
                data: JSON.stringify(ajax_data),
                type: "POST",
                success: function(data) {
                    console.debug(data);
                    handlers.display_info($modal, data);
                },
                // this will not show any error message yet, copy-paste from submissions-modal
                error: handlers.server_error($modal)
            });
        },
        get_active_status_list: function(e) {
            var $modal = e.data.modal;
            var ajax_data = {
            };
            $.ajax(handlers.urls.get_active_status_list, {
                data: JSON.stringify(ajax_data),
                type: "POST",
                success: function(data) {
                    console.debug(data);
                    handlers.display_info($modal, data);
                },
                // this will not show any error message yet, copy-paste from submissions-modal
                error: handlers.server_error($modal)
            });
        },
        display_info: function($modal, data) {
            $modal.find('.staff-info-container-data').html(JSON.stringify(data));
        },
        server_error: function($modal) {
            return function(request, status, message){
                $modal.find('.staff-info-container-data').html(templates.server_error({status: status, message: message}));
            };
        },
        error: function($modal, message) {
            handlers.server_error($modal)(null, '', message);
        },
        urls: {
            get_user_queue_status: runtime.handlerUrl(xblock, 'get_user_queue_status'),
            reset_active_status: runtime.handlerUrl(xblock, 'reset_active_status'),
            get_active_status_list: runtime.handlerUrl(xblock, 'get_active_status_list')
        }
    };

    var init = function ($, _)
    {
        console.log("QueueInfo initialization");
        var $modal = $(element);
        var id = $modal.data("id");

        $modal.find(".staff-get-queue-info-btn").on(
            "click",
            {modal: $modal},
            handlers.get_user_queue_info
        );

        $modal.find(".staff-reset-queue-status-btn").on(
            "click",
            {modal: $modal},
            handlers.reset_active_status
        );

        $modal.find(".staff-get-active-queue-status-btn").on(
            "click",
            {modal: $modal},
            handlers.get_active_status_list
        );
    };

    $(function(){
        init($, _);
    });
}
