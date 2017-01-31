function ScilabXBlockSettingsView(runtime, element)
{
    ScilabXBlockSettingsView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.upload_logic = {
        url: self.runtime.handlerUrl(self.element, 'upload_instructor_archive'),
        add: function (e, data) {
            var selected = self.element.find("div.ifmo-xblock-scilab-studio-archive-selected");
            selected.html('Выбран ' + data.files[0].name);
            selected.data('status', 'selected');
            selected.data('status-name', data.files[0].name);
            self.element.find("input.ifmo-xblock-scilab-studio-archive-upload").off('click').on('click', function () {
                self.element.find("input.ifmo-xblock-scilab-studio-archive-upload").val('Идёт загрузка...');
                data.submit();
            });
        },
        start: function() {
            self.element.find('input').attr('disabled', 'disabled');
        },
        done: function (e, data) {
            alert('Архив инструктора успешно загружен');
            var selected = self.element.find("div.ifmo-xblock-scilab-studio-archive-selected");
            selected.data('status', 'uploaded');
            selected.html('Загружен ' + selected.data('status-name'));
        },
        fail: function() {
            alert('При загрузке архива инструктора произошла ошибка');
        },
        always: function() {
            self.element.find("input.ifmo-xblock-scilab-studio-archive-upload").val('Загрузить');
            self.element.find('input').removeAttr('disabled');
        }
    };

    self.validate = function()
    {
        // Проверим статус архива: загружен, выбран или пуст
        var selected = $(self.element).find('.ifmo-xblock-scilab-studio-archive-selected');
        var stop_saving_confirm = "";

        if(selected.data('status') == 'empty') {
            stop_saving_confirm = 'Архив инструктора не был выбран.';
        } else if(selected.data('status') == 'selected') {
            stop_saving_confirm = 'Архив инструктора выбран, но не загружен.';
        }

        // Подтвердить действие
        if(stop_saving_confirm != "") {
            if (!confirm(stop_saving_confirm + " Продолжить сохранение?")) {
                return {
                    result: false,
                    message: stop_saving_confirm,
                    title: 'SciLab XBlock'
                }
            }
        }
        return {
            result: true
        }

    };

    self.save = function()
    {
        ScilabXBlockSettingsView.superclass.save.apply(self);
    };

    self.init_xblock = function($, _)
    {
        ScilabXBlockSettingsView.superclass.init_xblock.apply(this, [$, _]);

        var xblock = $(this.element).find('.ifmo-xblock-editor');
        var data = xblock.data('metadata');

        if (data.instructor_archive != undefined && data.instructor_archive.filename != undefined) {
            var selected = xblock.find('div.ifmo-xblock-scilab-studio-archive-selected');
            selected.html('Загружен ' + data.instructor_archive.filename);
            selected.data('status', 'uploaded');
        }

        xblock.find('input.ifmo-xblock-scilab-studio-archive-file').fileupload(self.upload_logic);

    };

    self.init_xblock_ready($, _);

    return {
        save: self.save
    };

}

xblock_extend(ScilabXBlockSettingsView, IfmoXBlockSettingsView);
