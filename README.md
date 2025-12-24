# Universal Snip Tool 📸🔬

A powerful desktop application that combines **LaTeX equation recognition** and **multilingual text OCR** into one easy-to-use snipping tool. Perfect for students, researchers, and anyone who needs to quickly digitize mathematical equations or extract text from screenshots.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **📐 LaTeX Math Recognition**: Capture mathematical equations and convert them to LaTeX code
- **📝 Multilingual Text OCR**: Extract text in English, French, Arabic, and combinations
- **🎯 Interactive Snipping**: Click and drag to select exactly what you need
- **📋 Auto-Copy**: Results automatically copied to clipboard
- **🔄 Dual Output**: Get both LaTeX and readable text formats for equations
- **🐛 Debug Mode**: Save intermediate processing steps for troubleshooting
- **⚡ GPU Acceleration**: Fast processing using AI models
- **🖥️ DPI Aware**: Works perfectly on high-resolution displays

## 🎬 Demo

Select the mode (Math or Text), click "Start Snipping", drag to select your region, and instantly get the recognized content copied to your clipboard!

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Windows, macOS, or Linux

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/universal-snip-tool.git
cd universal-snip-tool
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Tesseract OCR (for Text Mode)

**Windows:**
1. Download the installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the installation path
3. Update line 19 in the code with your Tesseract path if different:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 4: Install Language Packs (Optional)

For multilingual text recognition, install additional language packs:

**Windows:** Select languages during Tesseract installation

**macOS/Linux:**
```bash
# French
sudo apt-get install tesseract-ocr-fra

# Arabic
sudo apt-get install tesseract-ocr-ara
```

## 📦 Requirements

Create a `requirements.txt` file with:

```
tkinter
pillow>=9.0.0
pix2tex>=0.1.2
pyperclip>=1.8.0
pytesseract>=0.3.10
```

## 🎮 Usage

### Starting the Application

```bash
python "Latex + OCR.py"
```

### Math Mode (LaTeX)

1. Select **"🔬 Math (LaTeX)"** mode
2. Click **"✂ Start Snipping"**
3. Drag to select the mathematical equation
4. Release to process
5. LaTeX code is automatically copied to clipboard

**Example Output:**
```
LaTeX: \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}

Text:  (-b ± √(b^2 - 4ac))/(2a)
```

### Text Mode (OCR)

1. Select **"📝 Text (OCR)"** mode
2. Choose your language(s) from the dropdown
3. Click **"✂ Start Snipping"**
4. Drag to select the text region
5. Extracted text is automatically copied to clipboard

**Supported Languages:**
- English (`eng`)
- French (`fra`)
- Arabic (`ara`)
- Any combination (`eng+fra+ara`)

### Keyboard Shortcuts

- **ESC**: Cancel snipping and return to main window
- **Click & Drag**: Select region to capture

## ⚙️ Configuration Options

### Debug Mode
Enable to save intermediate image processing steps:
- `debug_1_original.png` - Original cropped image
- `debug_2_enhanced.png` - After contrast/sharpness enhancement
- `debug_3_resized.png` - After resizing (if needed)
- `debug_4_final.png` - Final preprocessed image

### Convert LaTeX to Text
When enabled, displays both LaTeX code and a human-readable text version with Unicode symbols (∫, √, π, etc.)

## 🔧 Troubleshooting

### "Tesseract Not Found" Error
- Ensure Tesseract is installed
- Check the path in line 19 matches your installation
- On Linux/macOS, ensure Tesseract is in your PATH

### Poor Recognition Quality
- Enable Debug Mode to inspect preprocessing
- Ensure the selected region has good contrast
- Try capturing a larger area
- For LaTeX: Use images with clear, high-resolution equations

### Model Loading Fails
- Check internet connection (first run downloads models)
- Ensure you have write permissions in the application directory
- Try reinstalling `pix2tex`: `pip install --upgrade pix2tex`

## 🏗️ Architecture

```
┌─────────────────────┐
│   GUI (tkinter)     │
├─────────────────────┤
│  Snipping Canvas    │
├─────────────────────┤
│  Image Preprocessing│
│  - Grayscale        │
│  - Contrast/Sharp   │
│  - Resize/Pad       │
├─────────────────────┤
│  Recognition Engine │
│  ├─ pix2tex (LaTeX) │
│  └─ Tesseract (OCR) │
├─────────────────────┤
│  Post-Processing    │
│  - LaTeX cleanup    │
│  - Text formatting  │
└─────────────────────┘
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) - LaTeX OCR engine
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Text recognition engine
- [Pillow](https://python-pillow.org/) - Image processing library

---

**Made with ❤️ by Harrysof**
