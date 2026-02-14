import queue
import datetime
from PyQt5.QtCore import QThread, pyqtSignal

from voice_out_translator.external_lib.transcription import transcribe, translate
from voice_out_translator.utils.temp_audio import cleanup_file


class AudioProcessorWorker(QThread):
    resultReady = pyqtSignal(str, datetime.datetime)
    errorOccurred = pyqtSignal(str)

    def __init__(self, queue: queue.Queue, config_gpt: dict):
        super().__init__()
        self._queue = queue
        self.config_gpt = config_gpt
        self._running = True  # Inicialmente True, start() mantém

    def start(self):
        """
        Sobrescrevemos start() apenas para garantir compatibilidade.
        Chama o start() original do QThread para executar run() em outra thread.
        """
        self._running = True
        super().start()  # ⚡ agora run() roda em thread separada

    def stop(self):
        """
        Para o processamento e coloca None na fila para liberar get()
        """
        self._running = False
        try:
            self._queue.put(None, block=False)
        except queue.Full:
            pass

    def run(self):
        """
        Loop de processamento da fila rodando na thread separada
        """
        while self._running:
            try:
                item = self._queue.get(timeout=0.1)

                if item is None:
                    continue

                self._process_item(item)

            except queue.Empty:
                continue
            except Exception as e:
                self.errorOccurred.emit(str(e))

    def _process_item(self, item):
        """
        Processa cada item da fila
        """
        path = None
        try:
            path = item["path"]
            timestamp = item["timestamp"]
            mode = item["mode"]

            if mode == "transcribe":
                text = transcribe(path,self.config_gpt)
            elif mode == "translate":
                text = translate(path,self.config_gpt)
            else:
                raise ValueError(f"Invalid mode: {mode}")

            self.resultReady.emit(text, timestamp)

        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            if path is not None:
                cleanup_file(path)

