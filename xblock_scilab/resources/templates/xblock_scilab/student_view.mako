<%inherit file="ifmo_xblock_base"/>

<%block name="block_body">
    <section class="ifmo-xblock-student">

        ${self.task_template()}
        ${self.upload_template()}
        ${self.annotation_template()}


        <div class="ifmo-xblock-content problem">
            Подождите, задание загружается...
            <pre>${context}</pre>
        </div>

    </section>

    <%include file="_submission_modal.mako" args="**context"/>

</%block>

<%block name="instructor_actions">
    <a class="instructor-info-action" href="#${meta['id']}-submissions-modal" id="${meta['id']}-submissions-button">Загруженные решения</a>
</%block>

<%block name="task_template">
    <script type="text/template" class="ifmo-xblock-template-base">
        <%doc>
            Template parameter:
                {
                    allow_submissions,
                    meta: {
                        name
                    },
                    message: {
                        text,
                        type
                    },
                    task_status,
                    task_with_pregenerated,
                    student_state: {
                        score: {
                            string
                        }
                    }
                }
        </%doc>
        <h2 class="problem-header"><%text><%= meta.name %></%text></h2>
        <div class="problem-progress"><%text><%= student_state.score.string %></%text></div>
        ${self.status()}
        ${self.message()}
        ${self.task_text()}
        % if not student_state['is_studio']:
            ${self.controllers_box()}
        % endif
    </script>
</%block>

<%block name="status">
    <%text>
        <% if (task_status == 'QUEUED') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info %>">
                Ваше решение поставлено в очередь на проверку.
            </div>
        <% } %>

        <% if (task_status == 'GENERATING') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info %>">
                Пожалуйста, подождите, пока генерируется ваш персональный вариант задания.
            </div>
        <% } %>
    </%text>
</%block>

<%block name="message">
    <%text>
        <% if (typeof message != 'undefined') { %>
        <div class="ifmo-xblock-message ifmo-xblock-message-<%= message.type %>"><%= message.text %></div>
        <% } %>
    </%text>
</%block>

<%block name="task_text">
    <%text>
        <% if (task_with_pregenerated) { %>
            <div class="task"><%= task_with_pregenerated %></div>
        <% } %>
    </%text>
</%block>

<%block name="controllers_box">
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
</%block>

<%block name="upload_template">
    <script type="text/template" class="scilab-template-upload-input">
        <%doc>
            Template parameter:
                {
                }
        </%doc>
        <div class="button upload_input">
            <span>Выберите файл</span>
            <input class="file_upload" type="file" name="submission"/>
        </div>
    </script>

    <script type="text/template" class="scilab-template-upload-selected">
        <%doc>
            Template parameter:
                {
                    filename
                }
        </%doc>
        <button class="button upload_another">Выбрать другой файл</button>
        <button class="button button-highlighted upload_do" data-in-progress="Идёт отправка...">Отправить <%text><%= filename %></%text></button>
    </script>
</%block>

<%block name="annotation_template"><%text>
<script type="text/template" class="scilab-template-annotation">
<%
    try {
        annotation_details = JSON.parse(annotation.reason);
    } catch(err) {
        annotation_details = {feedback: 'Submission has annotation, but error occurred while parsing it.'};
        annotation = {annotation_type: 'annotation parse error'};
        console.error(err);
    }
%>
    <style>
        table.annotation td {text-align: left;}
        table.annotation pre {margin: 0; padding: 0; font-size: 0.8em;}
    </style>
    <table class="annotation">
        <tr><th>Type</th><td><%= annotation.annotation_type %></td></tr>
        <!-- <tr><th>Reason</th><td><%= annotation.reason %></td></tr> -->
        <tr><th>Feedback</th><td><%= annotation_details.message %></td></tr>
        <tr><th>Pregenerated</th><td><pre><%= annotation_details.pregenerated %></pre></td></tr>
        <tr><th>Execute Output</th><td><pre><%= annotation_details.output_execute %></pre></td></tr>
        <tr><th>Check Output</th><td><pre><%= annotation_details.output_check %></pre></td></tr>
    </table>
</script>
</%text></%block>