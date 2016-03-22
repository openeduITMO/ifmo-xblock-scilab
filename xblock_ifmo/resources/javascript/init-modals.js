/**
 * Инициализация всех модальных окон.
 *
 * Находит все дочерние элементы element, имеющие класс `init-required`,
 * вызывает метод, указанный в аттрибуте `data-init-fn`.
 *
 * @TODO: init_modals должны перезавать инициализирующим функциям $ и _
 *
 * @param runtime XBlock runtime
 * @param element Элемент модельного окна
 * @param $ jQuery object
 * @param _ underscore object
 */
function init_modals(runtime, element, $, _)
{
    $(element).find('.init-required').each(function(i, e) {
        var init_fn = $(e).data('init-fn');
        if(typeof window[init_fn] == "function") {
            window[init_fn](runtime, e);
        } else {
            console.warn("init_fn is not a function: ", init_fn);
        }
        $(e).removeClass('init-required');
    });
}