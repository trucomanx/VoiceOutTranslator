"""
audio/vad.py

Voice Activity Detector baseado em energia RMS.
Detector simples e determinístico sem dependências externas complexas.
"""

import numpy as np


class RMSVoiceActivityDetector:
    """
    Detector de atividade de voz baseado em energia RMS.
    
    Compara a energia RMS de cada frame com um limiar calibrado
    para determinar se contém fala ou silêncio.
    """
    
    def __init__(self, sample_rate: int = 16000, silence_ratio: float = 1.2):
        """
        Inicializa o detector.
        
        Args:
            sample_rate: Taxa de amostragem do áudio (usado para referência)
            silence_ratio: Fração do RMS calibrado considerada como silêncio
        """
        self.sample_rate = sample_rate
        self.silence_ratio = silence_ratio
        self.rms_calibrated: float = 0.0
    
    def calibrate(self, frames: list[np.ndarray]) -> None:
        """
        Calibra o detector usando frames de ruído ambiente.
        
        Args:
            frames: Lista de frames de áudio contendo apenas ruído ambiente
        """
        if not frames:
            return
        
        rms_values = []
        for frame in frames:
            if len(frame) > 0:
                rms_values.append(self.rms(frame))
        
        if rms_values:
            self.rms_calibrated = float(np.mean(rms_values))
        
        print(self.rms_calibrated)
    
    def is_speech(self, frame: np.ndarray) -> bool:
        """
        Determina se um frame contém fala.
        
        Args:
            frame: Frame de áudio
            
        Returns:
            True se contém fala, False se é silêncio
        """
        if self.rms_calibrated == 0:
            return True
        
        frame_rms = self.rms(frame)
        threshold = self.rms_calibrated * self.silence_ratio
        
        return frame_rms > threshold
    
    def rms(self, frame: np.ndarray) -> float:
        """
        Calcula o RMS (Root Mean Square) de um frame.
        
        Args:
            frame: Frame de áudio
            
        Returns:
            Valor RMS do frame
        """
        if len(frame) == 0:
            return 0.0
        
        return float(np.sqrt(np.mean(frame ** 2)))
