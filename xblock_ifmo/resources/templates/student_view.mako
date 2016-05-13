## -*- coding: utf-8 -*-

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
                <%block name="instructor_actions"/>
            </div>

            <section aria-hidden="true" class="modal staff-modal" id="${meta['id']}-debug-modal" style="width: 800px">
                <div class="inner-wrapper" style="color: black">
                    <header><h2>Отладочная информация</h2></header>
                    <div>&nbsp;</div>
                    <table class="vertical">
                        <tr><th>Идентификатор</th><td><input type="text" style="width: 100%" value="${meta['location']}"/></td></tr>
                        <tr><th>id</th><td>${meta['id']}</td></tr>
                        <tr><th>Отображаемое имя</th><td>${meta['name']}</td></tr>
                        <tr><th>Срок сдачи</th><td>${meta['due']}</td></tr>
                        <tr><th>Попытки</th><td>${meta['attempts']}</td></tr>
                        <%block name="debug_info_rows"/>
                    </table>
                    <hr/>
                </div>
            </section>

        <%include file="_student_state_modal.mako" args="**context"/>

        % endif
    % endif

    % if student_state['is_studio']:
        <div><p><strong><i>Элементы управления недоступны в Студии.</i></strong></p></div>
    % endif

</section>