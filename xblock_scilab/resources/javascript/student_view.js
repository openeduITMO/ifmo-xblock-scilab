function ScilabXBlockStudentView(runtime, element)
{

    var upload_logic = {
        url: runtime.handlerUrl(element, 'upload_submission'),
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
                disable_controllers();
                data.submit();
            });
        },
        progressall: function (e, data) {
            var xblock = $(element).find('.ifmo-xblock-student');
            var percent = parseInt(data.loaded / data.total * 100, 10);
            xblock.find(".upload_do").text("Uploading... " + percent + "%");
        },
        done: function (e, data) {
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

        xblock.find('.reset-celery-task-id').on('click', function(e) {
            $.ajax({
                url: runtime.handlerUrl(element, 'reset_celery_task_id'),
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
        })
    }

    function disable_controllers()
    {
        $(element).find(".controllers").find("button").toggleClass('disabled').attr("disabled", "disabled");
    }

    function init_xblock($, _)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        var data = xblock.data('student-state');

        settings.allow_submissions = xblock.data('do-accept-submissions');

        data.message = xblock.data('message');
        data.message_type = xblock.data('message-type');

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