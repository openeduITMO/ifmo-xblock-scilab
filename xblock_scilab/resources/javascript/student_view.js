function ScilabXBlockStudentView(runtime, element)
{
    var urls = {
        upload_logic: runtime.handlerUrl(element, 'upload_submission'),
        reset_task: runtime.handlerUrl(element, 'reset_celery_task_id'),
        get_state: runtime.handlerUrl(element, 'get_user_state'),
        get_user_data: runtime.handlerUrl(element, 'get_user_data'),
        reset_state: runtime.handlerUrl(element, 'reset_user_state')
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
            render(data.result);
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

    var deplainify = function(obj) {
        for (var key in obj) {
            try {
                if (obj.hasOwnProperty(key)) {
                    obj[key] = deplainify(JSON.parse(obj[key]));
                }
            } catch (e) {
                console.log('failed to deplainify', obj);
            }
        }
        return obj;
    };

    var hooks = {
        render_student_answer: function(data) {
            return JSON.stringify(data);
        }
    };

    /*================================================================================================================*/

    function render(data)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        xblock.find('.ifmo-xblock-content').html(template.main(data));

        if (data.allow_submissions) {
            xblock.find('.upload_container').html(template.upload_input());
            xblock.find(".file_upload").fileupload(upload_logic);
        }

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
                //if (!confirm('Do you really want to reset state?')) {
                //    return;
                //}
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
            //disable_controllers(element);
        }

        if (data.task_status != 'IDLE') {
            setTimeout(function(){
                $.post(urls.get_user_data, '{}', function(data) {
                    render(data);
                }).fail(function(){
                    console.log('error');
                })
            }, 5000);
        }

        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
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
        var xblock = $(element).find('.ifmo-xblock-base');
        var context = xblock.data('context');

        var is_staff = context.student_state.is_staff == true;
        if (is_staff) {
            $(element).find('.instructor-info-action').leanModal();
        }

        render(context);
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
        init_modals(runtime, element, $, _, hooks);
    });

}