function ScilabXBlockSettingsView(runtime, element)
{

    var global_view = this;
    var saveUrl = runtime.handlerUrl(element, 'save_settings');

    var upload_logic = {
        url: runtime.handlerUrl(element, 'upload_instructor_archive'),
        add: function (e, data) {
            var selected = element.find("div.ifmo-xblock-scilab-studio-archive-selected");
            selected.html('Выбран ' + data.files[0].name);
            selected.data('status', 'selected');
            element.find("input.ifmo-xblock-scilab-studio-archive-upload").off('click').on('click', function () {
                element.find("input.ifmo-xblock-scilab-studio-archive-upload").val('Идёт загрузка...');
                data.submit();
            });
        },
        done: function (e, data) {
            alert('Архив инструктора успешно загружен');
            element.find("input.ifmo-xblock-scilab-studio-archive-upload").val('Загрузить');
        }
    };


    function save()
    {
        var view = this;
        view.runtime.notify('save', {state: 'start'});

        var data = {};
        $(element).find(".input").each(function(index, input) {
            data[input.name] = input.value;
        });

        // Проверим статус архива: загружен, выбран или пуст
        var selected = $(element).find('.ifmo-xblock-scilab-studio-archive-selected');
        var stop_saving_confirm = "";

        if(selected.data('status') == 'empty') {
            stop_saving_confirm = 'Архив инструктора не был выбран.';
        } else if(selected.data('status') == 'selected') {
            stop_saving_confirm = 'Архив инструктора выбран, но не загружен.';
        }

        // Подтвердить действие
        if(stop_saving_confirm != "") {
            if (!confirm(stop_saving_confirm + " Продолжить сохранение?")) {
                view.runtime.notify('error', {msg: stop_saving_confirm, title: 'SciLab XBlock'});
                return false;
            }
        }

        $.ajax({
            type: "POST",
            url: saveUrl,
            data: JSON.stringify(data),
            success: function() {
                view.runtime.notify('save', {state: 'end'});
            }
        });
    }

    function init_xblock($, _)
    {
        var xblock = $(element).find('.ifmo-xblock-editor');
        var data = xblock.data('metadata');
        var template = _.template(xblock.find('.ifmo-xblock-template-base').text());
        xblock.find('.ifmo-xblock-content').html(template(data));

        if (data.instructor_archive != undefined && data.instructor_archive.filename != undefined) {
            var selected = xblock.find('div.ifmo-xblock-scilab-studio-archive-selected');
            selected.html('Загружен ' + data.instructor_archive.filename);
            selected.data('status', 'uploaded');
        }

        xblock.find('input.ifmo-xblock-scilab-studio-archive-file').fileupload(upload_logic);
    }

    $(function(){
       init_xblock($, _);
    });

    return {
        save: save
    }

}