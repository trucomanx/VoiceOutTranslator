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

audio/capture.py

Não gere nenhum outro arquivo.
Não implemente UI.
Não implemente VAD.
Não salve arquivos.
Não use PyQt.
Não implemente processamento pesado.

============================================================
RESPONSABILIDADE EXCLUSIVA DO audio/capture.py
============================================================

Este arquivo é responsável APENAS por:

- Capturar áudio da SAÍDA DO SISTEMA (system output) no Ubuntu
- Entregar frames de áudio pequenos e contínuos
- Chamar uma callback fornecida pelo chamador
- Iniciar e parar a captura de forma segura

Este módulo NÃO decide nada.
Ele apenas CAPTURA e ENTREGA áudio.

============================================================
BIBLIOTECAS E AMBIENTE
============================================================

- Linguagem: Python 3
- Sistema: Ubuntu
- Backend de áudio: PulseAudio ou PipeWire
- Biblioteca recomendada:
  - sounddevice (preferencial)
  - fallback aceitável: pyaudio

Use sounddevice SE POSSÍVEL.

============================================================
INTERFACE EXTERNA QUE VOCÊ DEVE EXPOR
============================================================

Classe obrigatória:

SystemAudioCapture

Construtor OBRIGATÓRIO:

SystemAudioCapture(
    sample_rate: int,
    frame_duration: float,
    callback: Callable[[np.ndarray], None]
)

Parâmetros:
- sample_rate:
    - Ex: 16000
- frame_duration:
    - Em segundos
    - Ex: 0.02 (20 ms)
- callback:
    - Função que recebe um frame de áudio
    - Assinatura: callback(frame: np.ndarray) -> None

============================================================
COMPORTAMENTO DA CAPTURA
============================================================

- A captura deve:
  - Capturar o áudio que está sendo REPRODUZIDO no sistema
  - NÃO usar microfone
  - Usar device "monitor" do sistema (PulseAudio/PipeWire)
- Áudio deve ser:
  - Mono
  - float32
  - numpy.ndarray
- Cada frame deve conter aproximadamente:
  sample_rate * frame_duration amostras

============================================================
MÉTODOS PÚBLICOS OBRIGATÓRIOS
============================================================

1) start() -> None

- Inicia a captura de áudio
- Registra callback de áudio
- Pode rodar em thread interna da biblioteca
- Deve ser não-bloqueante

2) stop() -> None

- Para a captura de áudio
- Garante liberação de recursos
- Pode ser chamado múltiplas vezes sem erro

============================================================
IMPLEMENTAÇÃO (REGRAS)
============================================================

- Use callback de áudio da biblioteca escolhida
- Não implemente loops while manuais
- Não use threads explícitas (threading.Thread)
- Confie no mecanismo interno da biblioteca de áudio
- Trate exceções de device inexistente
- Se nenhum device monitor for encontrado:
  - Lance RuntimeError com mensagem clara

============================================================
INTERAÇÃO COM OUTROS MÓDULOS
============================================================

Este arquivo SERÁ USADO ASSIM:

from audio.capture import SystemAudioCapture

capture = SystemAudioCapture(
    sample_rate=16000,
    frame_duration=0.02,
    callback=some_function
)

capture.start()
...
capture.stop()

O módulo chamador NÃO deve saber detalhes internos
sobre dispositivos, streams ou callbacks.

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO use PyQt
- NÃO salve WAV
- NÃO processe RMS
- NÃO implemente VAD
- NÃO implemente fila
- NÃO implemente lógica de negócio

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de audio/capture.py.
Não gere explicações.
Não gere pseudocódigo.
Não gere outros arquivos.

O código deve ser funcional em Ubuntu
quando integrado com os demais módulos
que seguem os contratos definidos.

