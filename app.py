import base64
import io
import os

import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


def generar_qr(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


@app.route("/", methods=["GET", "POST"])
def index():
    qr_base64 = None
    url = ""
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            error = "Ingresa una URL válida."
        else:
            png_bytes = generar_qr(url)
            qr_base64 = base64.b64encode(png_bytes).decode("ascii")

    return render_template("index.html", qr_base64=qr_base64, url=url, error=error)


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    if not url:
        return "URL vacía", 400

    png_bytes = generar_qr(url)
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name="qr_resultado.png",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
