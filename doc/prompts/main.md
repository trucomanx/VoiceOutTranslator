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

main.py

Não gere nenhum outro arquivo.
Não implemente lógica de áudio.
Não implemente UI.
Não implemente threads manualmente.
Não replique código de outros módulos.

============================================================
RESPONSABILIDADE EXCLUSIVA DO main.py
============================================================

O arquivo main.py deve:

1) Inicializar a aplicação PyQt5 (QApplication)
2) Inicializar o sistema de arquivos temporários de áudio
3) Criar e exibir a janela principal (MainWindow)
4) Conectar o encerramento da aplicação a uma limpeza completa
5) Garantir shutdown limpo de threads, captura de áudio e arquivos temporários

O main.py é o ORQUESTRADOR DE ALTO NÍVEL.
Ele não conhece detalhes internos dos outros módulos.

============================================================
INTERFACES EXTERNAS QUE VOCÊ DEVE ASSUMIR COMO EXISTENTES
============================================================

--- utils/temp_audio.py ---

Assuma que existe o seguinte módulo e funções:

from utils.temp_audio import (
    init_temp_dir,
    cleanup_all
)

Contratos:

init_temp_dir() -> str
- Cria um diretório temporário exclusivo para o app
- Retorna o caminho do diretório
- Deve ser chamado UMA VEZ no startup

cleanup_all() -> None
- Remove todos os arquivos temporários e o diretório
- Pode ser chamado múltiplas vezes sem erro
- Deve ser chamado no encerramento do app


--- ui/main_window.py ---

Assuma que existe a seguinte classe:

from ui.main_window import MainWindow

Contrato da classe MainWindow(QMainWindow):

Construtor:
MainWindow(temp_dir: str)

- Recebe o caminho do diretório temporário
- Internamente inicializa:
  - captura de áudio
  - segmentação
  - fila
  - worker de processamento
- main.py NÃO deve acessar esses detalhes

Métodos públicos que EXISTEM e podem ser chamados:

- close_application() -> None
  - Solicita encerramento limpo:
    - para captura
    - para threads
    - esvazia filas

Sinais Qt que a MainWindow EMITE:

- applicationClosing()
  - Emitido quando a janela está fechando
  - Deve ser conectado a rotinas de cleanup globais

============================================================
COMPORTAMENTO DE STARTUP
============================================================

Ao iniciar o programa:

1) Criar QApplication
2) Chamar init_temp_dir() e guardar o path retornado
3) Criar MainWindow(temp_dir)
4) Exibir a janela
5) Iniciar o loop Qt (app.exec_())

============================================================
COMPORTAMENTO DE SHUTDOWN (CRÍTICO)
============================================================

O encerramento deve ser LIMPO e DETERMINÍSTICO.

Ao fechar a janela ou sair do app:

1) Chamar MainWindow.close_application()
2) Chamar cleanup_all() do utils/temp_audio
3) Garantir que QApplication finalize sem exceções

Implemente pelo menos UMA destas abordagens (ou ambas):

- Sobrescrever signal handling (SIGINT / SIGTERM)
- Conectar QApplication.aboutToQuit

O código deve tolerar:
- Fechamento manual da janela
- Ctrl+C no terminal
- Exceções inesperadas

============================================================
REQUISITOS TÉCNICOS
============================================================

- Use PyQt5
- Código claro e comentado
- Sem lógica de áudio
- Sem lógica de processamento pesado
- main.py NÃO deve criar QThreads manualmente
- main.py NÃO deve acessar filas
- main.py NÃO deve acessar arquivos WAV

============================================================
RESULTADO ESPERADO
============================================================

O arquivo main.py deve:

- Ser pequeno, limpo e orquestrador
- Conectar corretamente todos os pontos de inicialização e encerramento
- Não conter lógica que pertença a outros módulos
- Ser totalmente funcional quando os outros arquivos forem implementados

Gere APENAS o código de main.py.
Não explique o código.
Não gere texto fora do código.

