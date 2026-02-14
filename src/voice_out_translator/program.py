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
    "language_transcript": "pt"
}

configure.verify_default_config(CONFIG_GPT_PATH,default_content=DEFAULT_GPT_CONTENT)


def main():
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    
    # Inicializar diretório temporário
    temp_dir = init_temp_dir(prefix="audio_")
    virtual_monitor_name = "VirtualOutput"

    print("            temp_dir:",temp_dir)
    print("virtual_monitor_name:",virtual_monitor_name)
    
    # Criar janela principal
    main_window = MainWindow(temp_dir, virtual_monitor_name)
    
    # Conectar encerramento da aplicação ao cleanup
    app.aboutToQuit.connect(lambda: cleanup_all(temp_dir))
    main_window.applicationClosing.connect(lambda: cleanup_all(temp_dir))
    
    # Handler para sinais do sistema (Ctrl+C)
    def signal_handler(signum, frame):
        main_window.close_application()
        cleanup_all(temp_dir)
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Permitir Ctrl+C funcionar corretamente
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    
    # Exibir janela
    main_window.show()
    
    # Iniciar loop Qt
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
