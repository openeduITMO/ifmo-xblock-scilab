## -*- coding: utf-8 -*-

    <section aria-hidden="true" class="modal staff-modal init-required" id="${meta['id']}-submissions-modal" style="width: 800px" data-init-fn="SubmissionModal" data-id="${meta['id']}">
        <div class="inner-wrapper" style="color: black">
            <header><h2>Список решений</h2></header>
            <div>&nbsp;</div>
            <div>
                <label for="${meta['id']}-submission-id-input">Имя пользователя / идентификатор решения: </label>
                <input type="text" id="${meta['id']}-submission-id-input" name="submission-id">
                <input type="button" value="Показать" class="button staff-get-submission-info-btn" id="${meta['id']}-staff-get-submission-info-button"/>
            </div>
            <hr/>
            <div id="${meta['id']}-submission-info">
                <p>Информация о решении</p>
                <div class="staff-info-container" style="max-height: 600px; overflow-y: scroll;">
                    <pre>...</pre>
                </div>
            </div>
        </div>
    </section>
