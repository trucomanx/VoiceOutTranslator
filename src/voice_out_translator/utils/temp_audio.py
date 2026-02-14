"""
Módulo para criação e gerenciamento de arquivos WAV temporários.
"""

import os
import uuid
import wave
import shutil
import tempfile
from typing import Optional


from pydub import AudioSegment
import io


def init_temp_dir(prefix="meu_app_", suffix="", base_dir=None):
    """
    Inicializa um diretório temporário
    
    Args:
        prefix: Prefixo para o nome do diretório
        suffix: Sufixo para o nome do diretório
        base_dir: Diretório base (None usa o padrão do sistema)
    
    Returns:
        Caminho do diretório temporário criado

    Uso:
        temp_dir = init_temp_dir(prefix="processamento_", suffix="_data")
        print(temp_dir)  # Ex: /tmp/processamento_xyz123_data

    """
    temp_dir = tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=base_dir)
    return temp_dir

def create_temp_mp3(
    audio_bytes: bytes,
    sample_rate: int,
    channels: int,
    sample_width: int,
    prefix="chunk",
    temp_dir=None,
    bitrate="32k"
) -> str:
    """
    Cria um arquivo MP3 temporário a partir de dados de áudio PCM.
    
    Args:
        audio_bytes: Dados de áudio PCM crus (interleaved se stereo)
        sample_rate: Taxa de amostragem (ex: 16000)
        channels: Número de canais (1 ou 2)
        sample_width: Bytes por amostra (ex: 2 para int16)
        prefix: Prefixo do nome do arquivo
        temp_dir: Diretório temporário (usa sistema se None)
        bitrate: Bitrate do MP3 (ex: "32k", "64k")
    
    Returns:
        Path absoluto do arquivo MP3 criado
    
    Raises:
        Exception: Se houver erro na criação do arquivo
    """
    if temp_dir is None or not isinstance(temp_dir, str):
        temp_dir = tempfile.gettempdir()
    
    filename = f"{prefix}_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(temp_dir, filename)
    
    # Criar AudioSegment a partir dos bytes PCM
    audio = AudioSegment(
        data=audio_bytes,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels
    )
    
    # Exportar como MP3
    audio.export(
        filepath,
        format="mp3",
        bitrate=bitrate,
        parameters=["-ac", "1"]  # forçar mono para economizar mais
    )
    
    return filepath

def create_temp_wav(
    audio_bytes: bytes,
    sample_rate: int,
    channels: int,
    sample_width: int,
    prefix="chunk",
    temp_dir=None
) -> str:
    """
    Cria um arquivo WAV temporário a partir de dados de áudio PCM.
    
    Args:
        audio_bytes: Dados de áudio PCM crus (interleaved se stereo)
        sample_rate: Taxa de amostragem (ex: 16000)
        channels: Número de canais (1 ou 2)
        sample_width: Bytes por amostra (ex: 2 para int16)
    
    Returns:
        Path absoluto do arquivo WAV criado
    
    Raises:
        Exception: Se houver erro na criação do arquivo
    """
    if temp_dir is None or not isinstance(temp_dir, str):
        temp_dir = tempfile.gettempdir()

    
    filename = f"{prefix}_{uuid.uuid4().hex}.wav"
    filepath = os.path.join(temp_dir, filename)
    
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)
    
    return filepath


def cleanup_file(path: str) -> None:
    """
    Remove um arquivo do sistema de arquivos.
    
    Args:
        path: Caminho do arquivo a ser removido
    
    Returns:
        None
    
    Note:
        Não lança exceção se o arquivo não existir ou houver erro.
    """
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass



def cleanup_all(dir_path: str) -> None:
    """Remove todos os arquivos e o próprio diretório"""
    if not os.path.isdir(dir_path):
        return
    
    # Opção 1: Usar shutil.rmtree (mais simples e recomendado)
    shutil.rmtree(dir_path)

