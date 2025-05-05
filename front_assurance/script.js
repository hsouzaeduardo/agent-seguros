  const chatBox = document.getElementById('chatBox');
  const chatInput = document.getElementById('chatInput');
  

  function addMessage(msg, sender = 'user') {
    const el = document.createElement('div');
    el.className = 'message ' + sender;
    el.innerText = sender === 'user' ? `Você: ${msg}` : `Bot: ${msg}`;
    chatBox.appendChild(el);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

function startConversation() {
  
  const myHeaders = new Headers();
  myHeaders.append("user", "gustavo.leanca");

  const requestOptions = {
    method: "POST",
    headers: myHeaders,
    redirect: "follow"
  };

  fetch("http://localhost:8000/newAgent", requestOptions)
    .then((response) => response.json()) // Alterado para JSON
    .then((result) => {
      // Salvar o sessionId no sessionStorage
      sessionStorage.setItem("sessionId", result.sessionId);

      // Atualizar a variável de conversação com o conversationStep
      const conversationStep = result.conversationStep;
      showCallback(result.datetime, conversationStep, "📦 Callback do Step");
      // Exibir a resposta do Sales Agent no chat
      const salesAnswer = result.salesAnswer.split(": ")[1]; // Extrai apenas a mensagem do agente
      addMessage(salesAnswer, "bot");

      console.log("Session ID:", result.sessionId);
      console.log("Conversation Step:", conversationStep);
      
    })
    .catch((error) => console.error("Erro ao iniciar conversa:", error));
}

function showCallback(data, title = '📦 Callback do Step') {
  const separator = '\n==============================\n';
  const timestamp = new Date().toLocaleTimeString();
  const formatted = `${separator}${title} (${timestamp})\n${JSON.stringify(data, null, 2)}`;
  callbackBox.textContent += formatted + '\n';
  callbackBox.scrollTop = callbackBox.scrollHeight;
}

function handleSend() {
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage(text, 'user'); // mostra a mensagem do usuário

  const myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");
  sessionId = sessionStorage.getItem("sessionId") 
  myHeaders.append("session_id", sessionId);

  const raw = JSON.stringify({
    "message": text,
    "user": "henrique.souza"
  });

  const requestOptions = {
    method: "POST",
    headers: myHeaders,
    body: raw,
    redirect: "follow"
  };

  fetch("http://localhost:8000/conversationStep", requestOptions)
    .then(response => response.json())
    .then(data => {
      // Adiciona a resposta do agente no chat
      if (data.salesAnswer) {
        addMessage(data.salesAnswer, 'bot');
      } else {
        addMessage('Sem resposta do agente.', 'bot');
      }

      conversationStep = data.conversationStep;
      // Exibe tudo no callbackBox
      showCallback(data.datetime, conversationStep, "📦 Callback do Step");
      
    })
    .catch(error => {
      console.error('Erro:', error);
      addMessage('Erro na comunicação com o agente.', 'bot');
      showCallback({ error: error.message }, '❌ Erro no Callback');
    });

  chatInput.value = '';
}


  function handleMic() {
    addMessage('[🎤 Enviando áudio...]', 'user');

    fetch('https://suaapi.com/audio')
      .then(res => res.json())
      .then(data => addMessage(data.resposta || 'Sem resposta de áudio', 'bot'))
      .catch(() => addMessage('Erro no microfone', 'bot'));
  }

  function handleImageUpload() {
    const file = document.getElementById('imgUpload').files[0];
    if (!file) return;
  
    const formData = new FormData();
    formData.append('file', file);  // nome correto do campo
    formData.append('user', 'henrique.souza');  // Body param
  
    const sessionId = sessionStorage.getItem("sessionId");
  
    addMessage('[📷 Enviando imagem...]', 'user');
  
    fetch('http://localhost:8000/upload-image', {
      method: 'POST',
      headers: {
        'session_id': sessionId
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.salesAnswer) {
          addMessage(data.salesAnswer, 'bot');
          showCallback(data, "🖼️ Callback do Upload");
        } else {
          addMessage('Imagem enviada, mas sem resposta do agente.', 'bot');
        }
      })
      .catch(() => {
        addMessage('Erro ao enviar imagem', 'bot');
        showCallback({ error: 'Erro no envio de imagem' }, '❌ Erro no Callback');
      });
  }
  

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  addEventListener('load', () => {
    startConversation();
  });
  