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

audio/segmenter.py

Não gere nenhum outro arquivo.
Não implemente captura de áudio.
Não implemente UI.
Não implemente processamento pesado.
Não use PyQt.

============================================================
RESPONSABILIDADE EXCLUSIVA DO audio/segmenter.py
============================================================

Este módulo é responsável por:

- Receber frames de áudio contínuos
- Detectar início e fim de fala
- Agrupar frames de fala em segmentos
- Salvar segmentos válidos como arquivos WAV temporários
- Enfileirar metadata para processamento posterior

Este módulo é o PRODUTOR da fila FIFO.
Ele NÃO consome a fila.
Ele NÃO processa transcrição.

============================================================
INTERFACES EXTERNAS QUE VOCÊ DEVE ASSUMIR COMO EXISTENTES
============================================================

-------------------------
audio/vad.py
-------------------------

Assuma que existe:

from audio.vad import RMSVoiceActivityDetector

Classe RMSVoiceActivityDetector:

Métodos:
- is_speech(frame: np.ndarray) -> bool

-------------------------
utils/temp_audio.py
-------------------------

Assuma que existe:

from utils.temp_audio import get_temp_wav_path

Contrato:
- get_temp_wav_path(prefix: str = "chunk") -> str
- Retorna caminho único para WAV
- NÃO cria o arquivo ainda

-------------------------
audio/capture.py
-------------------------

Assuma que os frames recebidos por este módulo
vêm de uma callback registrada em:

SystemAudioCapture(
    sample_rate: int,
    frame_duration: float,
    callback: Callable[[np.ndarray], None]
)

Este módulo NÃO instancia SystemAudioCapture,
apenas recebe frames via método process_frame().

============================================================
INTERFACE PÚBLICA QUE VOCÊ DEVE IMPLEMENTAR
============================================================

Classe obrigatória:

SpeechSegmenter

Construtor OBRIGATÓRIO:

SpeechSegmenter(
    vad: RMSVoiceActivityDetector,
    queue: queue.Queue,
    get_mode_callable: Callable[[], str],
    sample_rate: int
)

Parâmetros:
- vad:
    - Instância já criada de RMSVoiceActivityDetector
- queue:
    - queue.Queue thread-safe
    - FIFO
- get_mode_callable:
    - Função sem parâmetros
    - Retorna "transcribe" ou "translate"
- sample_rate:
    - Ex: 16000

============================================================
MÉTODOS PÚBLICOS OBRIGATÓRIOS
============================================================

1) process_frame(frame: np.ndarray) -> None

- Chamado continuamente para cada frame de áudio
- NÃO deve bloquear
- NÃO deve lançar exceções

2) stop() -> None

- Finaliza segmento ativo, se existir
- Pode ser chamado múltiplas vezes
- Deve ser idempotente

============================================================
REGRAS DE SEGMENTAÇÃO (OBRIGATÓRIAS)
============================================================

Use os seguintes parâmetros fixos (constantes no código):

- FRAME_DURATION = inferido pelo tamanho do frame
- MIN_SPEECH_DURATION = 0.5 segundos
- SILENCE_TIMEOUT = 0.8 segundos

Lógica:

- Enquanto vad.is_speech(frame) == True:
  - acumular frames
  - marcar timestamp de início se for o primeiro frame

- Quando vad.is_speech(frame) == False:
  - incrementar contador de silêncio

- Se silêncio contínuo >= SILENCE_TIMEOUT:
  - encerrar segmento

Encerramento de segmento:

- Se duração < MIN_SPEECH_DURATION:
  - descartar
- Caso contrário:
  - salvar WAV
  - enfileirar metadata

============================================================
ARQUIVO WAV
============================================================

- Formato:
  - WAV
  - PCM 16-bit
  - Mono
  - sample_rate fornecido
- Use numpy + wave (ou soundfile)
- O caminho deve ser obtido via get_temp_wav_path()

============================================================
METADATA ENFILEIRADA
============================================================

Cada item colocado na fila deve ser um dict:

{
    "path": str,
    "timestamp": datetime.datetime,
    "mode": str   # "transcribe" ou "translate"
}

Regras:
- timestamp = início real da fala
- mode = valor retornado por get_mode_callable()
- mode deve ser capturado NO MOMENTO DO ENCERRAMENTO do segmento

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO use PyQt
- NÃO use threads explícitas
- NÃO bloqueie process_frame()
- NÃO acesse arquivos fora do diretório temporário
- NÃO consuma a fila
- NÃO implemente lógica de processamento pesado

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de audio/segmenter.py.
Não gere explicações.
Não gere pseudocódigo.
Não gere outros arquivos.

O código deve ser determinístico,
robusto contra variações de tempo,
e totalmente compatível com os contratos descritos acima.

