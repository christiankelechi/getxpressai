import sys
import cv2
import numpy as np
import mediapipe as mp
import os
import requests
import io
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QColorDialog, QVBoxLayout,
    QHBoxLayout, QFrame, QSlider, QComboBox, QCheckBox, QFileDialog,
    QProgressBar, QGroupBox, QGridLayout, QSpacerItem, QSizePolicy,
    QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QTabWidget,
    QScrollArea, QSplitter, QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QUrl
import mss
import threading
import pyaudio
import wave
import subprocess
from PIL import Image
import json

class AudioRecorder(QThread):
    """Thread for recording audio from microphone and speakers"""
    def __init__(self, output_path, sample_rate=44100, channels=2):
        super().__init__()
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        
    def run(self):
        p = pyaudio.PyAudio()
        
        # Open stream for microphone input
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        while self.recording:
            data = stream.read(1024)
            self.audio_data.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save audio to file
        with wave.open(self.output_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.audio_data))

class WallpaperSearcher(QThread):
    """Thread for searching and downloading wallpapers"""
    wallpaper_found = pyqtSignal(str, str)  # url, filename
    search_complete = pyqtSignal()
    
    def __init__(self, search_term):
        super().__init__()
        self.search_term = search_term
        
    def run(self):
        try:
            # Search for wallpapers using Unsplash API (free)
            url = f"https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": "Client-ID YOUR_UNSPLASH_ACCESS_KEY"  # You'll need to get this
            }
            params = {
                "query": self.search_term,
                "per_page": 20,
                "orientation": "landscape"
            }
            
            # For demo purposes, we'll use some sample URLs
            sample_wallpapers = [
                ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop", "mountain_landscape.jpg"),
                ("https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=1920&h=1080&fit=crop", "ocean_waves.jpg"),
                ("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920&h=1080&fit=crop", "forest_path.jpg"),
                ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop", "city_skyline.jpg"),
                ("https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=1920&h=1080&fit=crop", "desert_sunset.jpg"),
            ]
            
            for url, filename in sample_wallpapers:
                if self.search_term.lower() in filename.lower() or not self.search_term:
                    self.wallpaper_found.emit(url, filename)
                    
        except Exception as e:
            print(f"Wallpaper search error: {e}")
        finally:
            self.search_complete.emit()

class VideoRecorder(QThread):
    """Enhanced video recorder with audio support"""
    def __init__(self, output_path, fps=30, include_audio=True):
        super().__init__()
        self.output_path = output_path
        self.fps = fps
        self.frames = []
        self.recording = False
        self.include_audio = include_audio
        
    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (640, 480))
        
        while self.recording:
            if self.frames:
                frame = self.frames.pop(0)
                out.write(frame)
            self.msleep(33)  # ~30 FPS
        
        out.release()
    
    def add_frame(self, frame):
        if self.recording:
            self.frames.append(frame.copy())

