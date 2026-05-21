document.addEventListener('DOMContentLoaded', () => {
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

        // УЛУЧШЕННЫЙ ПОИСК ДЛЯ nested-admin:
        // Ищем группу кнопок по классу djn-group, у которой id или класс содержит упоминание кнопочной модели
        const buttonsGroup = blockSuite.querySelector(
            '.djn-group[id*="-projectblockbutton-"], ' +
            '.djn-group[id*="-button-"], ' +
            '.djn-group[class*="-button"], ' +
            '.djn-group[class*="-projectblockbutton"]'
        );

        // Вариант 1: Изображение и список (BLOCK_VARIANT_IMAGE_WITH_LIST)
        if (variant === '1') {
            if (rowImage) rowImage.style.display = '';
            if (rowLeftImage) rowLeftImage.style.display = 'none';
            rowsStringList.forEach(r => r.style.display = '');
            allTextRows.forEach(r => r.style.display = 'none');
            if (buttonsGroup) buttonsGroup.style.display = 'none';
        } 
        // Вариант 2: Два изображения (BLOCK_VARIANT_TWO_IMAGES)
        else if (variant === '2') {
            if (rowImage) rowImage.style.display = '';
            if (rowLeftImage) rowLeftImage.style.display = '';
            rowsStringList.forEach(r => r.style.display = 'none');
            allTextRows.forEach(r => r.style.display = 'none');
            if (buttonsGroup) buttonsGroup.style.display = 'none';
        } 
        // Вариант 3: Изображение и кнопки (BLOCK_VARIANT_IMAGE_WITH_BUTTONS)
        else if (variant === '3') {
            if (rowImage) rowImage.style.display = '';
            if (rowLeftImage) rowLeftImage.style.display = 'none';
            rowsStringList.forEach(r => r.style.display = 'none');
            allTextRows.forEach(r => r.style.display = ''); 
            if (buttonsGroup) buttonsGroup.style.display = ''; // Показываем группу кнопок
        } 
        // Если вариант не выбран (значение "---------")
        else {
            if (rowImage) rowImage.style.display = '';
            if (rowLeftImage) rowLeftImage.style.display = '';
            rowsStringList.forEach(r => r.style.display = '');
            allTextRows.forEach(r => r.style.display = '');
            if (buttonsGroup) buttonsGroup.style.display = '';
        }
    }

    // Ловим переключения "Варианта" пользователем во всей админке
    document.addEventListener('change', (e) => {
        if (e.target && e.target.name && e.target.name.endsWith('-variant')) {
            const blockSuite = e.target.closest('.djn-inline-form');
            if (blockSuite) toggleFields(blockSuite);
        }
    });

    // Инициализация интерфейса при загрузке страницы для уже сохраненных блоков
    setTimeout(() => {
        document.querySelectorAll('.djn-inline-form').forEach(blockSuite => {
            // Проверяем, что это именно форма контентного блока, а не вложенная кнопка
            if (blockSuite.querySelector('select[name$="-variant"]')) {
                toggleFields(blockSuite);
            }
        });
    }, 800); // Немного увеличили таймаут для тяжелых страниц с TinyMCE
});

(function() {
    const style = document.createElement('style');
    style.textContent = `
        /* Гарантированный отступ между контентными блоками (старыми и вновь созданными) */
        .djn-inline-form {
            margin-bottom: 35px !important;
            border: 1px solid #cbd5e1 !important; /* Четкая серая граница вокруг каждого блока */
            background: #ffffff !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; /* Легкая тень для объема */
            display: block !important;
            clear: both !important;
        }

        /* Дополнительный отступ для внутренних групп (например, кнопок внутри блока) */
        .djn-inline-form .djn-group {
            margin-top: 20px !important;
            margin-bottom: 10px !important;
        }

        /* Делаем красивую заплатку, чтобы шапка блока отделялась от полей */
        .djn-inline-form > h3 {
            background: #f1f5f9 !important;
            margin: -20px -20px 20px -20px !important;
            padding: 12px 20px !important;
            border-bottom: 1px solid #cbd5e1 !important;
        }
    `;
    document.head.appendChild(style);
})();