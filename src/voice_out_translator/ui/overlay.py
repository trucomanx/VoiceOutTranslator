#!/usr/bin/python3

"""
subtitle_overlay.py
Widget reutilizável para mostrar texto overlay transparente na tela.
Funciona como legendas flutuantes sobre qualquer aplicação.

COMO USAR:
    # Criar overlay
    overlay = SubtitleOverlay(position="bottom", font_size=24)
    
    # Mostrar texto
    overlay.show_text("Minha legenda aqui")
    
    # Esconder temporariamente (pode mostrar de novo depois)
    overlay.hide()
    
    # Mostrar de novo
    overlay.show()
    
    # Fechar permanentemente (precisa criar novo objeto depois)
    overlay.close()
    
    # Limpar texto mas manter visível
    overlay.clear_text()
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from typing import Optional


class SubtitleOverlay(QWidget):
    """
    Widget de overlay transparente para mostrar texto na tela.
    
    Características:
    - Sempre no topo de todas as janelas
    - Fundo transparente/semi-transparente customizável
    - Posição configurável (top, bottom, center, custom)
    - Auto-hide após timeout opcional
    - Estilos customizáveis (fonte, cores, tamanho)
    
    MÉTODOS PRINCIPAIS:
        show_text(text, duration_ms=None) - Mostra texto no overlay
        clear_text() - Limpa o texto (sem esconder o overlay)
        hide() - Esconde o overlay (herdado de QWidget, pode mostrar de novo)
        show() - Mostra o overlay (herdado de QWidget)
        close() - Fecha permanentemente (herdado de QWidget)
        update_style(...) - Atualiza cores/fontes dinamicamente
    
    EXEMPLO DE USO:
        overlay = SubtitleOverlay(position="bottom")
        overlay.show_text("Olá!")  # Mostra
        overlay.hide()              # Esconde (pode voltar)
        overlay.show()              # Volta a aparecer
        overlay.close()             # Fecha permanentemente
    """
    
    def __init__(
        self,
        position: str = "bottom",  # "top", "bottom", "center", "custom"
        font_size: int = 24,
        font_color: str = "white",
        background_color: str = "rgba(0, 0, 0, 180)",
        padding: int = 10,
        border_radius: int = 5,
        auto_hide_ms: Optional[int] = None,  # None = não esconde automaticamente
        screen_width_percent: float = 0.93,  # 1.0 = largura total, 0.8 = 80%
        height: int = 100,  # <<< AGORA ALTURA É PARÂMETRO GLOBAL
        custom_x: Optional[int] = None,
        custom_y: Optional[int] = None,
    ):
        super().__init__()

        self.position = position
        self.font_size = font_size
        self.font_color = font_color
        self.background_color = background_color
        self.padding = padding
        self.border_radius = border_radius
        self.auto_hide_ms = auto_hide_ms
        self.screen_width_percent = screen_width_percent
        self.height_value = height
        self.custom_x = custom_x
        self.custom_y = custom_y
        
        # Timer para auto-hide
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)

        self._setup_ui()

    # =============================================================

    def _setup_ui(self):
        """Configura a interface do overlay"""
        # Janela sem bordas, sempre no topo, transparente
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.Tool |  # Não aparece na barra de tarefas
            Qt.WindowTransparentForInput  # Permite cliques passarem através (opcional)
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para o texto
        self.subtitle_label = QLabel("")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        
        # Configurar fonte
        font = QFont()
        font.setPointSize(self.font_size)
        font.setBold(True)
        self.subtitle_label.setFont(font)
        
        # Aplicar estilo
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.background_color};
                color: {self.font_color};
                padding: {self.padding}px;
                border-radius: {self.border_radius}px;
            }}
        """)
        
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)
        
        # Posicionar na tela
        self._update_position()

    # =============================================================

    def _update_position(self):
        """Atualiza a posição da janela na tela"""
        screen = QApplication.desktop().screenGeometry()

        width = int(screen.width() * self.screen_width_percent)
        height = self.height_value

        # ---------------- POSICIONAMENTO ----------------

        if self.position == "custom":
            if self.custom_x is None or self.custom_y is None:
                raise ValueError("Para position='custom', custom_x e custom_y devem ser definidos.")

            x = self.custom_x
            y = self.custom_y

        elif self.position == "top":
            x = (screen.width() - width) // 2
            y = 50

        elif self.position == "center":
            x = (screen.width() - width) // 2
            y = (screen.height() - height) // 2

        elif self.position == "bottom":
            x = (screen.width() - width) // 2
            y = screen.height() - height - 50

        else:
            raise ValueError("position deve ser: top, bottom, center ou custom")

        self.setGeometry(x, y, width, height)

    # =============================================================

    def show_text(self, text: str, duration_ms: Optional[int] = None):
        """
        Mostra texto no overlay.
        
        Args:
            text: Texto a ser exibido
            duration_ms: Tempo em ms para esconder automaticamente (None = usa configuração padrão)
        
        Exemplo:
            overlay.show_text("Olá Mundo!")
            overlay.show_text("Mensagem temporária", duration_ms=3000)  # Esconde após 3s
        """
        self.subtitle_label.setText(text.strip())
        self._update_position()  # reposiciona caso altura tenha mudado
        self.show()  # Mostra o widget (herdado de QWidget)
        
        # Configurar auto-hide se aplicável
        hide_duration = duration_ms if duration_ms is not None else self.auto_hide_ms
        if hide_duration:
            self.hide_timer.start(hide_duration)

    # =============================================================

    def clear_text(self):
        """
        Limpa o texto do overlay (mas mantém o overlay visível).
        
        Para esconder o overlay completamente, use: overlay.hide()
        Para fechar permanentemente, use: overlay.close()
        
        Exemplo:
            overlay.clear_text()  # Limpa texto mas overlay continua visível
            overlay.hide()        # Esconde completamente (pode mostrar de novo)
            overlay.close()       # Fecha permanentemente
        """
        self.subtitle_label.setText("")

    # =============================================================

    def update_style(
        self,
        font_size: Optional[int] = None,
        font_color: Optional[str] = None,
        background_color: Optional[str] = None
    ):
        """
        Atualiza o estilo do overlay dinamicamente.
        
        Args:
            font_size: Novo tamanho da fonte em pontos
            font_color: Nova cor do texto (ex: "white", "#FFFFFF", "rgb(255,255,255)")
            background_color: Nova cor de fundo (ex: "rgba(0, 0, 0, 180)")
        
        Exemplo:
            overlay.update_style(font_size=32, font_color="red")
        """
        if font_size:
            self.font_size = font_size
            font = self.subtitle_label.font()
            font.setPointSize(font_size)
            self.subtitle_label.setFont(font)
        
        if font_color:
            self.font_color = font_color
        
        if background_color:
            self.background_color = background_color
        
        # Reaplicar stylesheet
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.background_color};
                color: {self.font_color};
                padding: {self.padding}px;
                border-radius: {self.border_radius}px;
            }}
        """)

    # =============================================================

    def get_font_size(self) -> int:
        """
        Retorna o tamanho atual da fonte.
        
        Returns:
            int: Tamanho da fonte em pontos
        
        Exemplo:
            tamanho_atual = overlay.get_font_size()
            print(f"Fonte atual: {tamanho_atual}")
        """
        return self.font_size
    
    # =========================================================================
    # MÉTODOS HERDADOS DE QWidget (documentados para referência)
    # =========================================================================
    # 
    # self.show() - Mostra o overlay (pode chamar após hide())
    # self.hide() - Esconde temporariamente (pode mostrar de novo)
    # self.close() - Fecha permanentemente (precisa criar novo objeto)
    # self.isVisible() - Retorna True se está visível
    #
    # Exemplo de uso em botões:
    #   btn_hide.clicked.connect(overlay.hide)
    #   btn_show.clicked.connect(overlay.show)
    #   btn_close.clicked.connect(overlay.close)
    # =========================================================================
    
    def closeEvent(self, event):
        """
        Sobrescreve closeEvent para limpar recursos ao fechar.
        Chamado automaticamente quando close() é invocado.
        """
        if self.hide_timer.isActive():
            self.hide_timer.stop()
        event.accept()


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    import sys
    import signal
    
    # Permitir Ctrl+C fechar o programa
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    # Exemplo 1: Legendas na parte inferior (estilo Netflix)
    subtitle_bottom = SubtitleOverlay(
        position="bottom",
        font_size=28,
        font_color="yellow",
        background_color="rgba(0, 0, 0, 75)",
        auto_hide_ms=10000  # Esconde após 10 segundos
    )
    subtitle_bottom.show_text("Legendas na parte inferior da tela!")
    
    QTimer.singleShot(3000, lambda: subtitle_bottom.show_text("Notificação importante!"))
    
    # Exemplo 2: Notificação no topo
    notification_top = SubtitleOverlay(
        position="top",
        font_size=20,
        font_color="white",
        background_color="rgba(50, 150, 250, 220)",
        screen_width_percent=0.5,  # 50% da largura
        auto_hide_ms=5000
    )
    
    # Mostrar após 1 segundo
    QTimer.singleShot(1000, lambda: notification_top.show_text("Notificação importante!"))
    
    # Exemplo 3: Mensagem central permanente
    message_center = SubtitleOverlay(
        position="center",
        font_size=32,
        font_color="lime",
        background_color="rgba(0, 0, 0, 150)"
    )
    
    QTimer.singleShot(2000, lambda: message_center.show_text("Mensagem central"))
    
    # Exemplo 4: Demonstração de hide/show/close
    demo = SubtitleOverlay(position="bottom", font_size=20)
    demo.show_text("Vou esconder em 4s...")
    QTimer.singleShot(4000, demo.hide)  # Esconde
    QTimer.singleShot(6000, demo.show)  # Mostra de novo
    QTimer.singleShot(7000, demo.close) # Fecha permanentemente
    
    # Fechar tudo após 12 segundos (para teste)
    QTimer.singleShot(12000, app.quit)
    
    sys.exit(app.exec_())

