"""
audio/capture.py

Captura áudio da saída do sistema (system output) no Ubuntu.
Entrega frames contínuos via callback.
"""

import os
import numpy as np
import sounddevice as sd
from typing import Callable


class SystemAudioCapture:
    """
    Captura áudio da saída do sistema usando monitor do PulseAudio.
    """

    def __init__(
        self,
        sample_rate: int,
        frame_duration: float,
        callback: Callable[[np.ndarray], None],
        sink_name: str = "VirtualOutput"
    ):
        """
        Inicializa captura de áudio do sistema.

        Args:
            sample_rate: Taxa de amostragem (ex: 16000)
            frame_duration: Duração do frame em segundos (ex: 0.02)
            callback: Função que recebe cada frame de áudio
            sink_name: Nome do sink virtual (ex: VirtualOutput)
        """
        self.sink_name = sink_name
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.callback = callback
        self.blocksize = int(sample_rate * frame_duration)
        self.stream = None
        
        # 🔑 informa ao Pulse qual source capturar
        os.environ["PULSE_SOURCE"] = f"{self.sink_name}.monitor"

        # mantido por compatibilidade com outros arquivos
        self.device_index = self._find_monitor_device()

    def _find_monitor_device(self) -> str:
        """
        Encontra o monitor do sink virtual configurado.

        Raises:
            RuntimeError: se o monitor não for encontrado
        """
        return "pulse"

    def _audio_callback(self, indata, frames, time, status):
        """
        Callback interno chamado pela biblioteca de áudio.

        Args:
            indata: Dados de áudio capturados
            frames: Número de frames
            time: Informação de timing
            status: Status da captura
        """
        if status:
            print(f"Status: {status}")
        
        # Converte para mono float32
        audio_frame = indata[:, 0].astype(np.float32).copy()

        # Entrega ao callback externo
        self.callback(audio_frame)

    def start(self) -> None:
        """
        Inicia a captura de áudio.
        """

        if self.stream is not None:
            return

        self.stream = sd.InputStream(
            device=self.device_index,   # <- "pulse"
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.blocksize,
            dtype=np.float32,
            callback=self._audio_callback
        )

        self.stream.start()


    def stop(self) -> None:
        """
        Para a captura de áudio e libera recursos.
        """
        if self.stream is None:
            return

        self.stream.stop()
        self.stream.close()
        self.stream = None

