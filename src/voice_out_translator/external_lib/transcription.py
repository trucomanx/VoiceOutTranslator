"""
Simulação de biblioteca de transcrição e tradução de áudio.
Este módulo fornece stubs para testes do pipeline.
"""

#import time
import random

from deep_consultation.core_audio import speech_file_transcript_deepinfra
from deep_consultation.core_audio import speech_file_translate_deepinfra

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
    
    print(audio_path)
    OUT=speech_file_translate_deepinfra(config_gpt["base_url"],
                                        config_gpt["api_key"],
                                        config_gpt["model_translate"],
                                        audio_path )
    
    return OUT
    

