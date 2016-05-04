function ScilabXBlockStudioView(runtime, element)
{

    var global_view = this;
    var saveUrl = runtime.handlerUrl(element, 'save_settings');

    var upload_logic = {
        url: runtime.handlerUrl(element, 'upload_instructor_archive'),
        add: function (e, data) {
            element.find("div.ifmo-xblock-scilab-studio-archive-selected").html('Selected ' + data.files[0].name);
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

        xblock.find('input.ifmo-xblock-scilab-studio-archive-file').fileupload(upload_logic);
    }

    $(function(){
       init_xblock($, _);
    });

    return {
        save: save
    }

}