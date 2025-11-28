// static/js/convert.js
const convertBtn = document.getElementById('convertBtn');
const urlInput = document.getElementById('url');
const formatSelect = document.getElementById('format');
const status = document.getElementById('status');
const progressBar = document.getElementById('progressBar');
const logEl = document.getElementById('log');

function log(msg){
    const p = document.createElement('div');
    p.textContent = msg;
    logEl.prepend(p);
}

convertBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    const fmt = formatSelect.value;

    if(!url){
        alert('Coloque o link do vídeo.');
        return;
    }

    status.textContent = "Iniciando...";
    progressBar.style.width = '0%';
    log('Iniciando conversão: ' + url);

    // Faz POST via XHR para permitir progresso de download
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/convert', true);
    xhr.responseType = 'blob';
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Upload progress (pequeno payload)
    xhr.upload.onprogress = function(e){
        if(e.lengthComputable){
            const p = Math.round((e.loaded / e.total)*100);
            status.textContent = 'Upload: ' + p + '%';
            progressBar.style.width = Math.max(5, p) + '%';
        }
    };

    // Download progress (o arquivo convertido)
    xhr.onprogress = function(e){
        // e.loaded = bytes baixados, e.total pode ser indefinido
        if(e.lengthComputable){
            const p = Math.round((e.loaded / e.total)*100);
            status.textContent = 'Download: ' + p + '%';
            progressBar.style.width = p + '%';
        } else {
            // quando total não é conhecido, fazemos um progresso visual suave
            status.textContent = `Baixando... ${Math.round(e.loaded / 1024)} KB`;
            let cur = parseFloat(progressBar.style.width) || 0;
            progressBar.style.width = Math.min(95, cur + 6) + '%';
        }
    };

    xhr.onload = function(){
        if(xhr.status === 200){
            status.textContent = 'Concluído — preparando arquivo...';
            const disposition = xhr.getResponseHeader('Content-Disposition') || '';
            let filename = fmt === 'mp3' ? 'converted.mp3' : 'converted.mp4';
            const m = disposition.match(/filename="?([^"]+)"?/);
            if(m) filename = m[1];

            const blob = xhr.response;
            const urlBlob = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = urlBlob;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(urlBlob);

            status.textContent = 'Download iniciado — verifique sua pasta de downloads.';
            progressBar.style.width = '100%';
            log('Conversão finalizada: ' + filename);
        } else {
            // tenta ler mensagem de erro (JSON)
            const reader = new FileReader();
            reader.onload = function(){
                try{
                    const txt = reader.result;
                    const obj = JSON.parse(txt);
                    status.textContent = 'Erro: ' + (obj.error || 'Erro interno');
                    log('Erro servidor: ' + JSON.stringify(obj));
                } catch(err){
                    status.textContent = 'Erro desconhecido';
                    log('Erro desconhecido ao converter.');
                }
            };
            reader.readAsText(xhr.response);
        }
    };

    xhr.onerror = function(){
        status.textContent = 'Erro na requisição';
        log('Erro de requisição XHR');
    };

    const payload = JSON.stringify({ url: url, format: fmt });
    xhr.send(payload);
});
