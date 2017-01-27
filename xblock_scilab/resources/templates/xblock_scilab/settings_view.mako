## -*- coding: utf-8 -*-

<%inherit file="ifmo_xblock_base"/>

<%block name="extra_settings">

    ${parent.extra_settings()}

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

</%block>
