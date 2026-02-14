"""
Simulação de biblioteca de transcrição e tradução de áudio.
Este módulo fornece stubs para testes do pipeline.
"""

#import time
import random

from deep_consultation.core_audio import speech_file_transcript_deepinfra

from pydub import AudioSegment
import os

def transcribe(audio_path: str, config_gpt: dict) -> str:
    """
    Simula transcrição de áudio.
    
    Args:
        audio_path: Caminho do arquivo de áudio (ignorado)
    
    Returns:
        String simulada em português
    """
    #time.sleep(random.uniform(0.5, 2.0))
    print(audio_path)
    OUT=speech_file_transcript_deepinfra(   config_gpt["base_url"],
                                            config_gpt["api_key"],
                                            config_gpt["model_transcript"],
                                            audio_path,
                                            language=config_gpt["language_transcript"])
    
    return OUT


def translate(audio_path: str, config_gpt: dict) -> str:
    """
    Simula tradução de áudio para português.
    
    Args:
        audio_path: Caminho do arquivo de áudio (ignorado)
    
    Returns:
        String simulada em português
    """
    #time.sleep(random.uniform(0.5, 2.0))
    print(audio_path)
    OUT=speech_file_transcript_deepinfra(   config_gpt["base_url"],
                                            config_gpt["api_key"],
                                            config_gpt["model_transcript"],
                                            audio_path,
                                            language=config_gpt["language_transcript"])
    
    return OUT
    
    
'''
def transcribe(audio_path: str, config_gpt: dict) -> str:
    """
    Transcreve áudio convertendo primeiro para MP3.
    
    Args:
        audio_path: Caminho do arquivo de áudio WAV
        config_gpt: Configuração da API
    
    Returns:
        Texto transcrito
    """
    # Converter WAV para MP3
    mp3_path = audio_path + ".mp3"
    
    try:
        # Carregar WAV e exportar como MP3
        audio = AudioSegment.from_wav(audio_path)
        audio.export(
            mp3_path,
            format="mp3",
            bitrate="32k",
            parameters=["-ac", "1"]  # mono
        )
        
        print(f"Convertido: {audio_path} -> {mp3_path}")
        
        # Enviar MP3 em vez de WAV
        OUT = speech_file_transcript_deepinfra(
            config_gpt["base_url"],
            config_gpt["api_key"],
            config_gpt["model_transcript"],
            mp3_path,  # ← Usar MP3
            language=config_gpt["language_transcript"]
        )
        
        return OUT
        
    finally:
        # Limpar arquivo MP3 temporário após uso
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
'''
