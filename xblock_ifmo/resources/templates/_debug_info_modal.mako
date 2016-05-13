## -*- coding: utf-8 -*-
<%block name="modal">
<section aria-hidden="true" class="modal staff-modal init-required" id="${meta['id']}-debug-modal" data-init-fn="DebugInfoModal" style="width: 800px">
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
</%block>