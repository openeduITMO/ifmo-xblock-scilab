## -*- coding: utf-8 -*-

<section aria-hidden="true" class="modal staff-modal init-required" id="${meta['id']}-submissions-modal" style="width: 800px" data-init-fn="SubmissionModal" data-id="${meta['id']}">
    <div class="inner-wrapper" style="color: black">
        <header><h2>Список решений</h2></header>
        <div>&nbsp;</div>
        <div>
            <label for="${meta['id']}-submission-id-input">Имя пользователя / идентификатор решения: </label>
            <input type="text" id="${meta['id']}-submission-id-input" name="submission_id">
            <input type="button" value="Показать" class="button staff-get-submission-info-btn" id="${meta['id']}-staff-get-submission-info-button"/>
        </div>
        <hr/>
        <div id="${meta['id']}-submission-info">
            <div class="staff-info-container" style="max-height: 600px; overflow-y: scroll;">
                <p>Введите имя пользователя или идентификатор решения в поле выше и нажмите "Показать".</p>
##                 <pre>...</pre>
            </div>
        </div>
    </div>

    <script type="text/template" class="submissions-list-template">
    <%text>
        <p><b>Список пользовательских решений</b></p>
        <table class="selectable">
            <thead>
                <tr>
                    <th>Попытка</th>
                    <th>Item</th>
                    <th>Создано</th>
                    <th>Загружено</th>
                </tr>
            </thead>
            <tbody>
            <% _.each(message, function(element, index) { %>
                <tr>
                    <td><%= element.attempt_number %></td>
                    <td><%= element.student_item %></td>
                    <td><%= element.created_at %></td>
                    <td><%= element.submitted_at %></td>
                </tr>
            <% }); %>
            </tbody>
        </table>
    </%text>
</script>

</section>
