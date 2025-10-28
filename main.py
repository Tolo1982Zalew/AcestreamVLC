# main.py - KOMPLETNA WERSJA z auto-otwieraniem VLC
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard

from scraper import get_acestream_links
import requests
import threading
import subprocess
import platform
import os

# Import Windows registry (opcjonalnie)
if platform.system() == "Windows":
    try:
        import winreg
    except ImportError:
        winreg = None

# Android API (tylko na Androidzie)
ANDROID = False
try:
    from jnius import autoclass, cast

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    ANDROID = True
    print("[INFO] ✅ Android Mode")
except:
    print("[INFO] 💻 PC Mode")


class AcestreamApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.channels = []
        self.current_channel = None
        self.current_acestream_id = None
        self.player_choice = "VLC"
        self.acestream_ports = [6878, 6879, 8621]
        self.acestream_url = None
        print("[DEBUG] Aplikacja zainicjowana")

    def build(self):
        print("[DEBUG] Budowanie UI...")
        Window.clearcolor = (0.1, 0.1, 0.15, 1)

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=12)

        # Header
        header = Label(
            text='📺 ACESTREAM → VLC',
            size_hint_y=None,
            height=60,
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(header)

        # Status Acestream Engine
        self.engine_status = Label(
            text='🔍 Sprawdzanie Acestream Engine...',
            size_hint_y=None,
            height=30,
            font_size='12sp',
            color=(1, 0.8, 0, 1)
        )
        main_layout.add_widget(self.engine_status)

        # Status platformy + Wybór playera
        top_bar = BoxLayout(size_hint_y=None, height=40, spacing=10)

        platform_label = Label(
            text=f"{'📱 Android' if ANDROID else '💻 PC Test'}",
            size_hint_x=0.5,
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )

        self.player_spinner = Spinner(
            text='🎬 VLC (HTTP)',
            values=('🎬 VLC (HTTP)', '🔴 Acestream Engine', '🌐 Proxy Online', '📋 Kopiuj'),
            size_hint_x=0.5,
            background_color=(0.3, 0.3, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        self.player_spinner.bind(text=self.on_player_change)

        top_bar.add_widget(platform_label)
        top_bar.add_widget(self.player_spinner)
        main_layout.add_widget(top_bar)

        # Pole wyszukiwania
        search_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        self.search_input = TextInput(
            hint_text='Wpisz nazwę kanału...',
            multiline=False,
            size_hint_x=0.7,
            font_size='16sp',
            background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[15, 12]
        )
        self.search_input.bind(on_text_validate=self.search_channels)

        search_btn = Button(
            text='🔎 SZUKAJ',
            size_hint_x=0.3,
            font_size='14sp',
            background_color=(0.4, 0.3, 0.8, 1),
            bold=True
        )
        search_btn.bind(on_press=self.search_channels)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        main_layout.add_widget(search_layout)

        # Licznik kanałów
        self.counter_label = Label(
            text='Kanały: 0',
            size_hint_y=None,
            height=25,
            font_size='13sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        main_layout.add_widget(self.counter_label)

        # Lista kanałów (scrollable)
        scroll = ScrollView(size_hint=(1, 1))
        self.channel_layout = GridLayout(
            cols=1,
            spacing=8,
            size_hint_y=None,
            padding=[5, 5]
        )
        self.channel_layout.bind(minimum_height=self.channel_layout.setter('height'))
        scroll.add_widget(self.channel_layout)
        main_layout.add_widget(scroll)

        # Panel kontrolny
        control_panel = GridLayout(
            cols=3,
            size_hint_y=None,
            height=65,
            spacing=8
        )

        self.play_btn = Button(
            text='▶️ PLAY',
            font_size='16sp',
            background_color=(0.2, 0.8, 0.2, 1),
            bold=True,
            disabled=True
        )
        self.play_btn.bind(on_press=self.play_selected)

        self.copy_btn = Button(
            text='📋 COPY',
            font_size='16sp',
            background_color=(0.2, 0.5, 0.8, 1),
            bold=True,
            disabled=True
        )
        self.copy_btn.bind(on_press=self.copy_link)

        self.info_btn = Button(
            text='ℹ️ INFO',
            font_size='16sp',
            background_color=(0.6, 0.4, 0.8, 1),
            bold=True,
            disabled=True
        )
        self.info_btn.bind(on_press=self.show_channel_info)

        control_panel.add_widget(self.play_btn)
        control_panel.add_widget(self.copy_btn)
        control_panel.add_widget(self.info_btn)
        main_layout.add_widget(control_panel)

        # Status
        self.status_label = Label(
            text='Gotowy do wyszukiwania',
            size_hint_y=None,
            height=35,
            font_size='13sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        main_layout.add_widget(self.status_label)

        print("[DEBUG] UI zbudowane")

        # Sprawdź Acestream Engine
        Clock.schedule_once(lambda dt: self.check_acestream_engine(), 0.5)

        # Załaduj początkową listę
        Clock.schedule_once(lambda dt: self.load_initial_channels(), 1)

        return main_layout

    def check_acestream_engine(self):
        """Sprawdź czy Acestream Engine działa"""
        print("[DEBUG] Sprawdzanie Acestream Engine...")

        def check_in_thread():
            for port in self.acestream_ports:
                try:
                    url = f"http://127.0.0.1:{port}/webui/api/service"
                    response = requests.get(url, timeout=1)
                    if response.status_code == 200:
                        self.acestream_url = f"http://127.0.0.1:{port}"
                        Clock.schedule_once(lambda dt: self._update_engine_status(port, True), 0)
                        return
                except:
                    continue

            Clock.schedule_once(lambda dt: self._update_engine_status(None, False), 0)

        thread = threading.Thread(target=check_in_thread)
        thread.daemon = True
        thread.start()

    def _update_engine_status(self, port, found):
        """Aktualizuj status engine"""
        if found:
            self.engine_status.text = f'✅ Engine: localhost:{port}'
            self.engine_status.color = (0, 1, 0, 1)
            print(f"[DEBUG] Acestream Engine znaleziony na porcie {port}")
        else:
            self.engine_status.text = '⚠️ Engine offline (tryb proxy)'
            self.engine_status.color = (1, 0.5, 0, 1)
            print("[DEBUG] Acestream Engine nie znaleziony")

    def on_player_change(self, spinner, text):
        """Zmiana playera"""
        if '🎬 VLC' in text:
            self.player_choice = "VLC"
        elif '🔴 Acestream' in text:
            self.player_choice = "ACESTREAM"
        elif '🌐 Proxy' in text:
            self.player_choice = "PROXY"
        else:
            self.player_choice = "COPY"

        print(f"[DEBUG] Wybrano player: {self.player_choice}")

    def load_initial_channels(self):
        """Załaduj początkową listę kanałów"""
        print("[DEBUG] Ładowanie początkowej listy...")
        self.status_label.text = '⏳ Ładowanie kanałów...'
        self._load_channels("[PL]")

    def _load_channels(self, query):
        """Ładowanie kanałów w osobnym wątku"""
        print(f"[DEBUG] Rozpoczęcie ładowania: {query}")

        def load_in_thread():
            try:
                print(f"[DEBUG] Wywołanie get_acestream_links({query})")
                channels = get_acestream_links(query)
                print(f"[DEBUG] Pobrano {len(channels)} kanałów")

                # Zaktualizuj GUI w głównym wątku
                Clock.schedule_once(lambda dt: self._update_channels(channels), 0)

            except Exception as e:
                print(f"[ERROR] Błąd ładowania: {e}")
                import traceback
                traceback.print_exc()
                Clock.schedule_once(lambda dt: self._update_channels([]), 0)

        thread = threading.Thread(target=load_in_thread)
        thread.daemon = True
        thread.start()

    def _update_channels(self, channels):
        """Aktualizuj GUI z pobranymi kanałami"""
        print(f"[DEBUG] Aktualizacja GUI: {len(channels)} kanałów")
        self.channels = channels
        self.display_channels()

    def search_channels(self, instance):
        """Wyszukaj kanały"""
        query = self.search_input.text.strip()
        print(f"[DEBUG] Wyszukiwanie: '{query}'")

        if not query:
            self.load_initial_channels()
            return

        self.status_label.text = f'🔍 Szukam: {query}...'
        self.channel_layout.clear_widgets()

        loading = Label(
            text='⏳ Wyszukiwanie...',
            size_hint_y=None,
            height=60,
            font_size='16sp'
        )
        self.channel_layout.add_widget(loading)

        self._load_channels(query)

    def display_channels(self):
        """Wyświetl listę kanałów"""
        print(f"[DEBUG] Wyświetlanie {len(self.channels)} kanałów")
        self.channel_layout.clear_widgets()

        if not self.channels:
            no_results = Label(
                text='❌ Brak wyników',
                size_hint_y=None,
                height=80,
                font_size='18sp',
                color=(1, 0.3, 0.3, 1)
            )
            self.channel_layout.add_widget(no_results)
            self.status_label.text = 'Brak wyników'
            self.counter_label.text = 'Kanały: 0'
            return

        for i, (title, link) in enumerate(self.channels, 1):
            btn = Button(
                text=f'{i}. 📺 {title[:60]}',
                size_hint_y=None,
                height=55,
                font_size='14sp',
                background_color=(0.15, 0.15, 0.2, 1),
                color=(1, 1, 1, 1),
                halign='left',
                valign='middle'
            )
            btn.bind(texture_size=btn.setter('text_size'))
            btn.bind(on_press=lambda x, t=title, l=link: self.select_channel(t, l))
            self.channel_layout.add_widget(btn)

        self.status_label.text = f'✅ Znaleziono {len(self.channels)} kanałów'
        self.counter_label.text = f'Kanały: {len(self.channels)}'
        print("[DEBUG] Kanały wyświetlone")

    def select_channel(self, title, link):
        """Wybierz kanał"""
        self.current_channel = title
        self.current_acestream_id = link.replace("acestream://", "")

        print(f"[DEBUG] Wybrano: {title}")
        print(f"[DEBUG] ID: {self.current_acestream_id}")

        self.status_label.text = f'✓ {title[:40]}'

        # Włącz przyciski
        self.play_btn.disabled = False
        self.copy_btn.disabled = False
        self.info_btn.disabled = False

        # Podświetl wybrany kanał
        for child in self.channel_layout.children:
            if isinstance(child, Button):
                if title in child.text:
                    child.background_color = (0.4, 0.3, 0.8, 1)
                else:
                    child.background_color = (0.15, 0.15, 0.2, 1)

    def play_selected(self, instance):
        """Odtwórz wybrany kanał"""
        if not self.current_acestream_id:
            return

        print(f"[DEBUG] Odtwarzanie: {self.player_choice}")

        if self.player_choice == "COPY":
            self.copy_link(instance)
            return

        if ANDROID:
            if self.player_choice == "VLC":
                self.play_in_vlc_android()
            elif self.player_choice == "PROXY":
                self.play_via_proxy_android()
            else:
                self.play_in_acestream_android()
        else:
            self.play_on_pc()

    def get_http_stream_url(self):
        """Pobierz HTTP URL streamu"""
        if self.acestream_url:
            url = f"{self.acestream_url}/ace/getstream?id={self.current_acestream_id}"
        else:
            url = f"http://acestream.info/ace/getstream?id={self.current_acestream_id}"

        print(f"[DEBUG] HTTP URL: {url}")
        return url

    def find_vlc_windows(self):
        """Znajdź VLC na Windows"""
        vlc_paths = []

        # Sprawdź rejestr
        if winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC")
                install_dir = winreg.QueryValueEx(key, "InstallDir")[0]
                vlc_exe = os.path.join(install_dir, "vlc.exe")
                if os.path.exists(vlc_exe):
                    vlc_paths.append(vlc_exe)
                    print(f"[DEBUG] VLC znaleziony w rejestrze: {vlc_exe}")
            except:
                pass

        # Sprawdź standardowe lokalizacje
        standard_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\VLC\vlc.exe"),
        ]

        for path in standard_paths:
            if os.path.exists(path) and path not in vlc_paths:
                vlc_paths.append(path)
                print(f"[DEBUG] VLC znaleziony: {path}")

        return vlc_paths

    def play_on_pc(self):
        """Otwórz w VLC na PC - z automatycznym uruchamianiem"""
        http_url = self.get_http_stream_url()

        # Skopiuj link do schowka
        Clipboard.copy(http_url)

        # Próba automatycznego uruchomienia VLC
        vlc_opened = False
        system = platform.system()

        try:
            if system == "Windows":
                # Znajdź VLC
                vlc_paths = self.find_vlc_windows()

                if vlc_paths:
                    vlc_path = vlc_paths[0]
                    print(f"[DEBUG] Uruchamianie VLC: {vlc_path}")
                    subprocess.Popen([vlc_path, http_url])
                    vlc_opened = True
                    self.status_label.text = '✅ VLC uruchomiony!'

            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "VLC", http_url])
                vlc_opened = True
                self.status_label.text = '✅ VLC uruchomiony!'
                print("[DEBUG] VLC uruchomiony (macOS)")

            elif system == "Linux":
                # Spróbuj różnych wariantów
                for cmd in ["vlc", "/usr/bin/vlc", "/snap/bin/vlc"]:
                    try:
                        subprocess.Popen([cmd, http_url])
                        vlc_opened = True
                        self.status_label.text = '✅ VLC uruchomiony!'
                        print(f"[DEBUG] VLC uruchomiony: {cmd}")
                        break
                    except FileNotFoundError:
                        continue

        except Exception as e:
            print(f"[ERROR] Błąd uruchamiania VLC: {e}")
            import traceback
            traceback.print_exc()

        # Pokaż odpowiedni komunikat
        if vlc_opened:
            msg = f"""✅ VLC uruchomiony automatycznie!

📺 {self.current_channel}

🔗 Stream URL:
{http_url}

Jeśli stream nie uruchomi się:
• Upewnij się że Acestream Engine działa
• Użyj trybu "🌐 Proxy Online"
• Ręcznie otwórz link (skopiowano do schowka)

💡 Wskazówka:
Aby stream działał, potrzebujesz uruchomionego
Acestream Engine w tle."""
        else:
            msg = f"""⚠️ Nie znaleziono VLC

📺 {self.current_channel}

🎬 Link HTTP (skopiowany do schowka):
{http_url}

Ręczna instrukcja:
1. Otwórz VLC
2. Menu: Media → Otwórz adres sieciowy (Ctrl+N)
3. Wklej link (Ctrl+V)
4. Kliknij Odtwórz

💡 Nie masz VLC? Pobierz:
https://www.videolan.org/vlc/

⚙️ Windows: VLC zwykle instaluje się w:
C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"""

        self.show_popup('VLC Player', msg.strip())

        if vlc_opened:
            print("[DEBUG] VLC auto-open: SUCCESS")
        else:
            print("[DEBUG] VLC auto-open: FAILED - link skopiowany")

    def play_in_vlc_android(self):
        """Otwórz w VLC na Androidzie"""
        try:
            http_url = self.get_http_stream_url()

            self.status_label.text = '🎬 Uruchamianie VLC...'

            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(http_url), "video/*")
            intent.setPackage("org.videolan.vlc")
            intent.putExtra("title", self.current_channel)

            activity = cast('android.app.Activity', PythonActivity.mActivity)
            activity.startActivity(intent)

            self.status_label.text = '✅ VLC uruchomiony!'
            print("[DEBUG] VLC uruchomiony na Androidzie")

        except Exception as e:
            print(f"[ERROR] Błąd VLC Android: {e}")
            self.show_popup('Błąd VLC', f'Nie można otworzyć VLC:\n{e}\n\nCzy VLC jest zainstalowany?')

    def play_via_proxy_android(self):
        """Użyj proxy online na Androidzie"""
        try:
            proxy_url = f"http://acestream.info/ace/getstream?id={self.current_acestream_id}"

            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(proxy_url), "video/*")

            activity = cast('android.app.Activity', PythonActivity.mActivity)
            activity.startActivity(Intent.createChooser(intent, "Otwórz w..."))

            self.status_label.text = '▶️ Otwarto przez proxy'

        except Exception as e:
            self.show_popup('Błąd', f'Błąd: {e}')

    def play_in_acestream_android(self):
        """Otwórz w Acestream Engine na Androidzie"""
        try:
            acestream_url = f"acestream://{self.current_acestream_id}"

            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(acestream_url))

            activity = cast('android.app.Activity', PythonActivity.mActivity)
            activity.startActivity(intent)

            self.status_label.text = '🔴 Uruchomiono Acestream'
        except Exception as e:
            self.show_popup('Błąd', str(e))

    def copy_link(self, instance):
        """Skopiuj linki do schowka"""
        if self.current_acestream_id:
            http_url = self.get_http_stream_url()
            acestream_link = f"acestream://{self.current_acestream_id}"

            # Kopiuj HTTP URL (najważniejszy)
            Clipboard.copy(http_url)

            msg = f"""📋 Skopiowano do schowka!

🔗 HTTP (VLC):
{http_url}

🔴 Acestream:
{acestream_link}

💡 Wklej w VLC:
1. Otwórz VLC
2. Ctrl+N (Otwórz adres sieciowy)
3. Ctrl+V (Wklej)
4. Enter"""

            self.show_popup('Skopiowano', msg)
            self.status_label.text = '📋 Linki skopiowane'

    def show_channel_info(self, instance):
        """Pokaż informacje o kanale"""
        if self.current_channel and self.current_acestream_id:
            http_url = self.get_http_stream_url()

            msg = f"""📺 Informacje o kanale

Nazwa:
{self.current_channel}

Acestream ID:
{self.current_acestream_id}

🔗 Link HTTP (VLC):
{http_url}

🔴 Link Acestream:
acestream://{self.current_acestream_id}

✅ Gotowe do odtworzenia!

💡 Wymagania:
• VLC Player (zainstalowany)
• Acestream Engine (uruchomiony w tle)
  LUB tryb "Proxy Online"
"""

            self.show_popup('Informacje', msg.strip())

    def show_popup(self, title, message):
        """Pokaż popup z wiadomością"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll = ScrollView(size_hint=(1, 0.8))
        msg_label = Label(
            text=message,
            size_hint_y=None,
            text_size=(Window.width * 0.7, None),
            halign='left',
            valign='top',
            font_size='13sp'
        )
        msg_label.bind(texture_size=msg_label.setter('size'))
        scroll.add_widget(msg_label)

        close_btn = Button(
            text='OK',
            size_hint=(1, 0.2),
            background_color=(0.4, 0.3, 0.8, 1),
            bold=True
        )

        content.add_widget(scroll)
        content.add_widget(close_btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.7)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    print("[DEBUG] Uruchamianie aplikacji...")
    try:
        AcestreamApp().run()
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback

        traceback.print_exc()
        input("Naciśnij Enter aby zamknąć...")
