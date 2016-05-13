function ScilabXBlockStudentView(runtime, element)
{
    var urls = {
        upload_logic: runtime.handlerUrl(element, 'upload_submission'),
        get_user_data: runtime.handlerUrl(element, 'get_user_data'),
        download_archive: runtime.handlerUrl(element, 'download_archive')
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
                helpers.disable_controllers(element);
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
        upload_selected: get_template("script.scilab-template-upload-selected"),
        annotation: get_template("script.scilab-template-annotation")
    };

    var helpers = {

        deplainify: function(obj)
        {
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
        },

        disable_controllers: function(context)
        {
            $(context).find("input").addClass('disabled').attr("disabled", "disabled");
        },

        enable_controllers: function(context)
        {
            $(context).find("input").removeClass('disabled').removeAttr("disabled");
        }

    };

    var hooks = {
        render_student_answer: function(data) {
            console.log(data);

            // Поскольку у нас нет доступа к идентификатору решения здесь,
            // нам нужен дополнитеьный хендлер, получающий файл по его SHA,
            // минуя обращение к submissions.api.
            var student_file_id = data.sha1;
            var instructor_file_id = /([^\/]*)$/.exec(data.instructor_real_path)[0];

            var student_url = urls.download_archive + '/student?' + student_file_id;
            var instructor_url = urls.download_archive + '/instructor_prev?' + instructor_file_id;

            return '<p>' +
                '<a href="' + student_url + '" class="button">Скачать решение ' + data.filename + '</a> ' +
                '<a href="' + instructor_url + '" class="button">Скачать проверяющий архив</a>' +
                '</p>';
        },
        render_annotation: function(data) {
            return template.annotation(data);
        }
    };

    /*================================================================================================================*/

    function pregenerated_replacer(str, pregen_arr) {
        var replacer = function(pregen_arr) {
            var arr = pregen_arr.slice();
            return function () {
                return arr.shift();
            }
        };
        if (pregen_arr != null) {
            return str.replace(/%s/g, replacer(pregen_arr));
        } else {
            // В превью студии нет прегена, потому что там нет пользователя как такового
            return str;
        }

    }

    function render(data)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        var template_content = pregenerated_replacer(template.main(data), data.pregenerated);
        xblock.find('.ifmo-xblock-content').html(template_content);

        if (data.allow_submissions) {
            xblock.find('.upload_container').html(template.upload_input());
            xblock.find(".file_upload").fileupload(upload_logic);
        }

        if (data.task_status == 'QUEUED') {
            // helpers.disable_controllers(element);
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

        $(element).find('a.staff-download-instructor-archive').attr('href', urls.download_archive + '/instructor');

        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
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
        init_modals(runtime, element, $, _, hooks, helpers);
    });

}