function ScilabXBlockStudentView(runtime, element)
{
    ScilabXBlockStudentView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.urls = {
        upload_logic: runtime.handlerUrl(element, 'upload_submission'),
        get_user_data: runtime.handlerUrl(element, 'get_user_data'),
        download_archive: runtime.handlerUrl(element, 'download_archive')
    };

    self.upload_logic = {
        url: self.urls.upload_logic,
        add: function (e, data) {
            var xblock = $(element).find('.ifmo-xblock-student');
            xblock.find('.upload_container').html(self.template.upload_selected({
                'filename': data.files[0].name
            }));
            xblock.find(".upload_another").on('click', function () {
                xblock.find('.upload_container').html(self.template.upload_input());
                xblock.find(".file_upload").fileupload(self.upload_logic);
            });
            xblock.find(".upload_do").on('click', function () {
                xblock.find(".upload_do").text("Uploading...");
                self.helpers.disable_controllers(element);
                data.submit();
            });
        },
        progressall: function (e, data) {
            var xblock = $(element).find('.ifmo-xblock-student');
            var percent = parseInt(data.loaded / data.total * 100, 10);
            xblock.find(".upload_do").text("Uploading... " + percent + "%");
        },
        start: function() {
            self.helpers.disable_controllers(element);
        },
        done: function (e, data) {
            render(data.result);
        },
        fail: function() {
            // Эмулируем сброс файла, потому что нам не из чего перерендерить страницу
            $(element).find("button.button.upload_another").click();
            alert('При загрузке архива с решением произошла ошибка');
        },
        always: function() {
            self.helpers.enable_controllers(element);
        }
    };

    self.add_hooks(self, {
        render_student_answer: function(data) {
            console.log('render_student_answer()');

            // Поскольку у нас нет доступа к идентификатору решения здесь,
            // нам нужен дополнитеьный хендлер, получающий файл по его SHA,
            // минуя обращение к submissions.api.
            var student_file_id = data.sha1;
            var instructor_file_id = /([^\/]*)$/.exec(data.instructor_real_path)[0];

            var student_url = self.urls.download_archive + '/student?' + student_file_id;
            var instructor_url = self.urls.download_archive + '/instructor_prev?' + instructor_file_id;

            return '<p>' +
                '<a href="' + student_url + '" class="button">Скачать решение ' + data.filename + '</a> ' +
                '<a href="' + instructor_url + '" class="button">Скачать проверяющий архив</a>' +
                '</p>';
        },
        render_annotation: function(data) {
            return self.template.annotation(data);
        }
    });

    self.add_helpers(self, {
        pregenerated_replacer: function (str, pregen_arr) {
            var replacer = function (pregen_arr) {
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
    });

    self.render = function(data)
    {
        var xblock = $(element).find('.ifmo-xblock-student');
        var template_content = data.task_status != 'GENERATING' ?
            self.helpers.pregenerated_replacer(self.template.main(data), data.pregenerated) : self.template.main(data);
        xblock.find('.ifmo-xblock-content').html(template_content);

        if (data.allow_submissions) {
            xblock.find('.upload_container').html(self.template.upload_input());
            xblock.find(".file_upload").fileupload(self.upload_logic);
        }

        if (data.task_status == 'QUEUED') {
            // helpers.disable_controllers(element);
        }

        if (data.task_status != 'IDLE') {
            setTimeout(function(){
                $.post(self.urls.get_user_data, '{}', function(data) {
                    self.render(data);
                }).fail(function(){
                    console.log('error');
                })
            }, 5000);
        }

        $(element).find('a.staff-download-instructor-archive').attr('href', self.urls.download_archive + '/instructor');

        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    };

    self.init_xblock = function($, _)
    {
        ScilabXBlockStudentView.superclass.init_xblock.apply(self, [$, _]);

        var xblock = $(element).find('.ifmo-xblock-base');
        var context = xblock.data('context');

        var template = _.partial(self.get_template, element);
        self.add_templates(self, {
            main: template('script.ifmo-xblock-template-base'),
            upload_input: template("script.scilab-template-upload-input"),
            upload_selected: template("script.scilab-template-upload-selected"),
            annotation: template("script.scilab-template-annotation")
        });

        self.render(context);
    };

    self.init_xblock_ready($, _);
}

xblock_extend(ScilabXBlockStudentView, IfmoXBlockStudentView);
