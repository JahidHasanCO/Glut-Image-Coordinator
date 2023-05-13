from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('index.html', uploaded=True)
    return render_template('index.html', uploaded=False)

@app.route('/upload', methods=['POST'])
def upload():
    image_file = request.files['image']
    if image_file:
        image = Image.open(image_file)
        image = image.convert('RGB')
        image = image.resize((500, 500), Image.LANCZOS)
        filename = 'uploaded_image.jpg'
        image_path = os.path.join(app.root_path, 'static', filename)
        image.save(image_path)

        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({'status': 'success', 'image_data': image_data})

    return jsonify({'status': 'error'})


@app.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    x = float(request.form['x'])
    y = float(request.form['y'])
    y = (500 - (y*500))/500  
    coords = f"X: {x}, Y: {y}"
    rgb = f"R: 0, G: 0, B: 0"  # Replace with your logic to retrieve RGB values based on coordinates
    return jsonify({'coords': coords, 'rgb': rgb})

if __name__ == '__main__':
    app.run()
 