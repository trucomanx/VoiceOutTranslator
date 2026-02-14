import numpy as np
import queue
import datetime
from typing import Callable
from voice_out_translator.audio.vad import RMSVoiceActivityDetector
from voice_out_translator.utils.temp_audio import create_temp_mp3


class SpeechSegmenter:
    
    
    def __init__(
        self,
        vad: RMSVoiceActivityDetector,
        queue: queue.Queue,
        get_mode_callable: Callable[[], str],
        sample_rate: int,
        temp_dir: str,
        min_speech_duration: float,
        silence_timeout: float
    ):
        self.min_speech_duration = min_speech_duration
        self.silence_timeout = silence_timeout
        self.vad = vad
        self.queue = queue
        self.get_mode_callable = get_mode_callable
        self.sample_rate = sample_rate
        self.temp_dir = temp_dir
        
        self.active_segment = None
        self.segment_frames = []
        self.segment_start_time = None
        self.silence_duration = 0.0
        self.frame_duration = None
    
    def process_frame(self, frame: np.ndarray) -> None:
        try:
            if self.frame_duration is None:
                self.frame_duration = len(frame) / self.sample_rate

            is_speech = self.vad.is_speech(frame)
            #print("is_speech:", is_speech,self.vad.rms(frame))
            
            if is_speech:
                if self.segment_start_time is None:
                    self.segment_start_time = datetime.datetime.now()
                
                self.segment_frames.append(frame.copy())
                self.silence_duration = 0.0
                self.active_segment = True
            else:
                if self.active_segment:
                    self.segment_frames.append(frame.copy())
                    self.silence_duration += self.frame_duration
                    
                    if self.silence_duration >= self.silence_timeout:
                        print("finalize_segment")
                        self._finalize_segment()
        except Exception:
            pass
    
    def stop(self) -> None:
        if self.active_segment and len(self.segment_frames) > 0:
            self._finalize_segment()
    
    def _finalize_segment(self) -> None:
        if len(self.segment_frames) == 0:
            self._reset_segment()
            return
        
        segment_duration = len(self.segment_frames) * self.frame_duration
        
        if segment_duration < self.min_speech_duration:
            self._reset_segment()
            return
        
        try:
            audio_data = np.concatenate(self.segment_frames)
            audio_int16 = np.int16(audio_data * 32767)
                        
            audio_path =  create_temp_mp3(audio_int16.tobytes(),
                                        self.sample_rate,
                                        1,
                                        2,
                                        prefix = "chunk",
                                        temp_dir = self.temp_dir ) 
            
            
            mode = self.get_mode_callable()
            
            metadata = {
                "path": audio_path,
                "timestamp": self.segment_start_time,
                "mode": mode
            }
            
            self.queue.put(metadata)
        except Exception:
            pass
        finally:
            self._reset_segment()
    
    def _reset_segment(self) -> None:
        self.active_segment = None
        self.segment_frames = []
        self.segment_start_time = None
        self.silence_duration = 0.0
