function ScilabXBlockStudentView(runtime, element)
{
    var urls = {
        upload_logic: runtime.handlerUrl(element, 'upload_submission'),
        reset_task: runtime.handlerUrl(element, 'reset_celery_task_id'),
        get_state: runtime.handlerUrl(element, 'get_user_data'),
        reset_state: runtime.handlerUrl(element, 'reset_user_data')
    };

    var upload_logic = {
        url: urls.upload_logic,
        add: function (e, data) {
            var xblock = $(element).find('.ifmo-xblock-student');
            xblock.find('.upload_container').html(template.upload_selected({
                'filename': data.files[0].name
            }));
            xblock.find(".upload_another").on('click', function () {
                xblock.find('.upload_container').html(template.upload_input());
                xblock.find(".file_upload").fileupload(upload_logic);
            });
            xblock.find(".upload_do").on('click', function () {
                xblock.find(".upload_do").text("Uploading...");
                disable_controllers(element);
                data.submit();
            });
        },
        progressall: function (e, data) {
            var xblock = $(element).find('.ifmo-xblock-student');
            var percent = parseInt(data.loaded / data.total * 100, 10);
            xblock.find(".upload_do").text("Uploading... " + percent + "%");
        },
        done: function (e, data) {
            console.log(data);
            if (data.result.success !== undefined) {
                state.message = {
                    'message_type': 'error',
                    'message_text': data.result.success
                };
                render(state);
            }
            else {
                var state = JSON.parse(data.result.student_state);
                if (data.result.message != undefined) {
                    state.message = data.result.message;
                    state.message_type = data.result.message_type;
                }
                render(state);
            }
        }
    };

    var get_template = function(tmpl){
        return _.template($(element).find(tmpl).text());
    };

    var template = {
        main: get_template('script.ifmo-xblock-template-base'),
        upload_input: get_template("script.scilab-template-upload-input"),
        upload_selected: get_template("script.scilab-template-upload-selected")
    };

    var settings = {};

    /*================================================================================================================*/

    function render(data)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        xblock.find('.ifmo-xblock-content').html(template.main(data));

        if (settings.allow_submissions) {
            xblock.find('.upload_container').html(template.upload_input());
            xblock.find(".file_upload").fileupload(upload_logic);
        }

        xblock.find('.reset-celery-task-id').off('click').on('click', function(e) {
            $.ajax({
                url: urls.reset_task,
                type: 'POST',
                data: '{}',
                dataType: 'json',
                success: function (data) {
                    var state = JSON.parse(data.result.student_state);
                    if (data.result.message != undefined) {
                        state.message = data.result.message;
                        state.message_type = data.result.message_type;
                    }
                    render(state);
                }
            })
        });

        $(element).find('.staff-get-state-btn').off('click').on('click', function(e) {
                disable_controllers(element);
                var data = {
                    'user_login': $(element).find('input[name="user"]').val()
                };
                $.ajax({
                    url: urls.get_state,
                    type: "POST",
                    data: JSON.stringify(data),
                    success: function(data){
                        var state = deplainify(data);
                        $(element).find('.staff-info-container').html('<pre>' + JSON.stringify(state, null, '  ') + '</pre>');
                    },
                    complete: function(data) {
                        console.info('staff-get-state-btn', data);
                        enable_controllers(element);
                    }
                });
            });

            $(element).find('.staff-reset-state-btn').off('click').on('click', function(e) {
                if (!confirm('Do you really want to reset state?')) {
                    return;
                }
                disable_controllers(element);
                var data = {
                    'user_login': $(element).find('input[name="user"]').val()
                };
                $.ajax({
                    url: urls.reset_state,
                    type: "POST",
                    data: JSON.stringify(data),
                    success: function(data) {
                        var state = deplainify(data);
                        $(element).find('.staff-info-container').html('<pre>' + JSON.stringify(state, null, '  ') + '</pre>');
                    },
                    complete: function(data){
                        console.info('staff-reset-state-btn', data);
                        enable_controllers(element);

                }});
            });

        if (data.task_status == 'QUEUED') {
            disable_controllers(element);
        }
    }

    function disable_controllers(context)
    {
        $(context).find("input").addClass('disabled').attr("disabled", "disabled");
    }

    function enable_controllers(context)
    {
        $(context).find("input").removeClass('disabled').removeAttr("disabled");
    }

    function init_xblock($, _)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        var data = xblock.data('student-state');

        settings.allow_submissions = xblock.data('do-accept-submissions');

        data.message = xblock.data('message');
        data.message_type = xblock.data('message-type');

        var is_staff = xblock.attr("data-is-staff") == "True";
        if (is_staff) {
            $(element).find('.instructor-info-action').leanModal();
        }

        render(data);
    }

    $(function(){
        if (require === undefined) {
            function loadjs(url) {
                $("<script>").attr("type", "text/javascript").attr("src", url).appendTo(element);
            }
            loadjs("/static/js/vendor/jQuery-File-Upload/js/jquery.iframe-transport.js");
            loadjs("/static/js/vendor/jQuery-File-Upload/js/jquery.fileupload.js");
            init_xblock($, _);
        } else {
            require(["jquery", "underscore", "jquery.fileupload"], init_xblock);
        }
    });

}