const button = document.getElementById('helloBtn');
const input = document.getElementById('nameInput');
const result = document.getElementById('result');

button.addEventListener('click', async () => {
  const name = encodeURIComponent(input.value || 'world');
  result.textContent = '読み込み中...';

  try {
    const response = await fetch(`/api/hello?name=${name}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    result.textContent = data.message;
  } catch (error) {
    result.textContent = `エラー: ${error.message}`;
  }
});
