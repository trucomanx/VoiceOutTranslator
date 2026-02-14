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

utils/temp_audio.py

Não gere nenhum outro arquivo.
Não implemente UI.
Não implemente captura de áudio.
Não implemente transcrição.

============================================================
RESPONSABILIDADE EXCLUSIVA DO utils/temp_audio.py
============================================================

Este módulo é responsável por:

- Criar arquivos WAV temporários
- Gerenciar nomes únicos de arquivos
- Garantir escrita correta no sistema de arquivos
- Limpar arquivos temporários após uso

Este módulo NÃO faz processamento de áudio.
Este módulo NÃO conhece VAD.
Este módulo NÃO conhece threads.
Este módulo NÃO conhece PyQt.

============================================================
DEPENDÊNCIAS PERMITIDAS
============================================================

Bibliotecas padrão permitidas:

- os
- tempfile
- uuid
- wave
- contextlib
- pathlib
- typing

NÃO use bibliotecas externas.

============================================================
INTERFACE PÚBLICA OBRIGATÓRIA
============================================================

O módulo DEVE expor exatamente estas duas funções públicas:

------------------------------------------------------------
1) create_temp_wav
------------------------------------------------------------

Assinatura obrigatória:

create_temp_wav(
    audio_bytes: bytes,
    sample_rate: int,
    channels: int,
    sample_width: int
) -> str

Descrição:

- Cria um arquivo WAV temporário no diretório do sistema (/tmp)
- Nome deve ser único
- Extensão obrigatória: ".wav"
- Deve escrever corretamente o header WAV
- Retorna o path absoluto do arquivo gerado

Parâmetros:

- audio_bytes:
    bytes PCM crus (interleaved se stereo)
- sample_rate:
    ex: 16000
- channels:
    1 ou 2
- sample_width:
    bytes por amostra (ex: 2 para int16)

Regras:
- O arquivo deve ser fechado corretamente
- Erros devem levantar exceção

------------------------------------------------------------
2) cleanup_file
------------------------------------------------------------

Assinatura obrigatória:

cleanup_file(path: str) -> None

Descrição:

- Remove o arquivo indicado
- Se o arquivo não existir:
    - NÃO lançar exceção
- Se ocorrer erro inesperado:
    - NÃO propagar exceção

============================================================
DETALHES DE IMPLEMENTAÇÃO OBRIGATÓRIOS
============================================================

- Use tempfile.gettempdir() ou tempfile.NamedTemporaryFile(delete=False)
- NÃO use delete=True
- NÃO deixe arquivos abertos
- Garanta flush e close

============================================================
INTERCONEXÕES COM OUTROS MÓDULOS
============================================================

Este módulo será usado por:

- audio/segmenter.py
- workers/processor.py

Assuma que outros módulos farão:

from utils.temp_audio import create_temp_wav, cleanup_file

Portanto:
- Os nomes das funções devem ser EXATAMENTE estes
- As assinaturas devem ser EXATAMENTE estas

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO crie classes
- NÃO use threads
- NÃO use PyQt
- NÃO registre logs
- NÃO imprima nada
- NÃO tente fazer cache
- NÃO retenha estado global

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de utils/temp_audio.py.
Não gere explicações.
Não gere comentários fora do código.
Não gere pseudocódigo.

O código deve ser:
- simples
- seguro
- previsível
- portável em Linux

