(function () {
  const inputSelector = 'input[type="file"].admin-image-preview-input';

  function getFieldName(input) {
    return input.name.split('-').pop();
  }

  function getPreviewFieldNames(input) {
    const fieldName = getFieldName(input);
    return [`${fieldName}_preview`, `${fieldName}_preview_field`];
  }

  function getSearchScopes(input) {
    return [
      input.closest('.djn-inline-form'),
      input.closest('fieldset.module'),
      input.closest('form'),
      document,
    ].filter(Boolean);
  }

  function findPreviewRow(input) {
    const previewFieldNames = getPreviewFieldNames(input);
    const scopes = getSearchScopes(input);

    for (const scope of scopes) {
      for (const fieldName of previewFieldNames) {
        const row = scope.querySelector(`.field-${fieldName}`);
        if (row) {
          return row;
        }
      }
    }
    return null;
  }

  function getPreviewAnchor(input) {
    return input.closest('p.file-upload') || input;
  }

  function createPreviewElement() {
    const preview = document.createElement('div');
    preview.className = 'admin-image-preview admin-image-preview--live';
    preview.style.cssText = [
      'box-sizing: border-box',
      'display: inline-flex',
      'align-items: center',
      'justify-content: center',
      'width: 240px',
      'height: 160px',
      'max-width: 100%',
      'max-height: 160px',
      'margin-top: 8px',
      'padding: 6px',
      'overflow: hidden',
      'background-color: #f8fafc',
      'background-size: contain',
      'background-repeat: no-repeat',
      'background-position: center center',
      'border: 1px solid #cfd8dc',
      'border-radius: 6px',
    ].join('; ');
    return preview;
  }

  function getPreviewContainer(row) {
    return row.querySelector('.readonly') || row.querySelector('.fieldBox') || row;
  }

  function ensurePreview(input) {
    if (input.adminImagePreviewElement && input.adminImagePreviewElement.isConnected) {
      return input.adminImagePreviewElement;
    }

    const previewRow = findPreviewRow(input);
    if (previewRow) {
      const existingPreview = previewRow.querySelector('.admin-image-preview');
      if (existingPreview) {
        input.adminImagePreviewElement = existingPreview;
        input.adminImagePreviewOriginalHtml = existingPreview.innerHTML;
        return existingPreview;
      }

      const emptyPreview = previewRow.querySelector('.admin-image-preview-empty');
      const preview = createPreviewElement();
      if (emptyPreview) {
        emptyPreview.replaceWith(preview);
      } else {
        getPreviewContainer(previewRow).appendChild(preview);
      }
      input.adminImagePreviewElement = preview;
      return preview;
    }

    const preview = createPreviewElement();
    getPreviewAnchor(input).insertAdjacentElement('afterend', preview);
    input.adminImagePreviewElement = preview;
    return preview;
  }

  function clearPreview(input) {
    if (!input.adminImagePreviewElement) {
      return;
    }

    if (input.adminImagePreviewOriginalHtml) {
      input.adminImagePreviewElement.innerHTML = input.adminImagePreviewOriginalHtml;
    } else {
      input.adminImagePreviewElement.remove();
      input.adminImagePreviewElement = null;
    }
  }

  function fitSize(sourceWidth, sourceHeight, maxWidth, maxHeight) {
    if (!sourceWidth || !sourceHeight) {
      return { width: maxWidth, height: maxHeight };
    }
    const scale = Math.min(maxWidth / sourceWidth, maxHeight / sourceHeight);
    return {
      width: Math.max(Math.round(sourceWidth * scale), 1),
      height: Math.max(Math.round(sourceHeight * scale), 1),
    };
  }

  function renderPreview(input, file, dataUrl) {
    const image = document.createElement('img');
    image.src = dataUrl;
    image.alt = file.name;
    image.addEventListener('load', function () {
      const size = fitSize(image.naturalWidth, image.naturalHeight, 240, 160);
      image.width = size.width;
      image.height = size.height;
      image.style.cssText = [
        'display: block',
        `width: ${size.width}px !important`,
        `height: ${size.height}px !important`,
        'max-width: 240px !important',
        'max-height: 160px !important',
      ].join('; ');
    });

    const preview = ensurePreview(input);
    preview.replaceChildren(image);
  }

  document.addEventListener('change', function (event) {
    const input = event.target;
    if (!input.matches(inputSelector)) {
      return;
    }

    const file = input.files && input.files[0];
    if (!file || !file.type.startsWith('image/')) {
      clearPreview(input);
      return;
    }

    const reader = new FileReader();
    reader.addEventListener('load', function () {
      renderPreview(input, file, reader.result);
    });
    reader.readAsDataURL(file);
  });
})();
