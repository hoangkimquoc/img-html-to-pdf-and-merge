import json
import os

class LanguageManager:
    def __init__(self, default="vi"):
        self.lang = default
        self.cache = {}
        self.fallback = {
            "en": {
                "title": "Image to PDF Converter",
                "add_images": "Add Images",
                "add_folder": "Add Folder",
                "clear_all": "Clear All",
                "browse": "Browse",
                "convert": "Convert",
                "converting": "Converting...",
                "cancel": "Cancel",
                "canceling": "Canceling...",
                "settings": "Settings",
                "home": "Home",
                "theme": "Theme",
                "language": "Language",
                "light": "Light",
                "dark": "Dark",
                "en_label": "English",
                "vi_label": "Vietnamese",
                "empty_hint": "Drag and drop images here or use Add Images/Add Folder",
                "images_added_title": "Images Added",
                "images_added_body": "Added {n} images to the list.",
                "no_images_title": "No Images",
                "no_images_body": "Please add images before converting.",
                "no_output_title": "No Output Path",
                "no_output_body": "Please select an output directory.",
                "saved_success_title": "Success",
                "saved_success_body": "PDF saved to {path}",
                "conversion_failed_title": "Conversion Failed",
                "label_method": "Method:",
                "label_quality": "Quality:",
                "label_sort": "Sort by:",
                "method_one": "One by one",
                "method_all": "All in one",
                "compression_original": "Original Size",
                "compression_high": "High",
                "compression_medium": "Medium",
                "compression_low": "Low",
                "sort_name": "Name",
                "sort_mtime": "Date Modified",
                "sort_ctime": "Date Created",
                "sort_size": "Size",
                "portrait": "Portrait",
                "no_margin": "No Margin"
            },
            "vi": {
                "title": "Chuyển ảnh thành PDF",
                "add_images": "Thêm ảnh",
                "add_folder": "Thêm thư mục",
                "clear_all": "Xóa tất cả",
                "browse": "Chọn",
                "convert": "Chuyển đổi",
                "converting": "Đang chuyển đổi...",
                "cancel": "Hủy",
                "canceling": "Đang hủy...",
                "settings": "Cài đặt",
                "home": "Trang chủ",
                "theme": "Giao diện",
                "language": "Ngôn ngữ",
                "light": "Sáng",
                "dark": "Tối",
                "en_label": "Tiếng Anh",
                "vi_label": "Tiếng Việt",
                "empty_hint": "Kéo thả ảnh vào đây hoặc dùng Thêm ảnh/Thêm thư mục",
                "images_added_title": "Đã thêm ảnh",
                "images_added_body": "Đã thêm {n} ảnh vào danh sách.",
                "no_images_title": "Chưa có ảnh",
                "no_images_body": "Vui lòng thêm ảnh trước khi chuyển đổi.",
                "no_output_title": "Chưa chọn nơi lưu",
                "no_output_body": "Vui lòng chọn thư mục lưu file.",
                "saved_success_title": "Thành công",
                "saved_success_body": "Đã lưu PDF tại {path}",
                "conversion_failed_title": "Lỗi chuyển đổi",
                "label_method": "Chế độ:",
                "label_quality": "Chất lượng:",
                "label_sort": "Sắp xếp:",
                "method_one": "Từng ảnh một",
                "method_all": "Gộp tất cả",
                "compression_original": "Kích thước gốc",
                "compression_high": "Cao",
                "compression_medium": "Trung bình",
                "compression_low": "Thấp",
                "sort_name": "Tên file",
                "sort_mtime": "Ngày sửa",
                "sort_ctime": "Ngày tạo",
                "sort_size": "Kích thước",
                "portrait": "Khổ dọc",
                "no_margin": "Không viền"
            }
        }
    
    def load(self, lang):
        fname = f"i18n.{lang}.json"
        try:
            if os.path.exists(fname):
                with open(fname, "r", encoding="utf-8") as f:
                    self.cache[lang] = json.load(f)
            else:
                self.cache[lang] = self.fallback.get(lang, {})
        except Exception:
            self.cache[lang] = self.fallback.get(lang, {})
            
    def t(self, key, **kw):
        if self.lang not in self.cache:
            self.load(self.lang)
        text = self.cache.get(self.lang, {}).get(key, self.fallback.get(self.lang, {}).get(key, key))
        if kw:
            try:
                return text.format(**kw)
            except Exception:
                return text
        return text
