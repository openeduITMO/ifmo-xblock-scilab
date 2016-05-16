## -*- coding: utf-8 -*-

<%!
    import json
%>

<div class="ifmo-xblock-editor" data-metadata="${metadata|h}">

    <script type="text/template" class="ifmo-xblock-template-base">

        <div class="wrapper-comp-settings is-active" data-metadata="">
            <ul class="list-input settings-list">

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_display_name" class="label setting-label">Отображаемое имя</label>
                        <input id="input_${id}_display_name" class="input setting-input" type="text" name="display_name" value="<%text><%= display_name %></%text>" />
                    </div>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_queue_name" class="label setting-label">Имя очереди</label>
                        <input id="input_${id}_queue_name" class="input setting-input" type="text" name="queue_name" value="<%text><%= queue_name %></%text>" />
                    </div>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_weight" class="label setting-label">Вес</label>
                        <input id="input_${id}_weight" class="input setting-input" type="text" name="weight" value="<%text><%= weight %></%text>" />
                    </div>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_attempts" class="label setting-label">Количество попыток</label>
                        <input id="input_${id}_attempts" class="input setting-input" type="text" name="attempts" value="<%text><%= attempts %></%text>" />
                    </div>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_instructor_archive" class="label setting-label">Архив инструктора</label>
                        <div class="ifmo-xblock-scilab-studio-archive-container">
                                <input id="input_${id}_instructor_archive" class="setting-input ifmo-xblock-scilab-studio-archive-file" type="file" name="instructor_archive"/>
                                <div class="ifmo-xblock-scilab-studio-archive-selected" data-status="empty">Архив не выбран</div>
                        </div>
                        <input type="button" class="upload_instructor_archive ifmo-xblock-scilab-studio-archive-upload" value="Отправить">
                    </div>
                    <span class="tip setting-help">Архив инструктора должен содержать файл <b>check.sce</b>. Этот сценарий должен создать файл <b>check_output</b>, содержащий вещественное число от 0 до 1.
                        Архив также может содержать сценарий с именем <b>generate.sce</b>, создающий файл <b>pregenerated</b>.</span>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_description" class="label setting-label">Текст задания</label>
                        <textarea id="input_${id}_description" class="input text setting-input" name="description"><%text><%= description %></%text></textarea>
                    </div>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_time_limit_generate" class="label setting-label">Лимит времени на генерацию</label>
                        <input id="input_${id}_time_limit_generate" class="input setting-input" type="text" name="time_limit_generate" value="<%text><%= time_limit_generate %></%text>" />
                    </div>
                    <span class="tip setting-help">Максимальное время в секундах, отведённое на генерацию варианта задания. Если не задано, то используется значение по умолчанию 10 секунд.</span>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_time_limit_execute" class="label setting-label">Лимит времени на исполнение</label>
                        <input id="input_${id}_time_limit_execute" class="input setting-input" type="text" name="time_limit_execute" value="<%text><%= time_limit_execute %></%text>" />
                    </div>
                    <span class="tip setting-help">Максимальное время в секундах, отведённое на исполнение пользовательского решения. Если не задано, то используется значение по умолчанию 10 секунд.</span>
                </li>

                <li class="field comp-setting-entry">
                    <div class="wrapper-comp-setting">
                        <label for="input_${id}_time_limit_check" class="label setting-label">Лимит времени на проверку</label>
                        <input id="input_${id}_time_limit_check" class="input setting-input" type="text" name="time_limit_check" value="<%text><%= time_limit_check %></%text>" />
                    </div>
                    <span class="tip setting-help">Максимальное время в секундах, отведённое на проверку пользовательского решения. Если не задано, то используется значение по умолчанию 10 секунд.</span>
                </li>

            </ul>
        </div>

    </script>

    <div class="ifmo-xblock-content"></div>

</div>