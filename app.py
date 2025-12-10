from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os, uuid

app = Flask(__name__)

OUTPUT_DIR = "static/memes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_PATH = "anton.ttf"     

def draw_text_on_image(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    def load_font(size):
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except:
            return ImageFont.load_default()

    def draw_centered(text, y):
        text = text.upper()

        size = max(20, w // 12)
        font = load_font(size)

        while True:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= w - 30 or size <= 10:
                break

            size -= 2
            font = load_font(size)

        x = (w - text_width) // 2

        outline = max(1, size // 13)

        for ox in range(-outline, outline + 1):
            for oy in range(-outline, outline + 1):
                if ox * ox + oy * oy <= outline * outline:
                    draw.text((x + ox, y + oy), text, font=font, fill="black")

        draw.text((x, y), text, font=font, fill="white")

    if top_text:
        draw_centered(top_text, 10)

    if bottom_text:
        bottom_y = int(h * 0.93) - 20  
        draw_centered(bottom_text, bottom_y)

    return img


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded = request.files.get("image")
        top = request.form.get("top_text", "")
        bottom = request.form.get("bottom_text", "")

        if not uploaded:
            return render_template("index.html", error="No file uploaded.")

        img = Image.open(uploaded).convert("RGB")

        img = draw_text_on_image(img, top, bottom)

        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, format="PNG")

        return send_file(path, mimetype="image/png")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
