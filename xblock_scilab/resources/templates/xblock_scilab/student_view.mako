<%inherit file="ifmo_xblock_base"/>

<%block name="block_body">
    <section class="ifmo-xblock-student">

    <script type="text/template" class="ifmo-xblock-template-base">
        <h2 class="problem-header"><%text><%= meta.name %></%text></h2>
        <div class="problem-progress"><%text><%= student_state.score.string %></%text></div>

        <%text>
        <% if (task_status == 'QUEUED') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info %>">
                Ваше решение поставлено в очередь на проверку.
            </div>
        <% } %>
        </%text>

        <%text>
        <% if (task_status == 'GENERATING') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info %>">
                Пожалуйста, подождите, пока генерируется ваш персональный вариант задания.
            </div>
        <% } %>
        </%text>

        <%text>
        <% if (task_with_pregenerated) { %>
            <div class="task"><%= task_with_pregenerated %></div>
        <% } %>
        </%text>

        <%text>
        <% if (typeof message != 'undefined') { %>
        <div class="ifmo-xblock-message ifmo-xblock-message-<%= message.type %>"><%= message.text %></div>
        <% } %>
        </%text>

    % if not student_state['is_studio']:

        <%text>
        <% if (allow_submissions) { %>

            <% if (task_status == 'IDLE') { %>
                <div class="controllers">
                    <div class="upload_container"></div>
                </div>
            <% } else { %>
                <!--<div class="ifmo-xblock-message ifmo-xblock-message-info">Your submission is queued for grading.</div>-->
            <% } %>

        <% } else { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info">
                Решения больше не принимаются.
            </div>
        <% } %>
        </%text>

    % endif

    </script>

    <script type="text/template" class="scilab-template-upload-input">
        <div class="button upload_input">
            <span>Выберите файл</span>
            <input class="file_upload" type="file" name="submission"/>
        </div>
    </script>

    <script type="text/template" class="scilab-template-upload-selected">
        <button class="button upload_another">Выбрать другой файл</button>
        <button class="button button-highlighted upload_do" data-in-progress="Идёт отправка...">Отправить <%text><%= filename %></%text></button>
    </script>

    <div class="ifmo-xblock-content problem">
        Подождите, задание загружается...
        <pre>${context}</pre>
    </div>

</section>
</%block>