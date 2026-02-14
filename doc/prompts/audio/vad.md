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

audio/vad.py

Não gere nenhum outro arquivo.
Não implemente captura de áudio.
Não implemente UI.
Não implemente threads.
Não salve arquivos.

============================================================
RESPONSABILIDADE EXCLUSIVA DO audio/vad.py
============================================================

Este módulo implementa um detector de atividade de voz (VAD)
extremamente simples e determinístico,
baseado exclusivamente em energia RMS do sinal.

Este módulo NÃO:
- agrupa frames
- salva arquivos
- decide início/fim de segmentos
- usa threads
- usa PyQt

============================================================
DEPENDÊNCIAS PERMITIDAS
============================================================

- numpy
- math
- typing (opcional)

============================================================
INTERFACE PÚBLICA OBRIGATÓRIA
============================================================

Classe obrigatória:

RMSVoiceActivityDetector

Construtor:

__init__(
    sample_rate: int = 16000,
    silence_ratio: float = 0.1
)

Parâmetros:
- sample_rate:
  - taxa de amostragem do áudio
  - usado apenas para referência
- silence_ratio:
  - fração do RMS calibrado abaixo da qual o frame é considerado silêncio
  - valor típico: 0.1 (10%)

============================================================
ESTADO INTERNO
============================================================

A classe deve manter:

- self.rms_calibrated : float | None
  - RMS médio do ruído ambiente
  - None antes da calibração

============================================================
MÉTODOS PÚBLICOS OBRIGATÓRIOS
============================================================

1) calibrate(frames: list[np.ndarray]) -> None

- Recebe uma lista de frames de áudio
- Esses frames representam SOMENTE ruído ambiente
- Calcula RMS médio global
- Salva em self.rms_calibrated

Regras:
- Se frames estiver vazio, não altere o estado
- Ignore frames vazios
- Não lance exceções

------------------------------------------------------------

2) is_speech(frame: np.ndarray) -> bool

- Retorna True se o frame contém fala
- Retorna False se o frame é silêncio

Regras:
- Se self.rms_calibrated for None:
  - Considere TODO frame como fala (True)
- Calcule RMS do frame
- Compare com:
    rms_calibrated * silence_ratio

------------------------------------------------------------

3) rms(frame: np.ndarray) -> float

- Calcula RMS do frame
- Deve funcionar com numpy arrays float32
- Não altera estado interno

============================================================
DEFINIÇÃO MATEMÁTICA DO RMS
============================================================

RMS = sqrt(mean(frame ** 2))

- Use numpy para eficiência
- Trate arrays vazios retornando 0.0

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO use PyQt
- NÃO use threads
- NÃO use timers
- NÃO faça I/O
- NÃO mantenha buffers longos
- NÃO implemente lógica de segmentação

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de audio/vad.py.
Não gere explicações.
Não gere texto fora do código.
Não gere outros arquivos.

O código deve ser:
- pequeno
- determinístico
- fácil de testar isoladamente
- compatível com audio/segmenter.py conforme contrato