class AILiveBackground(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Background Exporter & Virtual Camera")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(self.get_modern_style())
        
        # Initialize variables
        self.background_image = None
        self.background_color = (255, 255, 255)
        self.blend_strength = 0.5
        self.edge_feather = 15
        self.is_recording = False
        self.recorder = None
        self.audio_recorder = None
        self.record_webcam = True
        self.record_desktop = False
        self.record_audio = True
        self.output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "AI_Exports")
        self.backgrounds_dir = os.path.join(self.output_dir, "backgrounds")
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.backgrounds_dir, exist_ok=True)
        
        # Background management
        self.available_backgrounds = []
        self.current_background_index = 0
        
        # Mediapipe setup
        self.segment = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
        self.cap = cv2.VideoCapture(0)
        
        # Desktop capture setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
        
        # Load default backgrounds
        self.load_default_backgrounds()
        
        self.setup_ui()
        self.setup_timers()
    
    def load_default_backgrounds(self):
        """Load default background images"""
        default_backgrounds = [
            ("Office", "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&h=1080&fit=crop"),
            ("Nature", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920&h=1080&fit=crop"),
            ("Ocean", "https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=1920&h=1080&fit=crop"),
            ("City", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop"),
            ("Abstract", "https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop"),
        ]
        
        for name, url in default_backgrounds:
            self.available_backgrounds.append({
                'name': name,
                'url': url,
                'image': None,
                'local_path': None
            })

    def get_modern_style(self):
        return """
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #3a3a3a;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #2a2a2a;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #4fc3f7;
        }
        
        QPushButton {
            background-color: #4fc3f7;
            border: none;
            border-radius: 6px;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #29b6f6;
        }
        
        QPushButton:pressed {
            background-color: #0288d1;
        }
        
        QPushButton:disabled {
            background-color: #666666;
            color: #999999;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #3a3a3a;
            height: 8px;
            background: #2a2a2a;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #4fc3f7;
            border: 1px solid #4fc3f7;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QComboBox {
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 5px;
            color: white;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #4fc3f7;
            margin-right: 5px;
        }
        
        QCheckBox {
            color: white;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 2px solid #3a3a3a;
            background-color: #2a2a2a;
        }
        
        QCheckBox::indicator:checked {
            background-color: #4fc3f7;
            border-color: #4fc3f7;
        }
        
        QLabel {
            color: white;
        }
        
        QFrame {
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            background-color: #2a2a2a;
        }
        """
    
    def setup_ui(self):
        """Setup the modern UI layout with tabs"""
        main_layout = QHBoxLayout()
        
        # Left panel - Video display
        video_frame = QFrame()
        video_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        video_layout = QVBoxLayout(video_frame)
        
        self.video_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #4fc3f7; border-radius: 8px;")
        video_layout.addWidget(self.video_label)
        
        # Recording status
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4fc3f7; font-weight: bold; font-size: 16px;")
        video_layout.addWidget(self.status_label)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_image_btn = QPushButton("📸 Export Image")
        self.export_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.export_image_btn.clicked.connect(self.export_image)
        export_layout.addWidget(self.export_image_btn)
        
        self.export_video_btn = QPushButton("🎬 Export Video")
        self.export_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.export_video_btn.clicked.connect(self.export_video)
        export_layout.addWidget(self.export_video_btn)
        
        video_layout.addLayout(export_layout)
        main_layout.addWidget(video_frame, 2)
        
        # Right panel - Tabbed controls
        self.tab_widget = QTabWidget()
        self.tab_widget.setMaximumWidth(400)
        
        # Background Tab
        self.bg_tab = self.create_background_tab()
        self.tab_widget.addTab(self.bg_tab, "🎨 Backgrounds")
        
        # Recording Tab
        self.record_tab = self.create_recording_tab()
        self.tab_widget.addTab(self.record_tab, "🎥 Recording")
        
        # Wallpaper Tab
        self.wallpaper_tab = self.create_wallpaper_tab()
        self.tab_widget.addTab(self.wallpaper_tab, "🌐 Wallpapers")
        
        main_layout.addWidget(self.tab_widget, 1)
        
        self.setLayout(main_layout)
    
    def create_background_tab(self):
        """Create the background management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Background selection
        bg_group = QGroupBox("Background Selection")
        bg_layout = QVBoxLayout(bg_group)
        
        self.bg_list = QListWidget()
        self.bg_list.setMaximumHeight(150)
        self.populate_background_list()
        self.bg_list.itemClicked.connect(self.select_background)
        bg_layout.addWidget(self.bg_list)
        
        # Background controls
        bg_controls_layout = QHBoxLayout()
        self.prev_bg_btn = QPushButton("◀ Previous")
        self.prev_bg_btn.clicked.connect(self.previous_background)
        bg_controls_layout.addWidget(self.prev_bg_btn)
        
        self.next_bg_btn = QPushButton("Next ▶")
        self.next_bg_btn.clicked.connect(self.next_background)
        bg_controls_layout.addWidget(self.next_bg_btn)
        
        bg_layout.addLayout(bg_controls_layout)
        
        # Custom background
        self.custom_bg_btn = QPushButton("📁 Load Custom Background")
        self.custom_bg_btn.clicked.connect(self.load_custom_background)
        bg_layout.addWidget(self.custom_bg_btn)
        
        layout.addWidget(bg_group)
        
        # Blend settings
        blend_group = QGroupBox("Blend Settings")
        blend_layout = QGridLayout(blend_group)
        
        blend_layout.addWidget(QLabel("Blend Strength:"), 0, 0)
        self.blend_slider = QSlider(Qt.Orientation.Horizontal)
        self.blend_slider.setRange(0, 100)
        self.blend_slider.setValue(50)
        self.blend_slider.valueChanged.connect(self.update_blend_strength)
        blend_layout.addWidget(self.blend_slider, 0, 1)
        
        blend_layout.addWidget(QLabel("Edge Feather:"), 1, 0)
        self.feather_slider = QSlider(Qt.Orientation.Horizontal)
        self.feather_slider.setRange(5, 50)
        self.feather_slider.setValue(15)
        self.feather_slider.valueChanged.connect(self.update_edge_feather)
        blend_layout.addWidget(self.feather_slider, 1, 1)
        
        layout.addWidget(blend_group)
        
        # Solid color option
        self.color_btn = QPushButton("🎨 Solid Color Background")
        self.color_btn.clicked.connect(self.pick_color)
        layout.addWidget(self.color_btn)
        
        return tab
    
    def create_recording_tab(self):
        """Create the recording settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Recording options
        record_group = QGroupBox("Recording Options")
        record_layout = QVBoxLayout(record_group)
        
        self.webcam_check = QCheckBox("Record Webcam")
        self.webcam_check.setChecked(True)
        self.webcam_check.stateChanged.connect(self.toggle_webcam_recording)
        record_layout.addWidget(self.webcam_check)
        
        self.desktop_check = QCheckBox("Record Desktop Screen")
        self.desktop_check.stateChanged.connect(self.toggle_desktop_recording)
        record_layout.addWidget(self.desktop_check)
        
        self.audio_check = QCheckBox("Record Audio (Microphone)")
        self.audio_check.setChecked(True)
        self.audio_check.stateChanged.connect(self.toggle_audio_recording)
        record_layout.addWidget(self.audio_check)
        
        layout.addWidget(record_group)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        self.output_btn = QPushButton("📁 Choose Output Folder")
        self.output_btn.clicked.connect(self.choose_output_folder)
        output_layout.addWidget(self.output_btn)
        
        layout.addWidget(output_group)
        
        # Recording controls
        self.record_btn = QPushButton("🔴 Start Recording")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                font-size: 16px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)
        
        return tab
    
    def create_wallpaper_tab(self):
        """Create the wallpaper search tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search section
        search_group = QGroupBox("Wallpaper Search")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for wallpapers (e.g., nature, city, abstract)")
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍 Search Wallpapers")
        self.search_btn.clicked.connect(self.search_wallpapers)
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_group)
        
        # Results section
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.setMaximumHeight(200)
        self.wallpaper_list.itemClicked.connect(self.download_wallpaper)
        results_layout.addWidget(self.wallpaper_list)
        
        layout.addWidget(results_group)
        
        # URL import
        url_group = QGroupBox("Import from URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste wallpaper URL here")
        url_layout.addWidget(self.url_input)
        
        self.import_url_btn = QPushButton("📥 Import from URL")
        self.import_url_btn.clicked.connect(self.import_from_url)
        url_layout.addWidget(self.import_url_btn)
        
        layout.addWidget(url_group)
        
        return tab
    
    def setup_timers(self):
        """Setup timers for video updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS
    
    def populate_background_list(self):
        """Populate the background list widget"""
        self.bg_list.clear()
        for i, bg in enumerate(self.available_backgrounds):
            item = QListWidgetItem(f"{bg['name']} {'(Loaded)' if bg['image'] is not None else '(Not Loaded)'}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.bg_list.addItem(item)
    
    def select_background(self, item):
        """Select a background from the list"""
        index = item.data(Qt.ItemDataRole.UserRole)
        self.current_background_index = index
        self.load_background_image(index)
    
    def previous_background(self):
        """Go to previous background"""
        if self.current_background_index > 0:
            self.current_background_index -= 1
        else:
            self.current_background_index = len(self.available_backgrounds) - 1
        self.load_background_image(self.current_background_index)
        self.bg_list.setCurrentRow(self.current_background_index)
    
    def next_background(self):
        """Go to next background"""
        if self.current_background_index < len(self.available_backgrounds) - 1:
            self.current_background_index += 1
        else:
            self.current_background_index = 0
        self.load_background_image(self.current_background_index)
        self.bg_list.setCurrentRow(self.current_background_index)
    
    def load_background_image(self, index):
        """Load background image from URL or local path"""
        if index >= len(self.available_backgrounds):
            return
            
        bg = self.available_backgrounds[index]
        
        if bg['image'] is not None:
            self.background_image = bg['image']
            return
        
        try:
            if bg['url']:
                # Download image from URL
                response = requests.get(bg['url'], timeout=10)
                if response.status_code == 200:
                    img_data = response.content
                    pil_image = Image.open(io.BytesIO(img_data))
                    # Convert PIL to OpenCV format
                    img_array = np.array(pil_image)
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                    
                    # Resize to standard size
                    img_array = cv2.resize(img_array, (640, 480))
                    
                    bg['image'] = img_array
                    self.background_image = img_array
                    
                    # Save locally
                    filename = f"{bg['name'].lower().replace(' ', '_')}.jpg"
                    local_path = os.path.join(self.backgrounds_dir, filename)
                    cv2.imwrite(local_path, cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
                    bg['local_path'] = local_path
                    
                    self.populate_background_list()
                    
        except Exception as e:
            print(f"Error loading background: {e}")
    
    def load_custom_background(self):
        """Load custom background from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                img_array = cv2.imread(file_path)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                img_array = cv2.resize(img_array, (640, 480))
                
                # Add to available backgrounds
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.available_backgrounds.append({
                    'name': f"Custom: {name}",
                    'url': None,
                    'image': img_array,
                    'local_path': file_path
                })
                
                self.background_image = img_array
                self.current_background_index = len(self.available_backgrounds) - 1
                self.populate_background_list()
                self.bg_list.setCurrentRow(self.current_background_index)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load image: {e}")
    
    def search_wallpapers(self):
        """Search for wallpapers online"""
        search_term = self.search_input.text().strip()
        if not search_term:
            search_term = "nature"
        
        self.wallpaper_list.clear()
        self.wallpaper_list.addItem("Searching...")
        
        self.searcher = WallpaperSearcher(search_term)
        self.searcher.wallpaper_found.connect(self.add_wallpaper_result)
        self.searcher.search_complete.connect(self.search_complete)
        self.searcher.start()
    
    def add_wallpaper_result(self, url, filename):
        """Add wallpaper result to the list"""
        item = QListWidgetItem(filename)
        item.setData(Qt.ItemDataRole.UserRole, url)
        self.wallpaper_list.addItem(item)
    
    def search_complete(self):
        """Called when wallpaper search is complete"""
        if self.wallpaper_list.count() == 1 and self.wallpaper_list.item(0).text() == "Searching...":
            self.wallpaper_list.clear()
            self.wallpaper_list.addItem("No wallpapers found")
    
    def download_wallpaper(self, item):
        """Download and add wallpaper to backgrounds"""
        if item.text() in ["Searching...", "No wallpapers found"]:
            return
            
        url = item.data(Qt.ItemDataRole.UserRole)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_data = response.content
                pil_image = Image.open(io.BytesIO(img_data))
                img_array = np.array(pil_image)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                img_array = cv2.resize(img_array, (640, 480))
                
                # Add to backgrounds
                name = os.path.splitext(item.text())[0]
                self.available_backgrounds.append({
                    'name': f"Downloaded: {name}",
                    'url': url,
                    'image': img_array,
                    'local_path': None
                })
                
                self.background_image = img_array
                self.current_background_index = len(self.available_backgrounds) - 1
                self.populate_background_list()
                self.bg_list.setCurrentRow(self.current_background_index)
                
                QMessageBox.information(self, "Success", f"Wallpaper '{name}' added to backgrounds!")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not download wallpaper: {e}")
    
    def import_from_url(self):
        """Import wallpaper from URL"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_data = response.content
                pil_image = Image.open(io.BytesIO(img_data))
                img_array = np.array(pil_image)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                img_array = cv2.resize(img_array, (640, 480))
                
                # Add to backgrounds
                name = f"URL Import {len(self.available_backgrounds) + 1}"
                self.available_backgrounds.append({
                    'name': name,
                    'url': url,
                    'image': img_array,
                    'local_path': None
                })
                
                self.background_image = img_array
                self.current_background_index = len(self.available_backgrounds) - 1
                self.populate_background_list()
                self.bg_list.setCurrentRow(self.current_background_index)
                
                QMessageBox.information(self, "Success", "Wallpaper imported successfully!")
                self.url_input.clear()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not import wallpaper: {e}")
    
    def export_image(self):
        """Export current frame as image"""
        if not hasattr(self, 'last_frame') or self.last_frame is None:
            QMessageBox.warning(self, "Error", "No frame to export")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_background_export_{timestamp}.png"
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            # Convert RGB to BGR for OpenCV
            export_frame = cv2.cvtColor(self.last_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, export_frame)
            QMessageBox.information(self, "Success", f"Image exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not export image: {e}")
    
    def export_video(self):
        """Export video with current settings"""
        if self.is_recording:
            QMessageBox.warning(self, "Error", "Please stop recording first")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_background_video_{timestamp}.mp4"
        file_path = os.path.join(self.output_dir, filename)
        
        # Start recording
        self.start_recording(file_path)
        QMessageBox.information(self, "Recording Started", "Video recording started. Click 'Stop Recording' when done.")
    
    def toggle_audio_recording(self, state):
        self.record_audio = state == Qt.CheckState.Checked.value

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = (
                color.red(),
                color.green(),
                color.blue()
            )
    
    def update_blend_strength(self, value):
        self.blend_strength = value / 100.0
    
    def update_edge_feather(self, value):
        self.edge_feather = value
    
    def toggle_webcam_recording(self, state):
        self.record_webcam = state == Qt.CheckState.Checked.value
    
    def toggle_desktop_recording(self, state):
        self.record_desktop = state == Qt.CheckState.Checked.value
    
    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self, output_path=None):
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, filename)
        
        self.recorder = VideoRecorder(output_path, include_audio=self.record_audio)
        self.recorder.start()
        self.recorder.recording = True
        
        # Start audio recording if enabled
        if self.record_audio:
            audio_filename = output_path.replace('.mp4', '_audio.wav')
            self.audio_recorder = AudioRecorder(audio_filename)
            self.audio_recorder.start()
            self.audio_recorder.recording = True
        
        self.is_recording = True
        self.record_btn.setText("⏹️ Stop Recording")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                font-size: 16px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.status_label.setText(f"Recording to: {os.path.basename(output_path)}")
    
    def stop_recording(self):
        if self.recorder:
            self.recorder.recording = False
            self.recorder.wait()
            self.recorder = None
        
        if self.audio_recorder:
            self.audio_recorder.recording = False
            self.audio_recorder.wait()
            self.audio_recorder = None
        
        self.is_recording = False
        self.record_btn.setText("🔴 Start Recording")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                font-size: 16px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.status_label.setText("Ready to record")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.segment.process(frame_rgb)
        mask = results.segmentation_mask

        # Enhanced blending for more realistic results
        output = self.apply_advanced_blending(frame_rgb, mask)
        
        # Store last frame for export
        self.last_frame = output.copy()
        
        # Record frame if recording is enabled
        if self.is_recording and self.recorder and self.record_webcam:
            self.recorder.add_frame(cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
        
        # Convert to QImage and display
        image = QImage(
            output.data,
            output.shape[1],
            output.shape[0],
            output.strides[0],
            QImage.Format.Format_RGB888
        )
        self.video_label.setPixmap(QPixmap.fromImage(image))
    
    def apply_advanced_blending(self, frame_rgb, mask):
        """Apply advanced blending techniques for more realistic background replacement"""
        
        # Create a more refined mask with better edge detection
        mask_refined = self.refine_mask(mask)
        
        # Apply multiple levels of blur for smooth transitions
        mask_blurred = cv2.GaussianBlur(mask_refined, (self.edge_feather, self.edge_feather), 0)
        
        # Create additional edge smoothing
        mask_smooth = cv2.bilateralFilter(mask_blurred, 9, 75, 75)
        
        # Expand dimensions for broadcasting
        mask_3d = np.expand_dims(mask_smooth, axis=-1)
        
        # Create background - use image if available, otherwise solid color
        if self.background_image is not None:
            bg = self.background_image.copy()
            # Resize background to match frame size
            bg = cv2.resize(bg, (frame_rgb.shape[1], frame_rgb.shape[0]))
        else:
            bg = np.full_like(frame_rgb, self.background_color, dtype=np.uint8)
        
        # Apply color correction to match lighting
        frame_corrected = self.apply_color_correction(frame_rgb, bg)
        
        # Advanced blending with multiple passes
        # First pass: basic blending
        blended = mask_3d * frame_corrected + (1 - mask_3d) * bg
        
        # Second pass: edge refinement
        edge_mask = self.create_edge_mask(mask_refined)
        edge_mask_3d = np.expand_dims(edge_mask, axis=-1)
        
        # Final blend with edge smoothing
        final_output = edge_mask_3d * blended + (1 - edge_mask_3d) * bg
        
        return final_output.astype(np.uint8)
    
    def refine_mask(self, mask):
        """Refine the segmentation mask for better edge quality"""
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
        
        # Apply threshold with hysteresis for better edge definition
        mask_binary = (mask_cleaned > 0.5).astype(np.uint8) * 255
        
        # Find contours and fill holes
        contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask_filled = np.zeros_like(mask_binary)
        cv2.fillPoly(mask_filled, contours, 255)
        
        return mask_filled.astype(np.float32) / 255.0
    
    def create_edge_mask(self, mask):
        """Create a smooth edge mask for better blending"""
        # Detect edges
        edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
        
        # Dilate edges for smoother transition
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Create smooth edge mask
        edge_mask = cv2.GaussianBlur(edges_dilated, (9, 9), 0)
        edge_mask = edge_mask.astype(np.float32) / 255.0
        
        # Combine with original mask
        return np.maximum(mask, edge_mask)
    
    def apply_color_correction(self, foreground, background):
        """Apply color correction to match foreground lighting with background"""
        # Convert to LAB color space for better color matching
        fg_lab = cv2.cvtColor(foreground, cv2.COLOR_RGB2LAB)
        bg_lab = cv2.cvtColor(background, cv2.COLOR_RGB2LAB)
        
        # Calculate mean values for color transfer
        fg_mean = np.mean(fg_lab, axis=(0, 1))
        bg_mean = np.mean(bg_lab, axis=(0, 1))
        
        # Apply color transfer (simplified version)
        fg_corrected = fg_lab.copy()
        fg_corrected[:, :, 1] = fg_corrected[:, :, 1] - fg_mean[1] + bg_mean[1]  # a channel
        fg_corrected[:, :, 2] = fg_corrected[:, :, 2] - fg_mean[2] + bg_mean[2]  # b channel
        
        # Convert back to RGB
        fg_corrected_rgb = cv2.cvtColor(fg_corrected, cv2.COLOR_LAB2RGB)
        
        # Blend original and corrected based on blend strength
        return (self.blend_strength * fg_corrected_rgb + 
                (1 - self.blend_strength) * foreground).astype(np.uint8)
    
    def capture_desktop(self):
        """Capture desktop screen"""
        try:
            screenshot = self.sct.grab(self.monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            return img
        except Exception as e:
            print(f"Desktop capture error: {e}")
            return None

    def closeEvent(self, event):
        """Release resources when window closes."""
        if self.is_recording:
            self.stop_recording()
        
        self.timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

# ------------------ Run App ------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use modern Fusion style
    
    window = AILiveBackground()
    window.show()
    
    sys.exit(app.exec())
