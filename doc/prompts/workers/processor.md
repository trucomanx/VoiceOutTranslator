Quero criar um projeto Python com PyQt5 para Ubuntu com a seguinte estrutura fixa:

project/
 ├── main.py
 ├── ui/
 │    └── main_window.py
 ├── audio/
 │    ├── capture.py
 │    ├── vad.py
 │    └── segmenter.py
 ├── workers/
 │    └── processor.py
 ├── utils/
 │    └── temp_audio.py
 └── external_lib/
      └── transcription.py

VOCÊ É RESPONSÁVEL APENAS POR GERAR O ARQUIVO:

workers/processor.py

Não gere nenhum outro arquivo.
Não implemente UI.
Não implemente captura de áudio.
Não implemente VAD.
Não implemente segmentação.
Não altere contratos de outros módulos.

============================================================
RESPONSABILIDADE EXCLUSIVA DO workers/processor.py
============================================================

Este módulo é responsável por:

- Consumir itens de uma fila FIFO thread-safe
- Executar processamento pesado de áudio (transcrição ou tradução)
- Rodar FORA da thread principal da UI
- Comunicar resultados exclusivamente via sinais Qt

Este módulo é o CONSUMIDOR da fila.
Ele NÃO produz itens.
Ele NÃO interage com áudio em tempo real.

============================================================
INTERFACES EXTERNAS QUE VOCÊ DEVE ASSUMIR COMO EXISTENTES
============================================================

-------------------------
external_lib/transcription.py
-------------------------

Assuma que existe:

from external_lib.transcription import transcribe, translate

Contratos:

transcribe(audio_path: str) -> str
translate(audio_path: str) -> str

Regras:
- Funções bloqueantes
- Tempo de execução longo e variável
- Podem lançar exceções

-------------------------
utils/temp_audio.py
-------------------------

Assuma que existe:

from utils.temp_audio import cleanup_file

Contrato:

cleanup_file(path: str) -> None
- Remove arquivo WAV temporário
- Não lança exceção se o arquivo não existir

============================================================
INTERFACE PÚBLICA QUE VOCÊ DEVE IMPLEMENTAR
============================================================

Classe obrigatória:

AudioProcessorWorker(QObject)

Esta classe DEVE rodar dentro de um QThread.

============================================================
SINAIS Qt OBRIGATÓRIOS
============================================================

resultReady(text: str, timestamp: datetime.datetime)
- Emitido quando um item é processado com sucesso

errorOccurred(message: str)
- Emitido quando ocorre erro não fatal

============================================================
CONSTRUTOR OBRIGATÓRIO
============================================================

AudioProcessorWorker(queue: queue.Queue)

Parâmetros:
- queue:
  - queue.Queue thread-safe
  - Contém dicts com o seguinte formato:

{
    "path": str,
    "timestamp": datetime.datetime,
    "mode": str   # "transcribe" ou "translate"
}

============================================================
MÉTODOS PÚBLICOS OBRIGATÓRIOS
============================================================

1) start() -> None

- Inicia o loop de processamento
- Deve ser chamado após mover o objeto para QThread
- NÃO deve bloquear a thread chamadora

2) stop() -> None

- Solicita parada do loop
- Deve permitir finalizar item em processamento
- Deve ser idempotente

============================================================
LOOP DE PROCESSAMENTO (OBRIGATÓRIO)
============================================================

Comportamento:

- Loop contínuo enquanto ativo
- Usa queue.get() BLOQUEANTE
- Para cada item:
  - Lê item["path"], item["timestamp"], item["mode"]
  - Se mode == "transcribe":
      chamar transcribe(path)
    else if mode == "translate":
      chamar translate(path)
  - Captura texto retornado
  - Emite resultReady(text, timestamp)
  - Remove arquivo WAV usando cleanup_file(path)

============================================================
TRATAMENTO DE ERROS
============================================================

- Exceções durante processamento:
  - Devem ser capturadas
  - Emitir errorOccurred(str(e))
  - Garantir cleanup_file(path)
  - Continuar processamento do próximo item

- Nunca deixar a thread morrer silenciosamente

============================================================
REGRAS DE THREADING (CRÍTICO)
============================================================

- NÃO crie threads manualmente (threading.Thread)
- NÃO use timers
- NÃO use multiprocessing
- Use exclusivamente:
  - QObject
  - QThread
  - sinais/slots Qt

- NÃO acesse UI diretamente
- NÃO modifique widgets
- NÃO acesse QListView

============================================================
ENCERRAMENTO LIMPO
============================================================

- stop() deve:
  - sinalizar loop para encerrar
  - destravar queue.get() se necessário
- O loop deve sair de forma previsível
- Recursos devem ser liberados corretamente

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO implemente lógica de fila (isso já existe)
- NÃO implemente backpressure
- NÃO implemente UI
- NÃO acesse arquivos fora do WAV temporário
- NÃO assuma que a fila estará sempre cheia

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de workers/processor.py.
Não gere explicações.
Não gere pseudocódigo.
Não gere outros arquivos.

O código deve ser:
- robusto
- thread-safe
- totalmente compatível com PyQt5
- compatível com os contratos descritos acima

