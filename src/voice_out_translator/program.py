#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import signal
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from voice_out_translator.ui.main_window import MainWindow
from voice_out_translator.utils.temp_audio import init_temp_dir, cleanup_all

import voice_out_translator.about as about
import voice_out_translator.modules.configure as configure
from voice_out_translator.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu

# ---------- Path to config gpt file ----------
CONFIG_GPT_PATH = os.path.join( os.path.expanduser("~"),
                                ".config", 
                                about.__package__, 
                                "config.gpt.json" )
DEFAULT_GPT_CONTENT={
    "api_key": "",
    "usage": "https://deepinfra.com/dash/usage",
    "base_url": "https://api.deepinfra.com/v1/openai",
    "model_transcript": "mistralai/Voxtral-Mini-3B-2507",
    "language_transcript": "pt",
    "model_translate": "openai/whisper-large-v3"
}

configure.verify_default_config(CONFIG_GPT_PATH,default_content=DEFAULT_GPT_CONTENT)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Voice Out Translator - Translate and transcribe audio output/input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
      Run with default settings (output monitoring)
  
  %(prog)s --source-type output --device-name VirtualOutput
      Explicitly monitor audio output
  
  %(prog)s --source-type input --device-name VirtualInput
      Monitor audio input (microphone)
  
  %(prog)s --autostart
      Install autostart desktop file
  
  %(prog)s --applications
      Install application menu entry
        """
    )
    
    parser.add_argument(
        '--source-type',
        choices=['output', 'input'],
        default='output',
        help='Type of audio source to monitor (default: output)'
    )
    
    parser.add_argument(
        '--device-name',
        type=str,
        default=None,
        help='Name of virtual device (default: VirtualOutput for output, VirtualInput for input)'
    )
    
    parser.add_argument(
        '--autostart',
        action='store_true',
        help='Install autostart desktop file and exit'
    )
    
    parser.add_argument(
        '--applications',
        action='store_true',
        help='Install application menu entry and exit'
    )
    
    return parser.parse_args()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Parse argumentos
    args = parse_arguments()
    
    # Determinar nome do dispositivo baseado no source-type se não especificado
    if args.device_name is None:
        if args.source_type == 'output':
            args.device_name = 'VirtualOutput'
        else:  # input
            args.device_name = 'VirtualInput'
    
    # Criar desktop files se solicitado
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"))
    
    if args.autostart:
        create_desktop_directory(overwrite=True)
        create_desktop_menu(overwrite=True)
        create_desktop_file(os.path.join("~",".config","autostart"), overwrite=True)
        return
    
    if args.applications:
        create_desktop_directory(overwrite=True)
        create_desktop_menu(overwrite=True)
        create_desktop_file(os.path.join("~",".local","share","applications"), overwrite=True)
        return
    
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    
    # Inicializar diretório temporário
    temp_dir = init_temp_dir(prefix="audio_")
    
    print("       source_type:", args.source_type)
    print("       device_name:", args.device_name)
    print("          temp_dir:", temp_dir)
    
    # Criar janela principal
    main_window = MainWindow(
        temp_dir=temp_dir,
        source_type=args.source_type,
        device_name=args.device_name
    )
    
    # Conectar encerramento da aplicação ao cleanup
    app.aboutToQuit.connect(lambda: cleanup_all(temp_dir))
    
    # Exibir janela
    main_window.show()
    
    # Iniciar loop Qt
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
