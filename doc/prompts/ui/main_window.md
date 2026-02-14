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

ui/main_window.py

Não gere nenhum outro arquivo.
Não altere a estrutura do projeto.
Não implemente código de áudio de baixo nível.
Não replique lógica de outros módulos.

============================================================
RESPONSABILIDADE EXCLUSIVA DO ui/main_window.py
============================================================

Este arquivo implementa a JANELA PRINCIPAL da aplicação PyQt5.
Ele é responsável por:

1) Criar a interface gráfica (botões, seleção de modo, list view)
2) Orquestrar os componentes de áudio e processamento
3) Conectar sinais entre threads e UI
4) Manter o estado global da aplicação
5) Garantir start/stop seguro da captura e processamento

A UI NUNCA pode bloquear.
A UI NUNCA processa áudio pesado.

============================================================
INTERFACES EXTERNAS QUE VOCÊ DEVE ASSUMIR COMO EXISTENTES
============================================================

-------------------------
utils/temp_audio.py
-------------------------

Assuma que existe:

from utils.temp_audio import init_temp_dir

Contrato:
- init_temp_dir() -> str
- Retorna caminho do diretório temporário
- main.py já chama essa função e passa o path para MainWindow

-------------------------
audio/vad.py
-------------------------

Assuma que existe:

from audio.vad import RMSVoiceActivityDetector

Classe RMSVoiceActivityDetector:

__init__(
    sample_rate: int = 16000,
    silence_ratio: float = 0.1
)

Métodos:
- calibrate(frames: list[np.ndarray]) -> None
- is_speech(frame: np.ndarray) -> bool

-------------------------
audio/capture.py
-------------------------

Assuma que existe:

from audio.capture import SystemAudioCapture

Classe SystemAudioCapture:

__init__(
    sample_rate: int,
    frame_duration: float,
    callback: Callable[[np.ndarray], None]
)

Métodos:
- start() -> None
- stop() -> None

A callback será chamada continuamente com frames de áudio (numpy.ndarray).

-------------------------
audio/segmenter.py
-------------------------

Assuma que existe:

from audio.segmenter import SpeechSegmenter

Classe SpeechSegmenter:

__init__(
    vad: RMSVoiceActivityDetector,
    queue: queue.Queue,
    get_mode_callable: Callable[[], str],
    sample_rate: int
)

Métodos:
- process_frame(frame: np.ndarray) -> None
- stop() -> None

-------------------------
workers/processor.py
-------------------------

Assuma que existe:

from workers.processor import AudioProcessorWorker

Classe AudioProcessorWorker(QObject):

Sinais:
- resultReady(text: str, timestamp: datetime)
- errorOccurred(message: str)

Construtor:
AudioProcessorWorker(queue: queue.Queue)

Métodos:
- start() -> None
- stop() -> None

============================================================
INTERFACES INTERNAS QUE VOCÊ DEVE EXPOR
============================================================

Classe obrigatória:

MainWindow(QMainWindow)

Construtor:
MainWindow(temp_dir: str)

- Recebe caminho do diretório temporário criado pelo main.py
- NÃO cria diretório temporário aqui

Métodos públicos obrigatórios:

1) start_capture() -> None
   - Inicia captura de áudio
   - Inicia worker de processamento
   - Atualiza estado da UI

2) stop_capture() -> None
   - Para captura de áudio
   - Finaliza segmento ativo
   - Mantém worker vivo até fila esvaziar

3) calibrate_noise() -> None
   - Captura ~2 segundos de frames
   - Chama RMSVoiceActivityDetector.calibrate()

4) get_current_mode() -> str
   - Retorna "transcribe" ou "translate"
   - Baseado no estado atual da UI

5) close_application() -> None
   - Encerra captura, segmentação e worker
   - Deve ser idempotente

Slots Qt obrigatórios:

- on_result_ready(text: str, timestamp: datetime)
- on_error(message: str)

Sinal Qt que a MainWindow DEVE EMITIR:

- applicationClosing()

============================================================
ESTADO INTERNO DA MainWindow
============================================================

A MainWindow deve manter:

- self.queue : queue.Queue
- self.vad : RMSVoiceActivityDetector
- self.capture : SystemAudioCapture
- self.segmenter : SpeechSegmenter
- self.worker : AudioProcessorWorker

Além de:
- estado de captura (ativo / parado)
- modo atual (transcribe / translate)

============================================================
INTERFACE GRÁFICA OBRIGATÓRIA
============================================================

A janela deve conter:

- Botão "Iniciar Captura"
- Botão "Parar Captura"
- Botão "Calibrar Ruído"

- Selector de modo:
  - RadioButton OU ComboBox
  - Opções:
    - "Transcrever"
    - "Traduzir"

- QListView com QStandardItemModel
  - Cada item no formato:
    "[HH:MM:SS] texto"

============================================================
COMPORTAMENTO DA APLICAÇÃO
============================================================

START:
- start_capture():
  - cria SystemAudioCapture se não existir
  - conecta callback para SpeechSegmenter.process_frame
  - inicia captura
  - inicia AudioProcessorWorker

STOP:
- stop_capture():
  - para captura
  - chama SpeechSegmenter.stop()

PROCESSAMENTO:
- AudioProcessorWorker emite resultReady
- UI adiciona item no ListView
- Ordem deve respeitar timestamps

ENCERRAMENTO:
- close_application():
  - chama stop_capture()
  - chama worker.stop()
  - emite applicationClosing()

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- A UI NUNCA acessa arquivos WAV
- A UI NUNCA chama transcribe() ou translate()
- A UI NUNCA acessa threads diretamente
- Toda comunicação entre threads é via sinais Qt

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de ui/main_window.py.
Não gere explicações.
Não gere outros arquivos.
Não use pseudocódigo.
O código deve ser funcional quando os outros módulos forem implementados conforme os contratos acima.

