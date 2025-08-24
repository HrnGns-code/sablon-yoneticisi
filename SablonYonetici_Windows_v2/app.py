
import sys, os, json, uuid
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget, QListWidgetItem, QPushButton,
    QHBoxLayout, QVBoxLayout, QSplitter, QInputDialog, QMessageBox, QTextEdit,
    QLineEdit, QDialog, QDialogButtonBox, QLabel, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import Qt, QEvent

# Try to import keyboard for global hotkeys.
# If not available, the app still works without global hotkeys.
try:
    import keyboard  # pip install keyboard
    KEYBOARD_AVAILABLE = True
except Exception as e:
    KEYBOARD_AVAILABLE = False

APP_NAME = "Şablon Yöneticisi"
DATA_FILE = "templates.json"
SETTINGS_FILE = "settings.json"

def resource_path(relative_path: str) -> str:
    # Resolve path to be compatible both in dev and PyInstaller bundle
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def ensure_default_files():
    # Create default templates.json and settings.json if missing
    data_path = resource_path(DATA_FILE)
    settings_path = resource_path(SETTINGS_FILE)

    if not os.path.exists(data_path):
        sample = {
            "categories": [
                {
                    "name": "İptal",
                    "templates": [
                        {"id": str(uuid.uuid4()), "title": "Üyelik İptal 1",
                         "text": "Merhaba, talebiniz üzerine üyelik iptal işleminiz gerçekleştirildi. Herhangi bir sorunuz olursa yardımcı olmaktan memnuniyet duyarız."},
                        {"id": str(uuid.uuid4()), "title": "Sipariş İptal 1",
                         "text": "Bilgilendirme: İlgili sipariş iptal edilmiştir. Ücret iade süreci bankanıza bağlı olarak 1-7 iş günü içinde tamamlanacaktır."}
                    ]
                },
                {
                    "name": "Şikayet",
                    "templates": [
                        {"id": str(uuid.uuid4()), "title": "Kargo Gecikme Yanıtı",
                         "text": "Yaşanan gecikme için üzgünüz. Kargo sürecini hızlandırmak adına ilgili birimle görüştük; en kısa sürede teslim edilecektir."}
                    ]
                },
                {
                    "name": "Özür",
                    "templates": [
                        {"id": str(uuid.uuid4()), "title": "Genel Özür",
                         "text": "Yaşadığınız olumsuz deneyim için içtenlikle özür dileriz. Size daha iyi hizmet verebilmek için gerekli aksiyonları alıyoruz."}
                    ]
                }
            ]
        }
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)

    if not os.path.exists(settings_path):
        defaults = {
            "hotkeys": {
                # You can assign a template id to these hotkeys via UI (sağ tık -> kısayol ata).
                "ctrl+shift+t": None,
                "ctrl+shift+q": None
            },
            "auto_paste_on_click": True,
            "minimize_to_tray_on_close": True
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(defaults, f, ensure_ascii=False, indent=2)

class TemplateStore:
    def __init__(self, data_file: str):
        self.data_file = resource_path(data_file)
        self.data: Dict[str, Any] = {"categories": []}
        self.load()

    def load(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            # normalize
            if "categories" not in self.data or not isinstance(self.data["categories"], list):
                self.data["categories"] = []
        except Exception:
            self.data = {"categories": []}

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Save error:", e)

    # --- Category ops ---
    def list_categories(self) -> List[Dict[str, Any]]:
        return self.data["categories"]

    def add_category(self, name: str):
        self.data["categories"].append({"name": name, "templates": []})
        self.save()

    def rename_category(self, index: int, new_name: str):
        self.data["categories"][index]["name"] = new_name
        self.save()

    def delete_category(self, index: int):
        del self.data["categories"][index]
        self.save()

    # --- Template ops ---
    def list_templates(self, cat_index: int) -> List[Dict[str, Any]]:
        return self.data["categories"][cat_index]["templates"]

    def add_template(self, cat_index: int, title: str, text: str) -> str:
        tid = str(uuid.uuid4())
        self.data["categories"][cat_index]["templates"].append({"id": tid, "title": title, "text": text})
        self.save()
        return tid

    def edit_template(self, cat_index: int, tpl_index: int, title: str, text: str):
        self.data["categories"][cat_index]["templates"][tpl_index]["title"] = title
        self.data["categories"][cat_index]["templates"][tpl_index]["text"] = text
        self.save()

    def delete_template(self, cat_index: int, tpl_index: int):
        del self.data["categories"][cat_index]["templates"][tpl_index]
        self.save()

    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        for c in self.data["categories"]:
            for t in c["templates"]:
                if t.get("id") == template_id:
                    return t
        return None

class SettingsStore:
    def __init__(self, settings_file: str):
        self.settings_file = resource_path(settings_file)
        self.settings: Dict[str, Any] = {}
        self.load()

    def load(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except Exception:
            self.settings = {"hotkeys": {}, "auto_paste_on_click": True, "minimize_to_tray_on_close": True}

    def save(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Settings save error:", e)

    def get_hotkey_target(self, combo: str) -> Optional[str]:
        return self.settings.get("hotkeys", {}).get(combo)

    def set_hotkey_target(self, combo: str, template_id: Optional[str]):
        self.settings.setdefault("hotkeys", {})
        self.settings["hotkeys"][combo] = template_id
        self.save()

    def auto_paste_on_click(self) -> bool:
        return bool(self.settings.get("auto_paste_on_click", True))

    def set_auto_paste_on_click(self, value: bool):
        self.settings["auto_paste_on_click"] = bool(value)
        self.save()

class TemplateDialog(QDialog):
    def __init__(self, parent=None, title="Şablon", init_title="", init_text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(520, 380)

        self.title_edit = QLineEdit(self)
        self.title_edit.setText(init_title)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(init_text)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Başlık:"))
        form_layout.addWidget(self.title_edit)
        form_layout.addWidget(QLabel("Metin:"))
        form_layout.addWidget(self.text_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=self)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(btn_box)
        self.setLayout(main_layout)

    def get_values(self):
        return self.title_edit.text().strip(), self.text_edit.toPlainText()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(980, 600)

        self.store = TemplateStore(DATA_FILE)
        self.settings = SettingsStore(SETTINGS_FILE)

        # Build UI
        self.category_list = QListWidget(self)
        self.template_list = QListWidget(self)

        # Buttons
        self.btn_add_cat = QPushButton("Kategori Ekle")
        self.btn_ren_cat = QPushButton("Kategori Yeniden Adlandır")
        self.btn_del_cat = QPushButton("Kategori Sil")

        self.btn_add_tpl = QPushButton("Şablon Ekle")
        self.btn_edit_tpl = QPushButton("Şablon Düzenle")
        self.btn_del_tpl = QPushButton("Şablon Sil")

        # Layouts
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Kategoriler"))
        left_layout.addWidget(self.category_list)
        left_layout.addWidget(self.btn_add_cat)
        left_layout.addWidget(self.btn_ren_cat)
        left_layout.addWidget(self.btn_del_cat)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Şablonlar"))
        right_layout.addWidget(self.template_list)
        right_layout.addWidget(self.btn_add_tpl)
        right_layout.addWidget(self.btn_edit_tpl)
        right_layout.addWidget(self.btn_del_tpl)
        right_widget = QWidget()
        
        self.preview_edit = QTextEdit(self)
        self.preview_edit.setReadOnly(True)
        right_layout.addWidget(QLabel("Önizleme"))
        right_layout.addWidget(self.preview_edit)

        right_widget.setLayout(right_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        central = QWidget()
        central_layout = QHBoxLayout()
        central_layout.addWidget(splitter)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Context menu for template list
        self.template_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.template_list.customContextMenuRequested.connect(self.on_template_context_menu)

        # Connect signals
        self.category_list.currentRowChanged.connect(self.refresh_templates)
        self.template_list.itemDoubleClicked.connect(self.on_template_double_clicked)
        self.template_list.currentItemChanged.connect(self.on_template_selected)

        self.btn_add_cat.clicked.connect(self.add_category)
        self.btn_ren_cat.clicked.connect(self.rename_category)
        self.btn_del_cat.clicked.connect(self.delete_category)

        self.btn_add_tpl.clicked.connect(self.add_template)
        self.btn_edit_tpl.clicked.connect(self.edit_template)
        self.btn_del_tpl.clicked.connect(self.delete_template)

        self.build_tray_icon()
        self.refresh_categories()

        # Register global hotkeys
        self.hotkey_handles = []
        self.register_hotkeys()

    def on_template_selected(self, current, previous):
        if current:
            # Şablonun metnini al
            template_text = current.data(256)  # Qt.UserRole için 256 kullanıyoruz
            self.template_text.setPlainText(template_text)
        else:
            self.template_text.clear()

    # ---------- System Tray ----------
    def build_tray_icon(self):
        # Create a simple icon programmatically
        pm = QPixmap(64, 64)
        pm.fill(QColor("#2d89ef"))
        painter = QPainter(pm)
        painter.setPen(Qt.GlobalColor.white)
        painter.setBrush(Qt.GlobalColor.white)
        # Draw a simple "T" for Templates
        painter.drawRect(28, 10, 8, 36)  # vertical bar
        painter.drawRect(16, 10, 32, 8)  # top bar
        painter.end()

        icon = QIcon(pm)
        self.setWindowIcon(icon)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(icon, self)
            menu = QMenu()
            act_show = QAction("Göster", self, triggered=self.show_normal_from_tray)
            act_quit = QAction("Çıkış", self, triggered=self.quit_app)
            menu.addAction(act_show)
            menu.addSeparator()
            menu.addAction(act_quit)
            self.tray.setContextMenu(menu)
            self.tray.setToolTip(APP_NAME)
            self.tray.show()
        else:
            self.tray = None

    def show_normal_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def quit_app(self):
        self.unregister_hotkeys()
        QApplication.quit()

    def closeEvent(self, event):
        # Minimize to tray if enabled
        if self.settings.settings.get("minimize_to_tray_on_close", True) and self.tray:
            event.ignore()
            # self.hide()
            if self.tray:
                self.tray.showMessage(APP_NAME, "Arka planda çalışmaya devam ediyor.", QSystemTrayIcon.MessageIcon.Information, 2500)
        else:
            self.unregister_hotkeys()
            event.accept()

    # ---------- Data/UI ----------
    def refresh_categories(self):
        self.category_list.clear()
        for cat in self.store.list_categories():
            self.category_list.addItem(cat["name"])
        if self.category_list.count() > 0 and self.category_list.currentRow() < 0:
            self.category_list.setCurrentRow(0)

    def refresh_templates(self, cat_row: int):
        self.template_list.clear()
        if cat_row < 0 or cat_row >= len(self.store.list_categories()):
            return
        for tpl in self.store.list_templates(cat_row):
            item = QListWidgetItem(tpl["title"])
            item.setData(Qt.ItemDataRole.UserRole, tpl["id"])
            self.template_list.addItem(item)

    # ---------- Category ops ----------
    def add_category(self):
        name, ok = QInputDialog.getText(self, "Yeni Kategori", "Kategori adı:")
        if ok:
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Hata", "Kategori adı boş olamaz.")
                return
            self.store.add_category(name)
            self.refresh_categories()

    def rename_category(self):
        row = self.category_list.currentRow()
        if row < 0:
            return
        current_name = self.store.list_categories()[row]["name"]
        name, ok = QInputDialog.getText(self, "Kategori Yeniden Adlandır", "Yeni ad:", text=current_name)
        if ok:
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Hata", "Kategori adı boş olamaz.")
                return
            self.store.rename_category(row, name)
            self.refresh_categories()

    def delete_category(self):
        row = self.category_list.currentRow()
        if row < 0:
            return
        reply = QMessageBox.question(self, "Silinsin mi?", "Bu kategoriyi ve içindeki tüm şablonları silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.store.delete_category(row)
            self.refresh_categories()
            self.template_list.clear()

    # ---------- Template ops ----------
    def add_template(self):
        cat_row = self.category_list.currentRow()
        if cat_row < 0:
            QMessageBox.warning(self, "Hata", "Önce bir kategori seçiniz.")
            return
        dlg = TemplateDialog(self, title="Yeni Şablon", init_title="", init_text="")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            title, text = dlg.get_values()
            if not title.strip():
                QMessageBox.warning(self, "Hata", "Başlık boş olamaz.")
                return
            self.store.add_template(cat_row, title.strip(), text)
            self.refresh_templates(cat_row)

    def edit_template(self):
        cat_row = self.category_list.currentRow()
        tpl_row = self.template_list.currentRow()
        if cat_row < 0 or tpl_row < 0:
            return
        tpl = self.store.list_templates(cat_row)[tpl_row]
        dlg = TemplateDialog(self, title="Şablon Düzenle", init_title=tpl["title"], init_text=tpl["text"])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            title, text = dlg.get_values()
            if not title.strip():
                QMessageBox.warning(self, "Hata", "Başlık boş olamaz.")
                return
            self.store.edit_template(cat_row, tpl_row, title.strip(), text)
            self.refresh_templates(cat_row)

    def delete_template(self):
        cat_row = self.category_list.currentRow()
        tpl_row = self.template_list.currentRow()
        if cat_row < 0 or tpl_row < 0:
            return
        reply = QMessageBox.question(self, "Silinsin mi?", "Bu şablonu silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.store.delete_template(cat_row, tpl_row)
            self.refresh_templates(cat_row)

    # ---------- Use template ----------
    def on_template_double_clicked(self, item: QListWidgetItem):
        tpl_id = item.data(Qt.ItemDataRole.UserRole)
        tpl = self.store.get_template_by_id(tpl_id)
        if not tpl:
            return
        self.use_template_text(tpl["text"])

    def use_template_text(self, text: str, force_paste: Optional[bool] = None):
        # Copy to clipboard
        QApplication.clipboard().setText(text)
        auto_paste = self.settings.auto_paste_on_click() if force_paste is None else force_paste
        if auto_paste:
            # Hide window briefly so paste goes to previous app
            # self.hide()
            QApplication.processEvents()
            # Try to paste via keyboard if available
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.press_and_release("ctrl+v")
                except Exception:
                    pass
            # If keyboard module is not available, user can Ctrl+V manually
            # Brief info via tray
            if self.tray:
                self.tray.showMessage(APP_NAME, "Metin yapıştırıldı (veya panoya kopyalandı).", QSystemTrayIcon.MessageIcon.Information, 1800)
        else:
            if self.tray:
                self.tray.showMessage(APP_NAME, "Metin panoya kopyalandı.", QSystemTrayIcon.MessageIcon.Information, 1800)

    # ---------- Context menu on template list ----------
    def on_template_context_menu(self, pos):
        item = self.template_list.itemAt(pos)
        menu = QMenu(self)

        act_copy = QAction("Panoya Kopyala", self, triggered=lambda: self.context_copy(item))
        act_paste = QAction("Aktif Pencereye Yapıştır", self, triggered=lambda: self.context_paste(item))
        menu.addAction(act_copy)
        menu.addAction(act_paste)

        menu.addSeparator()
        act_assign_t = QAction("Ctrl+Shift+T kısayoluna ata", self, triggered=lambda: self.assign_hotkey_to_item(item, "ctrl+shift+t"))
        act_assign_q = QAction("Ctrl+Shift+Q kısayoluna ata", self, triggered=lambda: self.assign_hotkey_to_item(item, "ctrl+shift+q"))
        menu.addAction(act_assign_t)
        menu.addAction(act_assign_q)

        menu.exec(self.template_list.mapToGlobal(pos))

    def context_copy(self, item: Optional[QListWidgetItem]):
        if not item:
            return
        tpl_id = item.data(Qt.ItemDataRole.UserRole)
        tpl = self.store.get_template_by_id(tpl_id)
        if not tpl:
            return
        QApplication.clipboard().setText(tpl["text"])
        if self.tray:
            self.tray.showMessage(APP_NAME, "Panoya kopyalandı.", QSystemTrayIcon.MessageIcon.Information, 1200)

    def context_paste(self, item: Optional[QListWidgetItem]):
        if not item:
            return
        tpl_id = item.data(Qt.ItemDataRole.UserRole)
        tpl = self.store.get_template_by_id(tpl_id)
        if not tpl:
            return
        self.use_template_text(tpl["text"], force_paste=True)

    # ---------- Hotkeys ----------
    def unregister_hotkeys(self):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass

    def register_hotkeys(self):
        if not KEYBOARD_AVAILABLE:
            return
        self.unregister_hotkeys()

        for combo, tpl_id in self.settings.settings.get("hotkeys", {}).items():
            if tpl_id:
                def make_cb(tid):
                    def _cb():
                        tpl = self.store.get_template_by_id(tid)
                        if tpl:
                            self.use_template_text(tpl["text"], force_paste=True)
                    return _cb
                try:
                    keyboard.add_hotkey(combo, make_cb(tpl_id), suppress=False, trigger_on_release=True)
                except Exception as e:
                    print(f"Hotkey '{combo}' kaydı başarısız: {e}")

    def assign_hotkey_to_item(self, item: Optional[QListWidgetItem], combo: str):
        if not item:
            return
        if not KEYBOARD_AVAILABLE:
            QMessageBox.warning(self, "Kısayol", "Global kısayollar için 'keyboard' modülünü kurmanız gerekir:\npip install keyboard\nWindows'ta yönetici izinleri gerekebilir.")
            return
        tpl_id = item.data(Qt.ItemDataRole.UserRole)
        self.settings.set_hotkey_target(combo, tpl_id)
        self.register_hotkeys()
        if self.tray:
            self.tray.showMessage(APP_NAME, f"{combo} kısayolu şablona atandı.", QSystemTrayIcon.MessageIcon.Information, 1800)

def main():
    ensure_default_files()

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    if not KEYBOARD_AVAILABLE:
        # Inform user once about missing keyboard module
        QMessageBox.information(win, "Bilgi",
                                "Global kısayollar için 'keyboard' modülü bulunamadı.\n"
                                "Kısayolları kullanmak isterseniz:\n\n"
                                "    pip install keyboard\n\n"
                                "komutunu çalıştırın (Windows'ta yönetici izni gerekebilir).")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
