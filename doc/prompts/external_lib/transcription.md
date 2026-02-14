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

external_lib/transcription.py

Não gere nenhum outro arquivo.
Não implemente UI.
Não implemente captura de áudio.
Não use modelos reais de IA.

============================================================
RESPONSABILIDADE EXCLUSIVA DO external_lib/transcription.py
============================================================

Este módulo simula (mocka) uma biblioteca pesada de
transcrição e tradução de áudio.

Ele existe apenas para:
- permitir testes do pipeline
- garantir contratos de interface
- simular latência variável

============================================================
DEPENDÊNCIAS PERMITIDAS
============================================================

Bibliotecas padrão permitidas:

- time
- random
- typing

============================================================
INTERFACE PÚBLICA OBRIGATÓRIA
============================================================

O módulo DEVE expor exatamente estas DUAS funções públicas:

------------------------------------------------------------
1) transcribe
------------------------------------------------------------

Assinatura obrigatória:

transcribe(audio_path: str) -> str

Descrição:

- Simula a transcrição de um arquivo de áudio
- Ignora completamente o conteúdo do arquivo
- Retorna uma string fixa ou semi-aleatória em português

Comportamento obrigatório:
- Introduzir atraso artificial entre 0.5 e 2.0 segundos
- Retornar sempre uma string NÃO vazia

Exemplos válidos de retorno:
- "oi a todos"
- "teste de transcrição"
- "áudio capturado com sucesso"

------------------------------------------------------------
2) translate
------------------------------------------------------------

Assinatura obrigatória:

translate(audio_path: str) -> str

Descrição:

- Simula a tradução de um áudio para português
- Ignora completamente o conteúdo do arquivo
- Retorna uma string fixa ou semi-aleatória em português

Comportamento obrigatório:
- Introduzir atraso artificial entre 0.5 e 2.0 segundos
- Retornar sempre uma string NÃO vazia

Exemplos válidos de retorno:
- "olá a todos"
- "isso é uma tradução simulada"
- "texto traduzido para português"

============================================================
INTERCONEXÕES COM OUTROS MÓDULOS
============================================================

Este módulo será usado por:

- workers/processor.py

Assuma que outros módulos farão:

from external_lib.transcription import transcribe, translate

Portanto:
- Os nomes das funções devem ser EXATAMENTE estes
- As assinaturas devem ser EXATAMENTE estas

============================================================
RESTRIÇÕES CRÍTICAS
============================================================

- NÃO valide se o arquivo existe
- NÃO abra o arquivo
- NÃO leia o áudio
- NÃO use bibliotecas externas
- NÃO registre logs
- NÃO imprima nada
- NÃO lance exceções

============================================================
RESULTADO ESPERADO
============================================================

Gere APENAS o código de external_lib/transcription.py.
Não gere explicações.
Não gere texto fora do código.
Não gere comentários fora do código.

O código deve ser:
- extremamente simples
- determinístico no contrato
- útil como stub de testes

