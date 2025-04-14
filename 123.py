import os
from flask import Flask, request, send_from_directory, render_template_string, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>File Storage</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-align: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
        }
        input, button {
            margin: 10px;
            padding: 12px;
            font-size: 16px;
            border-radius: 5px;
            border: none;
        }
        button {
            background-color: #28a745;
            color: white;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background-color: #218838;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            background: rgba(255, 255, 255, 0.2);
            margin: 5px 0;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .delete-btn {
            background-color: #dc3545;
            padding: 6px 12px;
            font-size: 14px;
            border-radius: 5px;
            transition: 0.3s;
        }
        .delete-btn:hover {
            background-color: #c82333;
        }
    </style>
</head>
<body>
    <div class='container'>
        <h1>📂 File Storage For PDF/Docx Group2
    </h1>
        <form id='uploadForm' enctype='multipart/form-data'>
            <input type='file' id='fileInput' name='file'>
            <button type='button' onclick='uploadFile()'>Upload</button>
        </form>
        <h2>Stored Files</h2>
        <ul id='fileList'></ul>
    </div>
    <script>
        function uploadFile() {
            let formData = new FormData(document.getElementById('uploadForm'));
            fetch('/upload', { method: 'POST', body: formData })
                .then(response => response.json())
                .then(() => loadFiles());
        }
        function loadFiles() {
            fetch('/files')
                .then(response => response.json())
                .then(data => {
                    let fileList = document.getElementById('fileList');
                    fileList.innerHTML = '';
                    data.files.forEach(file => {
                        let li = document.createElement('li');
                        li.innerHTML = `<a href='/download/${file}' style='color: white;'>${file}</a> 
                                        <button class='delete-btn' onclick='deleteFile("${file}")'>Delete</button>`;
                        fileList.appendChild(li);
                    });
                });
        }
        function deleteFile(filename) {
            fetch(`/delete/${filename}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(() => loadFiles());
        }
        loadFiles();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400
    if file and allowed_file(file.filename):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return {"message": "File uploaded successfully"}, 200
    return {"error": "Invalid file type"}, 400

@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return {"files": files}, 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"}), 200
    return jsonify({"error": "File not found"}), 404

def allowed_file(filename):
    return filename.lower().endswith((".pdf", ".docx"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
