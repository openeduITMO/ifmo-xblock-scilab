## -*- coding: utf-8 -*-

<%!
    import json
%>

<div class="ifmo-xblock-editor" data-metadata="${json.dumps(metadata)|h}">

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
                        <label for="input_${id}_description" class="label setting-label">Текст задания</label>
                        <textarea id="input_${id}_description" class="input text setting-input" name="description"><%text><%= description %></%text></textarea>
                    </div>
                </li>

                <%block name="extra_settings"/>

            </ul>
        </div>

    </script>

    <div class="ifmo-xblock-content"></div>

</div>