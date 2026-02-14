import os
import json
import queue
import subprocess
from datetime import datetime
from typing import Callable

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QSize
from PyQt5.QtWidgets import (
    QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QFileDialog, 
    QHBoxLayout, QPushButton, QRadioButton, QButtonGroup, QMessageBox, 
    QListView, QLabel, QDoubleSpinBox, QSpinBox, QStyledItemDelegate
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QDesktopServices, QFont


from voice_out_translator.audio.vad import RMSVoiceActivityDetector
from voice_out_translator.audio.capture import SystemAudioCapture
from voice_out_translator.audio.segmenter import SpeechSegmenter
from voice_out_translator.workers.processor import AudioProcessorWorker

import voice_out_translator.about             as about
import voice_out_translator.modules.configure as configure

from voice_out_translator.modules.resources import resource_path
from voice_out_translator.modules.wabout    import show_about_window


# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )

DEFAULT_CONTENT={   
    "toolbar_save": "Save as",
    "toolbar_save_tooltip": "Save as the listview content as JSON file",
    "toolbar_gpt_conf": "LLM Conf.",
    "toolbar_gpt_conf_tooltip": "Open the configure Json file of LLM.",
    "toolbar_url_usage": "LLM Usage",
    "toolbar_url_usage_tooltip": "Open the web page that shows the data usage and cost.",
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "btn_start": "Start Capture",
    "btn_start_tooltip": "Start the capture of audio from the standard output",
    "btn_stop": "Stop Capture",
    "btn_stop_tooltip": "Stop capture of audio",
    "mode_label": "Mode:",
    "mode_label_tooltip": "Configure the mode of the speech-to-text conversion.",
    "mode_radio_transcribe": "Transcribe",
    "mode_radio_transcribe_tooltip": "Transcribe the audio in the same language of audio",
    "mode_radio_translate": "Translate",
    "mode_radio_translate_tooltip": "Translate the audio from any language to english",
    "rms_noise_calibration": "RMS Noise Calibration:",
    "rms_noise_calibration_tooltip": "Set the RMS Noise value, which is normalized to 1.0 and used to determine when an audio frame is considered a silence frame.",
    "btn_calibrate": "Calibrate Noise",
    "btn_calibrate_tooltip": "To obtain the RMS audio value of some frames of the current output audio, this value is used as an RMS noise calibration.",
    "font_label": "Set font size:",
    "font_label_tooltip": "Set the font size value in the list view of transcriptions/translations.",
    "save_transcriptions": "Save transcriptions",
    "error": "Error",
    "success": "Success",
    "window_width": 800,
    "window_height": 600
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)


# ---------- Path to GPT config file ----------

CONFIG_GPT_PATH = os.path.join( os.path.expanduser("~"),
                                ".config", 
                                about.__package__, 
                                "config.gpt.json" )

CONFIG_GPT=configure.load_config(CONFIG_GPT_PATH)

SAMPLE_RATE = 8000

# ---------------------------------------------




# Adicione esta classe antes da MainWindow
class WordWrapDelegate(QStyledItemDelegate):
    """Delegate que permite quebra de linha automática no QListView"""
    
    def paint(self, painter, option, index):
        # Configurar para quebrar texto
        option.features |= option.HasDisplay
        super().paint(painter, option, index)
    
    def sizeHint(self, option, index):
        # Calcular altura necessária para o texto com quebra de linha
        text = index.data(Qt.DisplayRole)
        if not text:
            return super().sizeHint(option, index)
        
        # Criar um QTextDocument para calcular altura com word wrap
        from PyQt5.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setTextWidth(option.rect.width())
        doc.setDefaultFont(option.font)
        doc.setPlainText(text)
        
        return QSize(option.rect.width(), int(doc.size().height()))
        
class MainWindow(QMainWindow):
    applicationClosing = pyqtSignal()
    calibrationComplete = pyqtSignal(float)  # ← Novo sinal

    def __init__(self, temp_dir: str, source_type: str, device_name: str):
        super().__init__()
        self.temp_dir = temp_dir
        self.source_type = source_type
        self.device_name = device_name
        
        # Setup virtual device based on source type
        if source_type == 'output':
            from voice_out_translator.utils.virtual_out import setup_virtual_output
            setup_virtual_output(virtual_sink=device_name)
        else:  # input
            from voice_out_translator.utils.virtual_in import setup_virtual_input
            setup_virtual_input(virtual_sink=device_name)
        
        self.setWindowTitle(about.__program_name__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path("icons", "logo.png")
        self.setWindowIcon(QIcon(self.icon_path)) 
        
        # Estado interno
        self.queue = queue.Queue()
        self.vad = RMSVoiceActivityDetector(sample_rate=SAMPLE_RATE, silence_ratio=1.15) 
        self.capture = None
        self.segmenter = None
        self.worker = None
        
        self.is_capturing = False
        self.current_mode = "transcribe"
        
        # Calibração
        self.calibration_frames = []
        self.is_calibrating = False
        
        self._create_toolbar()
        self._setup_ui()
        self._setup_worker()
        
        self.calibrationComplete.connect(self._update_rms_spinbox)  


    def _create_toolbar(self):
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)



        #
        self.save_action = QAction(QIcon.fromTheme("document-save-as"), 
                                   CONFIG["toolbar_save"], 
                                   self)
        self.save_action.setToolTip(CONFIG["toolbar_save_tooltip"])
        self.save_action.triggered.connect(self.save_transcriptions)
        self.toolbar.addAction(self.save_action)

        # Adicionar o espaçador
        self.toolbar_spacer = QWidget()
        self.toolbar_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toolbar.addWidget(self.toolbar_spacer)
        
        #
        self.configure_action = QAction(QIcon.fromTheme("document-properties"), 
                                        CONFIG["toolbar_configure"], 
                                        self)
        self.configure_action.setToolTip(CONFIG["toolbar_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)
        self.toolbar.addAction(self.configure_action)
        
        #
        self.gpt_conf_action = QAction( QIcon.fromTheme("document-properties"), 
                                        CONFIG["toolbar_gpt_conf"], 
                                        self)
        self.gpt_conf_action.setToolTip(CONFIG["toolbar_gpt_conf_tooltip"])
        self.gpt_conf_action.triggered.connect(self.open_llm_conf_editor)
        self.toolbar.addAction(self.gpt_conf_action)
        
        #
        self.url_usage_action = QAction(QIcon.fromTheme("emblem-web"), 
                                        CONFIG["toolbar_url_usage"], 
                                        self)
        self.url_usage_action.setToolTip(CONFIG["toolbar_url_usage_tooltip"])
        self.url_usage_action.triggered.connect(self.open_url_usage_editor)
        self.toolbar.addAction(self.url_usage_action)
        
        #
        self.about_action = QAction(QIcon.fromTheme("help-about"), 
                                    CONFIG["toolbar_about"], 
                                    self)
        self.about_action.setToolTip(CONFIG["toolbar_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        self.toolbar.addAction(self.about_action)
        
        # Coffee
        self.coffee_action = QAction(   QIcon.fromTheme("emblem-favorite"), 
                                        CONFIG["toolbar_coffee"], 
                                        self)
        self.coffee_action.setToolTip(CONFIG["toolbar_coffee_tooltip"])
        self.coffee_action.triggered.connect(self.on_coffee_action_click)
        self.toolbar.addAction(self.coffee_action)

        # Conectar ao sinal de mudança de orientação
        self.toolbar.orientationChanged.connect(self._update_spacer_policy)
        self._update_spacer_policy()

    def _update_spacer_policy(self):
        """Atualiza a política do espaçador baseado na orientação da toolbar"""
        if self.toolbar.orientation() == Qt.Horizontal:
            # Horizontal: expande na largura
            self.toolbar_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            # Vertical: expande na altura
            self.toolbar_spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def save_transcriptions(self):
        """Salva todas as transcrições em um arquivo JSON"""
        
        # Abrir diálogo para escolher onde salvar
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            CONFIG["save_transcriptions"],
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filepath:  # Usuário cancelou
            return
        
        # Adicionar extensão .json se não tiver
        if not filepath.endswith('.json'):
            filepath += '.json'
        
        # Coletar todas as entradas da lista
        transcriptions = []
        for row in range(self.list_model.rowCount()):
            item = self.list_model.item(row)
            if item:
                transcriptions.append(item.text())
        
        # Salvar em JSON
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(transcriptions, f, ensure_ascii=False, indent=2)
            
            # Opcional: mostrar mensagem de sucesso
            QMessageBox.information(self, CONFIG["success"], f"Saved in:\n{filepath}")
            
        except Exception as e:
            print(CONFIG["error"]+f":{e}")
            QMessageBox.critical(self, CONFIG["error"], f"Error saving file:\n{str(e)}")

    def _open_file_in_text_editor(self, filepath):
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', filepath])
    
    def open_url_usage_editor(self):
        QDesktopServices.openUrl(QUrl(CONFIG_GPT["usage"]))
        
    def open_configure_editor(self):
        self._open_file_in_text_editor(CONFIG_PATH)
        
    def open_llm_conf_editor(self):
        self._open_file_in_text_editor(CONFIG_GPT_PATH)

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    
        
    
    def _setup_ui(self):
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Botões de controle
        button_layout = QHBoxLayout()
        
       
        self.btn_start = QPushButton(CONFIG["btn_start"])
        self.btn_start.setIcon(QIcon.fromTheme("media-record"))
        self.btn_start.setToolTip(CONFIG["btn_start_tooltip"])
        self.btn_start.clicked.connect(self.start_capture)
        button_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton(CONFIG["btn_stop"])
        self.btn_stop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.btn_stop.setToolTip(CONFIG["btn_stop_tooltip"])
        self.btn_stop.clicked.connect(self.stop_capture)
        self.btn_stop.setEnabled(False)
        button_layout.addWidget(self.btn_stop)

        
        main_layout.addLayout(button_layout)
        
        
        # Selector de modo
        mode_layout = QHBoxLayout()
        mode_label = QLabel(CONFIG["mode_label"])
        mode_label.setToolTip(CONFIG["mode_label_tooltip"])
        mode_layout.addWidget(mode_label)
        
        
        self.radio_transcribe = QRadioButton(CONFIG["mode_radio_transcribe"])
        self.radio_translate  = QRadioButton(CONFIG["mode_radio_translate"])
        self.radio_transcribe.setChecked(True)
        
        self.radio_transcribe.setToolTip(CONFIG["mode_radio_transcribe_tooltip"])
        self.radio_translate.setToolTip(CONFIG["mode_radio_translate_tooltip"])
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_transcribe)
        self.mode_group.addButton(self.radio_translate)
        
        self.radio_transcribe.toggled.connect(self._on_mode_changed)
        
        mode_layout.addWidget(self.radio_transcribe)
        mode_layout.addWidget(self.radio_translate)
        mode_layout.addStretch()
        
        main_layout.addLayout(mode_layout)
        

        
        # RMS Calibration
        rms_layout = QHBoxLayout()
        rms_label = QLabel(CONFIG["rms_noise_calibration"])
        rms_label.setToolTip(CONFIG["rms_noise_calibration_tooltip"])
        rms_layout.addWidget(rms_label)

        self.rms_spinbox = QDoubleSpinBox()
        self.rms_spinbox.setRange(0.0, 1.0)
        self.rms_spinbox.setSingleStep(0.01)  # Incremento de 0.01
        self.rms_spinbox.setDecimals(3)  # 2 casas decimais
        self.rms_spinbox.setValue(0.0)  # Valor inicial
        self.rms_spinbox.valueChanged.connect(self._on_rms_spinbox_changed) 
        self.rms_spinbox.setToolTip(CONFIG["rms_noise_calibration_tooltip"])
        rms_layout.addWidget(self.rms_spinbox)

        
        self.btn_calibrate = QPushButton(CONFIG["btn_calibrate"])
        self.btn_calibrate.setIcon(QIcon.fromTheme("audio-volume-medium"))
        self.btn_calibrate.setToolTip(CONFIG["btn_calibrate_tooltip"])
        self.btn_calibrate.clicked.connect(self.calibrate_noise)
        rms_layout.addWidget(self.btn_calibrate)

        #rms_layout.addStretch()

        main_layout.addLayout(rms_layout)
        
        
        # Definir fonte e tamanho
        font = QFont()
        font.setPointSize(12)  # ← Tamanho desejado (12, 14, 16, etc.)

        
        # ListView
        self.list_model = QStandardItemModel()
        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        self.list_view.setFont(font)

        # Adicionar delegate para quebra de linha
        self.list_view.setItemDelegate(WordWrapDelegate())

        # Habilitar word wrap
        self.list_view.setWordWrap(True)
        self.list_view.setResizeMode(QListView.Adjust)

        main_layout.addWidget(self.list_view)
        
        
        # Font Size Control
        font_layout = QHBoxLayout()
        font_label = QLabel(CONFIG["font_label"])
        font_label.setToolTip(CONFIG["font_label_tooltip"])
        font_layout.addWidget(font_label)

        self._on_font_size_changed(12)
        
        self.font_spinbox = QSpinBox()
        self.font_spinbox.setRange(8, 24)  # Tamanho mínimo 8, máximo 24
        self.font_spinbox.setValue(12)     # Valor inicial (ajuste conforme preferir)
        self.font_spinbox.setSuffix(" pt")  # Adiciona "pt" no final
        self.font_spinbox.valueChanged.connect(self._on_font_size_changed)

        font_layout.addWidget(self.font_spinbox)
        font_layout.addStretch()

        main_layout.addLayout(font_layout)
        
    def _on_font_size_changed(self, size: int):
        """Atualiza o tamanho da fonte do list view"""
        font = QFont()
        font.setPointSize(size)
        self.list_view.setFont(font)
    
    def _on_rms_spinbox_changed(self, value: float):
        """Atualiza o VAD quando o spinbox é modificado manualmente"""
        self.vad.rms_calibrated = value
    
    def _setup_worker(self):
        self.worker = AudioProcessorWorker(self.queue, CONFIG_GPT)
        self.worker.resultReady.connect(self.on_result_ready)
        self.worker.errorOccurred.connect(self.on_error)
    
    def _on_mode_changed(self):
        if self.radio_transcribe.isChecked():
            self.current_mode = "transcribe"
        else:
            self.current_mode = "translate"
    
    def get_current_mode(self) -> str:
        return self.current_mode
    
    def start_capture(self):
        if self.is_capturing:
            return
        
        # Criar segmenter
        self.segmenter = SpeechSegmenter(
            vad=self.vad,
            queue=self.queue,
            get_mode_callable=self.get_current_mode,
            sample_rate=SAMPLE_RATE,
            temp_dir=self.temp_dir,
            min_speech_duration = 0.5,
            silence_timeout = 0.5
        )
        
        # Criar capture - usa device_name apropriado (output ou input)
        self.capture = SystemAudioCapture(
            sample_rate=SAMPLE_RATE,
            frame_duration=0.03, # segundos
            callback=self._audio_callback,
            sink_name=self.device_name  # ← agora usa device_name genérico
        )
               
        # Iniciar worker
        self.worker.start()
        
        # Iniciar captura
        self.capture.start()
        
        self.is_capturing = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_calibrate.setEnabled(False)
    
    def stop_capture(self):
        if not self.is_capturing:
            return
        
        # Parar captura
        if self.capture:
            self.capture.stop()
        
        # Finalizar segmento ativo
        if self.segmenter:
            self.segmenter.stop()
        
        self.is_capturing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_calibrate.setEnabled(True)
    
    def calibrate_noise(self):
        if self.is_capturing or self.is_calibrating:
            return
        
        self.is_calibrating = True
        self.calibration_frames = []
        self.btn_calibrate.setEnabled(False)
        self.btn_start.setEnabled(False)
        
        # Criar capture temporário para calibração - usa device_name apropriado
        self.capture = SystemAudioCapture(
            sample_rate=SAMPLE_RATE,
            frame_duration=0.03,
            callback=self._calibration_callback,
            sink_name=self.device_name  # ← agora usa device_name genérico
        )
        
        self.capture.start()
    
    def _update_rms_spinbox(self, value: float):
        """Atualiza o spinbox com o valor calibrado (thread-safe)"""
        self.rms_spinbox.blockSignals(True)  # ← Bloquear sinais
        self.rms_spinbox.setValue(value)
        self.rms_spinbox.blockSignals(False)  # ← Desbloquear sinais
    
    def _calibration_callback(self, frame: np.ndarray):
        self.calibration_frames.append(frame)
        
        # ~2 segundos a 30ms por frame = ~67 frames
        if len(self.calibration_frames) >= 67:
            self.capture.stop()
            self.vad.calibrate(self.calibration_frames)
            
            # Emitir sinal em vez de chamar setValue diretamente
            if self.vad.rms_calibrated is not None:
                self.calibrationComplete.emit(self.vad.rms_calibrated)  # ← Usar sinal
            
            self.calibration_frames = []
            self.is_calibrating = False
            self.btn_calibrate.setEnabled(True)
            self.btn_start.setEnabled(True)
    
    def _audio_callback(self, frame: np.ndarray):
        if self.is_capturing and self.segmenter:
            self.segmenter.process_frame(frame)
    
    def on_result_ready(self, text: str, timestamp: datetime):
        time_str = timestamp.strftime("%H:%M:%S")
        item_text = f"[{time_str}] {text}"
        
        item = QStandardItem(item_text)
        self.list_model.appendRow(item)
        
        # Scroll para o último item
        last_index = self.list_model.index(self.list_model.rowCount() - 1, 0)
        self.list_view.scrollTo(last_index)
    
    def on_error(self, message: str):
        error_item = QStandardItem(f"[ERRO] {message}")
        self.list_model.appendRow(error_item)
    
    def close_application(self):
        self.stop_capture()
        
        if self.worker:
            self.worker.stop()
        
        self.applicationClosing.emit()
    
    def closeEvent(self, event):
        self.close_application()
        event.accept()
