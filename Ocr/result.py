from Levenshtein import distance
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

font_path = os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf")
fm.fontManager.addfont(font_path)
fontprop = fm.FontProperties(fname=font_path)

font_name = fontprop.get_name()
print("폰트 이름:", font_name)

plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False

def calculate_accuracy(original, ocr):
    dist = distance(original, ocr)
    max_len = max(len(original), len(ocr))
    accuracy = (1 - dist / max_len) * 100
    return accuracy

true_path = "input/true.txt"
ocr_files = {
    "Tesseract": "output/tesseract.txt",
    "OCR.Space": "output/ocrspace.txt",
    "PDF+Tesseract": "output/pymupdf_tesseract.txt"
}

with open(true_path, "r", encoding="utf-8") as f:
    true_text = f.read()

results = {}
for name, file_path in ocr_files.items():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ocr_text = f.read()
    except FileNotFoundError:
        print(f"파일 없음: {file_path}")
        results[name] = 0
        continue

    acc = calculate_accuracy(true_text, ocr_text)
    results[name] = acc
    print(f"{name} 정확도: {acc:.2f}%")


methods = list(results.keys())
scores = list(results.values())

plt.bar(methods, scores)
plt.title("OCR 정확도 비교")
plt.ylabel("정확도 (%)")
plt.ylim(0, 100)
plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.savefig("output/ocr_accuracy_comparison.png")
print("\n 그래프 저장됨: output/ocr_accuracy_comparison.png")

plt.show()
