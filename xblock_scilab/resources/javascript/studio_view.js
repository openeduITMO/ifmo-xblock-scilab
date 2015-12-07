function ScilabXBlockStudioView(runtime, element)
{

    var global_view = this;
    var saveUrl = runtime.handlerUrl(element, 'save_settings');

    var upload_logic = {
        url: runtime.handlerUrl(element, 'upload_instructor_checker'),
        add: function (e, data) {
            element.find("span.selected_instructor_checker").html('Selected ' + data.files[0].name);
            element.find("input.upload_instructor_checker").off('click').on('click', function () {
                element.find("input.upload_instructor_checker").val('Uploading...');
                data.submit();
            });
        },
        done: function (e, data) {
                element.find("input.upload_instructor_checker").val('Upload');
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

        xblock.find('input.instructor_checker').fileupload(upload_logic);
    }

    $(function(){
       init_xblock($, _);
    });

    return {
        save: save
    }

}