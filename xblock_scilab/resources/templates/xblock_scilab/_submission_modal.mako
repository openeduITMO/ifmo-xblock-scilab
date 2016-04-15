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
        <p><b>Список пользовательских решений <%= username %></b></p>
        <table class="selectable">
            <thead>
                <tr>
                    <th>Попытка</th>
                    <th>Item</th>
                    <!-- <th>Создано</th> -->
                    <th>Загружено</th>
                </tr>
            </thead>
            <tbody>
            <% _.each(submissions, function(i, index) { %>
                <tr data-submission-id="<%= username %>+<%= i.attempt_number %>" class="submission-element">
                    <td><%= i.attempt_number %></td>
                    <td><%= i.student_item %></td>
                    <!-- <td><%= i.created_at %></td> -->
                    <td><%= i.submitted_at %></td>
                </tr>
            <% }); %>
            </tbody>
        </table>
    </%text>
    </script>

    <script type="text/template" class="server-error-template">
    <%text>
        <p>При загрузке данных произошла ошибка: <b><%= status %> <%= message %></b></p>
    </%text>
    </script>

    <script type="text/template" class="annotation-template">
    <%text>
        <input type="button" class="submissions-all" data-username="<%= username %>" value="Все решения <%= username %>"/><hr/>
        <p>Информация о пользовательском решении:</p>

        <p>
            <table>
                <tbody>
                    <tr><td>Пользователь</td><td><%= username %></td></tr>
                    <tr><td>Номер попытки</td><td><%= submission.attempt_number %></td></tr>
                    <tr><td>Отправлено</td><td><%= submission.submitted_at %></td></tr>
                </tbody>
            </table>
        </p>

        <p><b>Ответ пользователя</b></p>
        <%= rendered_answer %>

        <% if(score){ %>
            <p><b>Оценка за работу</b></p>
            <p>
                <table>
                    <tr><th>Время</th><td><%= score.created_at %></td></tr>
                    <tr><th>Максимальный балл</th><td><%= score.points_possible %></td></tr>
                    <tr><th>Полученный балл</th><td><%= score.points_earned %></td></tr>
                </table>
            </p>
        <% } else { %>
            <p><b>Работа не была оценена</b></p>
        <% } %>

        <% if(annotation){ %>
            <p><b>Аннотация к работе</b></p>
            <%= rendered_annotation %>
        <% } else { %>
            <p><b>Нет связанной с работой аннотации</b></p>
        <% } %>

    </%text>
    </script>

    <script type="text/template" class="annotation-default-answer-template">
    <%text>
        <pre><%= answer %></pre>
    </%text>
    </script>

    <script type="text/template" class="annotation-default-annotation-template">
    <%text>
        <table>
            <tr><th>Аннотация</th><td><%= annotation %></td></tr>
        </table>
    </%text>
    </script>

</section>
