document.addEventListener('DOMContentLoaded', () => {
    function hasErrors(element) {
        return Boolean(
            element && (
                element.classList.contains('errors') ||
                element.querySelector('.errorlist, .errors')
            )
        );
    }

    function expandParentFieldset(element) {
        const fieldset = element.closest('fieldset');
        if (fieldset) {
            fieldset.classList.remove('collapsed');
            fieldset.style.display = '';
        }
    }

    function setElementDisplay(element, displayValue) {
        if (!element) return;

        if (hasErrors(element)) {
            element.style.display = '';
            expandParentFieldset(element);
            return;
        }

        element.style.display = displayValue;
    }

    function setRowsDisplay(rows, displayValue) {
        rows.forEach(row => setElementDisplay(row, displayValue));
    }

    function findButtonsGroup(blockSuite) {
        const managementInput = blockSuite.querySelector('input[name$="-buttons-TOTAL_FORMS"]');
        if (managementInput) {
            return managementInput.closest('.djn-group');
        }

        return blockSuite.querySelector(
            '.djn-group[id*="-buttons-group"], ' +
            '.djn-group[id*="-projectblockbutton-"], ' +
            '.djn-group[id*="-button-"], ' +
            '.djn-group[class*="-buttons"], ' +
            '.djn-group[class*="-button"], ' +
            '.djn-group[class*="-projectblockbutton"]'
        );
    }

    function revealErrors(blockSuite) {
        blockSuite.querySelectorAll('.errorlist, .errors').forEach(errorNode => {
            const row = errorNode.closest('.form-row');
            const group = errorNode.closest('.djn-group');

            if (row) row.style.display = '';
            if (group) group.style.display = '';
            expandParentFieldset(errorNode);
        });
    }

    // Функция скрытия/показа полей внутри конкретного блока
    function toggleFields(blockSuite) {
        // Находим селектор поля variant
        const variantSelect = blockSuite.querySelector('select[name$="-variant"]');
        if (!variantSelect) return;

        const variant = variantSelect.value;

        // Ищем строки полей (Django оборачивает их в .form-row и добавляет класс .field-[имя_поля])
        const rowImage = blockSuite.querySelector('.form-row.field-image');
        const rowLeftImage = blockSuite.querySelector('.form-row.field-left_image');
        
        // Находим строки языковых переводов для списков тезисов (string_list)
        const rowsStringList = blockSuite.querySelectorAll('.form-row[class*="field-string_list_"]');
        
        // Находим все строки языковых переводов для текстов (text и accented_text)
        const rowsText = blockSuite.querySelectorAll('.form-row[class*="field-text_"]');
        const rowsAccentedText = blockSuite.querySelectorAll('.form-row[class*="field-accented_text_"]');
        const allTextRows = [...rowsText, ...rowsAccentedText];

        const buttonsGroup = findButtonsGroup(blockSuite);

        // Вариант 1: Изображение и список (BLOCK_VARIANT_IMAGE_WITH_LIST)
        if (variant === '1') {
            setElementDisplay(rowImage, '');
            setElementDisplay(rowLeftImage, 'none');
            setRowsDisplay(rowsStringList, '');
            setRowsDisplay(allTextRows, '');
            setElementDisplay(buttonsGroup, 'none');
        } 
        // Вариант 2: Два изображения (BLOCK_VARIANT_TWO_IMAGES)
        else if (variant === '2') {
            setElementDisplay(rowImage, '');
            setElementDisplay(rowLeftImage, '');
            setRowsDisplay(rowsStringList, 'none');
            setRowsDisplay(allTextRows, '');
            setElementDisplay(buttonsGroup, 'none');
        } 
        // Вариант 3: Изображение и кнопки (BLOCK_VARIANT_IMAGE_WITH_BUTTONS)
        else if (variant === '3') {
            setElementDisplay(rowImage, '');
            setElementDisplay(rowLeftImage, 'none');
            setRowsDisplay(rowsStringList, 'none');
            setRowsDisplay(allTextRows, ''); 
            setElementDisplay(buttonsGroup, ''); // Показываем группу кнопок
        } 
        // Если вариант не выбран (значение "---------")
        else {
            setElementDisplay(rowImage, '');
            setElementDisplay(rowLeftImage, '');
            setRowsDisplay(rowsStringList, '');
            setRowsDisplay(allTextRows, '');
            setElementDisplay(buttonsGroup, '');
        }

        revealErrors(blockSuite);
    }

    // Ловим переключения "Варианта" пользователем во всей админке
    document.addEventListener('change', (e) => {
        if (e.target && e.target.name && e.target.name.endsWith('-variant')) {
            const blockSuite = e.target.closest('.djn-inline-form');
            if (blockSuite) toggleFields(blockSuite);
        }
    });

    revealErrors(document);

    // Инициализация интерфейса при загрузке страницы для уже сохраненных блоков
    setTimeout(() => {
        document.querySelectorAll('.djn-inline-form').forEach(blockSuite => {
            // Проверяем, что это именно форма контентного блока, а не вложенная кнопка
            if (blockSuite.querySelector('select[name$="-variant"]')) {
                toggleFields(blockSuite);
            }
        });
        revealErrors(document);
    }, 800); // Немного увеличили таймаут для тяжелых страниц с TinyMCE
});

(function() {
    const style = document.createElement('style');
    style.textContent = `
        /* Гарантированный отступ между контентными блоками (старыми и вновь созданными) */
        #content_blocks-group > .djn-fieldset > .djn-items > .djn-inline-form {
            margin-bottom: 35px !important;
            border: 1px solid #cbd5e1 !important; /* Четкая серая граница вокруг каждого блока */
            background: #ffffff !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; /* Легкая тень для объема */
            display: block !important;
            clear: both !important;
        }

        /* Дополнительный отступ для внутренних групп (например, кнопок внутри блока) */
        #content_blocks-group > .djn-fieldset > .djn-items > .djn-inline-form .djn-group {
            margin-top: 20px !important;
            margin-bottom: 10px !important;
        }

        /* Делаем красивую заплатку, чтобы шапка блока отделялась от полей */
        #content_blocks-group > .djn-fieldset > .djn-items > .djn-inline-form > h3 {
            background: #f1f5f9 !important;
            margin: -20px -20px 20px -20px !important;
            padding: 12px 20px !important;
            border-bottom: 1px solid #cbd5e1 !important;
        }
    `;
    document.head.appendChild(style);
})();
