(function () {
  const inputSelector = 'input[type="file"].admin-image-preview-input';

  function getPreviewAnchor(input) {
    return input.closest('p.file-upload') || input;
  }

  function ensurePreview(input) {
    if (input.adminImagePreviewElement && input.adminImagePreviewElement.isConnected) {
      return input.adminImagePreviewElement;
    }

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
    getPreviewAnchor(input).insertAdjacentElement('afterend', preview);
    input.adminImagePreviewElement = preview;
    return preview;
  }

  function clearPreview(input) {
    if (input.adminImagePreviewUrl) {
      URL.revokeObjectURL(input.adminImagePreviewUrl);
      input.adminImagePreviewUrl = null;
    }
    if (input.adminImagePreviewElement) {
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

    if (input.adminImagePreviewUrl) {
      URL.revokeObjectURL(input.adminImagePreviewUrl);
    }

    const previewUrl = URL.createObjectURL(file);
    input.adminImagePreviewUrl = previewUrl;
    const image = document.createElement('img');
    image.src = previewUrl;
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
  });
})();
