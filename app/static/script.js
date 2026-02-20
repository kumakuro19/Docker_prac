const form = document.getElementById('convertForm');
const fileInput = document.getElementById('pyFile');
const result = document.getElementById('result');
const button = document.getElementById('convertBtn');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const file = fileInput.files?.[0];
  if (!file) {
    result.textContent = '.py ファイルを選択してください。';
    return;
  }

  const formData = new FormData();
  formData.append('py_file', file);

  button.disabled = true;
  result.textContent = '変換中です...';

  try {
    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.error) {
          message = errorData.error;
        }
      } catch (_) {
        // ignore parse error
      }
      throw new Error(message);
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get('Content-Disposition') || '';
    const match = contentDisposition.match(/filename="?([^\";]+)"?/);
    const filename = match?.[1] || 'converted.zip';

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    result.textContent = `変換完了: ${filename} をダウンロードしました。`;
  } catch (error) {
    result.textContent = `エラー: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});
