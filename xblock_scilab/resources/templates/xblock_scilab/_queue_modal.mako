## -*- coding: utf-8 -*-

<section aria-hidden="true" class="modal staff-modal init-required" id="${meta['id']}-queue-info-modal" style="width: 800px" data-init-fn="QueueInfoModal" data-id="${meta['id']}">
    <div class="inner-wrapper" style="color: black">
        <header><h2>Состояние очереди</h2></header>
        <div>&nbsp;</div>
        <div>
            <label for="${meta['id']}-queue-user-input">Имя пользователя</label>
            <input type="text" id="${meta['id']}-queue-user-input" name="username">
            <input type="button" value="Показать" class="button staff-get-queue-info-btn" id="${meta['id']}-staff-get-queue-info-button"/>
            <input type="button" value="Сбросить" class="button staff-reset-queue-status-btn" id="${meta['id']}-staff-reset-queue-status-button"/>
            <input type="button" value="Активные статусы" class="button staff-get-active-queue-status-btn" id="${meta['id']}-staff-get-active-queue-status-button"/>
        </div>
        <hr/>
        <div id="${meta['id']}-submission-info">
            <div class="staff-info-container" style="max-height: 600px; overflow-y: scroll;">
                <p>Введите имя пользователя и нажмите "Показать", чтобы получить состояния пользователя в очереди.</p>
                <p>Введите имя пользователя и нажмите "Сбросить", чтобы сбросить состояния пользователя в очереди. Ранее сгенерированный вариант будет сохранён.</p>
                <p>Нажмите кнопку "Активные статусы" для получения списка пользователей с активными статусами (проверка или генерация).</p>
            </div>
            <hr/>
            <pre class="staff-info-container-data">...</pre>
        </div>
    </div>

    <script type="text/template" class="server-error-template">
    <%text>
        <p>При загрузке данных произошла ошибка: <b><%= status %> <%= message %></b></p>
    </%text>
    </script>

</section>
