## -*- coding: utf-8 -*-

<section aria-hidden="true" class="modal staff-modal init-required" id="${meta['id']}-tools-modal" data-init-fn="StudentStateModal" style="width: 800px">
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
            <div class="staff-info-container" style="max-height: 600px; overflow-y: scroll;"></div>
        </div>
    </div>
</section>