#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import signal
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


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"))
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), overwrite=True)
            return
    
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    
    # Inicializar diretório temporário
    temp_dir = init_temp_dir(prefix="audio_")
    virtual_monitor_name = "VirtualOutput"
    print("            temp_dir:",temp_dir)
    print("virtual_monitor_name:",virtual_monitor_name)
    
    # Criar janela principal
    main_window = MainWindow(temp_dir, virtual_monitor_name)
    
    # Conectar encerramento da aplicação ao cleanup
    app.aboutToQuit.connect(lambda: cleanup_all(temp_dir))
    
    # Exibir janela
    main_window.show()
    
    # Iniciar loop Qt
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
