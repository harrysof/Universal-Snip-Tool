import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from PIL import ImageGrab, ImageEnhance, ImageOps, Image, ImageTk
from pix2tex.cli import LatexOCR
import pyperclip
import threading
import ctypes
import time
import re

class LatexSnipper:
    def __init__(self):
        self.latex_model = None
        self.tesseract_available = False
        self.is_loading = True
        self.history = []
        
        # Check for Tesseract
        try:
            import pytesseract
            # If Tesseract is not in PATH, uncomment and set the correct path:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self.pytesseract = pytesseract
            self.tesseract_available = True
        except ImportError:
            self.pytesseract = None
        
        # Fix DPI awareness for Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass
        
        # --- UI SETUP ---
        self.root = tk.Tk()
        self.root.title("Universal Snip Tool")
        self.root.geometry("450x380")
        self.root.attributes("-topmost", True)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Loading AI...", fg="red", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)
        
        # Mode Selection Frame
        mode_frame = tk.LabelFrame(self.root, text="Recognition Mode", font=("Arial", 9, "bold"))
        mode_frame.pack(pady=5, padx=10, fill="x")
        
        self.mode_var = tk.StringVar(value="latex")
        
        mode_inner = tk.Frame(mode_frame)
        mode_inner.pack(pady=5)
        
        tk.Radiobutton(mode_inner, text="📐 Math (LaTeX)", variable=self.mode_var, 
                      value="latex", font=("Arial", 9)).grid(row=0, column=0, padx=10)
        tk.Radiobutton(mode_inner, text="📝 Text (OCR)", variable=self.mode_var, 
                      value="text", font=("Arial", 9)).grid(row=0, column=1, padx=10)
        
        # Language selection (for text mode)
        lang_frame = tk.Frame(mode_frame)
        lang_frame.pack(pady=2)
        tk.Label(lang_frame, text="Language:", font=("Arial", 8)).pack(side="left", padx=5)
        
        self.lang_var = tk.StringVar(value="eng+fra+ara")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                   values=["eng", "fra", "ara", "eng+fra", "eng+ara", "fra+ara", "eng+fra+ara"],
                                   width=15, state="readonly", font=("Arial", 8))
        lang_combo.pack(side="left")
        
        # Snip Button
        self.btn_snip = tk.Button(
            self.root, text="✂ Start Snipping", 
            command=self.start_snip, 
            state="disabled", 
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.btn_snip.pack(pady=10, padx=20, fill="x")
        
        # Options Frame
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=5)
        
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = tk.Checkbutton(options_frame, text="Debug mode", variable=self.debug_var)
        self.debug_check.grid(row=0, column=0, padx=5)
        
        self.text_var = tk.BooleanVar(value=True)
        self.text_check = tk.Checkbutton(options_frame, text="Convert LaTeX to text", variable=self.text_var)
        self.text_check.grid(row=0, column=1, padx=5)
        
        # Result display
        result_label = tk.Label(self.root, text="Last Result:", font=("Arial", 9))
        result_label.pack(pady=(10, 0))
        
        self.result_text = scrolledtext.ScrolledText(self.root, height=6, wrap=tk.WORD, font=("Courier", 9))
        self.result_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Button frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        self.btn_copy = tk.Button(btn_frame, text="📋 Copy Result", command=self.copy_result, 
                                  state="disabled", font=("Arial", 9, "bold"))
        self.btn_copy.pack()
        
        # Info label
        info_text = "LaTeX mode: Math equations | Text mode: Multilingual OCR"
        if not self.tesseract_available:
            info_text = "⚠️ Install Tesseract for text OCR: pip install pytesseract"
        
        info_label = tk.Label(self.root, text=info_text, font=("Arial", 7), fg="gray", wraplength=400)
        info_label.pack(pady=2)

        # Load model in background
        threading.Thread(target=self.load_model, daemon=True).start()
        
        self.root.mainloop()

    def load_model(self):
        """Loads the LaTeX AI model once at startup."""
        try:
            self.latex_model = LatexOCR()
            self.is_loading = False
            self.root.after(0, self.on_model_loaded)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load LaTeX model:\n{e}"))

    def on_model_loaded(self):
        status_text = "✓ Ready (LaTeX"
        if self.tesseract_available:
            status_text += " + Text OCR)"
        else:
            status_text += " only)"
        
        self.status_label.config(text=status_text, fg="green")
        self.btn_snip.config(state="normal")

    def start_snip(self):
        """Hides window and starts snipping."""
        # Check if Tesseract is needed but not available
        if self.mode_var.get() == "text" and not self.tesseract_available:
            messagebox.showwarning("Tesseract Not Found", 
                                 "Text OCR requires Tesseract.\n\n"
                                 "Install: pip install pytesseract\n"
                                 "And download Tesseract from:\n"
                                 "https://github.com/UB-Mannheim/tesseract/wiki")
            return
        
        self.root.withdraw()
        self.root.update()
        time.sleep(0.2)
        
        # Take a full screenshot first
        self.full_screenshot = ImageGrab.grab()
        self.create_snip_window()
    
    def create_snip_window(self):
        self.snip_window = tk.Toplevel(self.root)
        self.snip_window.attributes("-fullscreen", True)
        self.snip_window.attributes("-topmost", True)
        
        # Create canvas
        self.canvas = tk.Canvas(self.snip_window, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Darken screenshot for overlay
        dark_img = self.full_screenshot.point(lambda p: int(p * 0.3))
        self.bg_image = ImageTk.PhotoImage(dark_img)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.cancel_snip())
        
        # Instructions
        mode_text = "equation" if self.mode_var.get() == "latex" else "text"
        self.canvas.create_text(
            self.snip_window.winfo_screenwidth() // 2, 30, 
            text=f"Select {mode_text} to recognize (ESC to cancel)", 
            fill="white", font=("Arial", 14, "bold")
        )

    def on_click(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='red', width=3
        )
        self.highlight = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill='white', stipple='gray50', outline=''
        )

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        self.canvas.coords(self.highlight, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))
        
        self.snip_window.destroy()
        
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            self.process_image_from_screenshot(x1, y1, x2, y2)
        else:
            self.root.deiconify()

    def cancel_snip(self):
        self.snip_window.destroy()
        self.root.deiconify()

    def preprocess_for_latex(self, img):
        """Enhanced preprocessing for LaTeX OCR."""
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if self.debug_var.get():
            img.save("debug_1_original.png")
        
        gray = ImageOps.grayscale(img)
        gray = ImageOps.autocontrast(gray, cutoff=2)
        
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(3.0)
        
        enhancer = ImageEnhance.Sharpness(gray)
        gray = enhancer.enhance(2.5)
        
        img = gray.convert('RGB')
        
        if self.debug_var.get():
            img.save("debug_2_enhanced.png")
        
        width, height = img.size
        min_width, min_height = 400, 200
        
        if width < min_width or height < min_height:
            scale = max(min_width / width, min_height / height)
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            if self.debug_var.get():
                img.save("debug_3_resized.png")
        
        padding = 20
        new_width = img.width + 2 * padding
        new_height = img.height + 2 * padding
        padded = Image.new('RGB', (new_width, new_height), 'white')
        padded.paste(img, (padding, padding))
        
        if self.debug_var.get():
            padded.save("debug_4_final.png")
        
        return padded

    def preprocess_for_text(self, img):
        """Preprocessing optimized for text OCR."""
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if self.debug_var.get():
            img.save("debug_text_1_original.png")
        
        # Convert to grayscale
        gray = ImageOps.grayscale(img)
        
        # Auto contrast
        gray = ImageOps.autocontrast(gray, cutoff=1)
        
        # Moderate enhancement (less aggressive than LaTeX)
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(gray)
        gray = enhancer.enhance(1.5)
        
        # Scale up if too small
        width, height = gray.size
        if width < 300 or height < 100:
            scale = max(300 / width, 100 / height)
            new_size = (int(width * scale * 2), int(height * scale * 2))
            gray = gray.resize(new_size, Image.Resampling.LANCZOS)
        
        if self.debug_var.get():
            gray.save("debug_text_2_final.png")
        
        return gray

    def latex_to_text(self, latex):
        """Convert LaTeX to more readable text format."""
        text = latex
        
        replacements = {
            r'\\frac{([^}]+)}{([^}]+)}': r'(\1)/(\2)',
            r'\\sqrt{([^}]+)}': r'√(\1)',
            r'\\int': '∫', r'\\sum': '∑', r'\\prod': '∏',
            r'\\infty': '∞', r'\\alpha': 'α', r'\\beta': 'β',
            r'\\gamma': 'γ', r'\\delta': 'δ', r'\\theta': 'θ',
            r'\\pi': 'π', r'\\sigma': 'σ', r'\\omega': 'ω',
            r'\\leq': '≤', r'\\geq': '≥', r'\\neq': '≠',
            r'\\approx': '≈', r'\\times': '×', r'\\div': '÷',
            r'\\pm': '±', r'\\cdot': '·', r'\\partial': '∂',
            r'\\nabla': '∇', r'\\in': '∈', r'\\subset': '⊂',
            r'\\cup': '∪', r'\\cap': '∩', r'\\rightarrow': '→',
            r'\\leftarrow': '←', r'\\Rightarrow': '⇒', r'\\Leftarrow': '⇐',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        text = re.sub(r'_\{([^}]+)\}', r'_(\1)', text)
        text = re.sub(r'\^\{([^}]+)\}', r'^(\1)', text)
        text = re.sub(r'_(\w)', r'_\1', text)
        text = re.sub(r'\^(\w)', r'^\1', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('{ ', '{').replace(' }', '}')
        
        return text.strip()

    def clean_latex(self, latex):
        """Post-process LaTeX to fix common OCR errors."""
        latex = re.sub(r'\s+', ' ', latex).strip()
        latex = latex.replace('| ', '|').replace(' |', '|')
        latex = latex.replace('( ', '(').replace(' )', ')')
        return latex

    def process_image_from_screenshot(self, x1, y1, x2, y2):
        try:
            self.status_label.config(text="Processing...", fg="orange")
            self.root.deiconify()
            self.root.update()
            
            # Crop from screenshot
            img = self.full_screenshot.crop((x1, y1, x2, y2))
            
            result = ""
            result_type = ""
            
            if self.mode_var.get() == "latex":
                # LaTeX recognition
                img_processed = self.preprocess_for_latex(img)
                latex = self.latex_model(img_processed)
                latex = self.clean_latex(latex)
                
                result = f"LaTeX: {latex}"
                result_type = "latex"
                
                if self.text_var.get():
                    text_version = self.latex_to_text(latex)
                    result += f"\n\nText:  {text_version}"
                
                # Store for copying
                self.last_result = latex
                
            else:
                # Text OCR
                img_processed = self.preprocess_for_text(img)
                
                # Get selected language
                lang = self.lang_var.get()
                
                # Run Tesseract OCR
                text = self.pytesseract.image_to_string(img_processed, lang=lang)
                text = text.strip()
                
                result = f"Text ({lang}):\n{text}"
                result_type = "text"
                
                # Store for copying
                self.last_result = text
            
            # Display result
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
            # Auto-copy to clipboard
            pyperclip.copy(self.last_result)
            
            # Enable copy button
            self.btn_copy.config(state="normal")
            
            self.status_label.config(text="✓ Copied to clipboard!", fg="green")
            print(f"Result: {self.last_result}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.config(text="✗ Error processing image", fg="red")

    def copy_result(self):
        if hasattr(self, 'last_result'):
            pyperclip.copy(self.last_result)
            self.status_label.config(text="✓ Copied!", fg="blue")

if __name__ == "__main__":
    LatexSnipper()