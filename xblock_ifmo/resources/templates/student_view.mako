<%!
    import json
%>
<section class="xmodule_display xmodule_CapaModule ifmo-xblock-base" data-context="${json.dumps(context.kwargs)|h}">

<%block name="block_body"/>


    % if student_state['is_staff']:
        % if not student_state['is_studio']:

            <div class="wrap-instructor-info">
                <a class="instructor-info-action" href="#${meta['id']}-tools-modal" id="${meta['id']}-tools-button">Инструменты инструктора</a>
                <a class="instructor-info-action" href="#${meta['id']}-debug-modal" id="${meta['id']}-debug-button">Отладочная информация</a>
            </div>

            <section aria-hidden="true" class="modal staff-modal" id="${meta['id']}-debug-modal" style="width: 800px">
                <div class="inner-wrapper" style="color: black">
                    <header><h2>Отладочная информация</h2></header>
                    <div>&nbsp;</div>
                    <table>
                        <tr>
                            <th>id</th>
##                             <td>${id}</td>
                        </tr>
                        <tr>
                            <th>location</th>
##                             <td>${location}</td>
                        </tr>
                        <tr>
                            <th>weight</th>
##                             <td>${weight}</td>
                        </tr>
                    </table>
                    <hr/>
                </div>
            </section>

            <section aria-hidden="true" class="modal staff-modal" id="${meta['id']}-tools-modal" style="width: 800px">
                <div class="inner-wrapper" style="color: black">
                    <header><h2>Инструменты инструктора</h2></header>
                    <div>&nbsp;</div>
                    <div>
                        <label for="${meta['id']}-staff-user-input">Имя пользователя: </label>
                        <input type="text" id="${meta['id']}-staff-user-input" name="user">
                        <input type="button" value="Получить" class="button staff-get-state-btn" id="${meta['id']}-staff-get-state-button"/>
                        <input type="button" value="Сбросить" class="button staff-reset-state-btn" id="${meta['id']}-staff-reset-state-button"/>
                        <!--<input type="button" value="Перепроверить" class="button staff-update-state-btn disabled" id="${meta['id']}-staff-update-state-button" disabled="disabled"/>-->
                    </div>
                    <hr/>
                    <div id="${meta['id']}-staff-info">
                        <p>Состояние пользователя</p>
                        <div class="staff-info-container" style="max-height: 600px; overflow-y: scroll;">
##                             <pre>${context}</pre>
                        </div>
                    </div>
                </div>
            </section>
        % else:
            <div><p><strong><i>Элементы управления недоступны в Студии.</i></strong></p></div>
        % endif
    % endif

</section>