import os
import queue
from datetime import datetime
from typing import Callable

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QListView,
    QLabel,
    QDoubleSpinBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from voice_out_translator.audio.vad import RMSVoiceActivityDetector
from voice_out_translator.audio.capture import SystemAudioCapture
from voice_out_translator.audio.segmenter import SpeechSegmenter
from voice_out_translator.workers.processor import AudioProcessorWorker
from voice_out_translator.utils.virtual_out import setup_virtual_output

import voice_out_translator.about as about
import voice_out_translator.modules.configure as configure

CONFIG_GPT_PATH = os.path.join( os.path.expanduser("~"),
                                ".config", 
                                about.__package__, 
                                "config.gpt.json" )

CONFIG_GPT=configure.load_config(CONFIG_GPT_PATH)

SAMPLE_RATE = 8000

class MainWindow(QMainWindow):
    applicationClosing = pyqtSignal()
    calibrationComplete = pyqtSignal(float)  # ← Novo sinal

    def __init__(self, temp_dir: str, virtual_monitor_name: str):
        super().__init__()
        self.temp_dir = temp_dir
        self.virtual_monitor_name = virtual_monitor_name
        setup_virtual_output( virtual_sink = virtual_monitor_name)
        
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
        
        self._setup_ui()
        self._setup_worker()
        
        self.calibrationComplete.connect(self._update_rms_spinbox)  
        
    
    def _setup_ui(self):
        self.setWindowTitle("Captura de Áudio")
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Botões de controle
        button_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Iniciar Captura")
        self.btn_start.clicked.connect(self.start_capture)
        button_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Parar Captura")
        self.btn_stop.clicked.connect(self.stop_capture)
        self.btn_stop.setEnabled(False)
        button_layout.addWidget(self.btn_stop)

        
        main_layout.addLayout(button_layout)
        
        # Selector de modo
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Modo:")
        mode_layout.addWidget(mode_label)
        
        self.radio_transcribe = QRadioButton("Transcrever")
        self.radio_translate = QRadioButton("Traduzir")
        self.radio_transcribe.setChecked(True)
        
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
        rms_label = QLabel("RMS noise calibration:")
        rms_layout.addWidget(rms_label)

        self.rms_spinbox = QDoubleSpinBox()
        self.rms_spinbox.setRange(0.0, 1.0)
        self.rms_spinbox.setSingleStep(0.01)  # Incremento de 0.01
        self.rms_spinbox.setDecimals(3)  # 2 casas decimais
        self.rms_spinbox.setValue(0.0)  # Valor inicial
        self.rms_spinbox.valueChanged.connect(self._on_rms_spinbox_changed) 
        rms_layout.addWidget(self.rms_spinbox)

        
        self.btn_calibrate = QPushButton("Calibrar Ruído")
        self.btn_calibrate.clicked.connect(self.calibrate_noise)
        rms_layout.addWidget(self.btn_calibrate)

        #rms_layout.addStretch()

        main_layout.addLayout(rms_layout)
        
        
        # ListView
        self.list_model = QStandardItemModel()
        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        
        main_layout.addWidget(self.list_view)
    
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
        
        # Criar capture
        self.capture = SystemAudioCapture(
            sample_rate=SAMPLE_RATE,
            frame_duration=0.03, # segundos
            callback=self._audio_callback,
            sink_name=self.virtual_monitor_name
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
        
        # Criar capture temporário para calibração
        self.capture = SystemAudioCapture(
            sample_rate=SAMPLE_RATE,
            frame_duration=0.03,
            callback=self._calibration_callback,
            sink_name=self.virtual_monitor_name
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
