from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

BASE_URL = "https://pddikti.kemdikbud.go.id/api/pencarian/enc/all"

def get_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except ValueError as e:  # Includes JSONDecodeError
        return {"error": f"Failed to decode JSON. Raw response: {response.text}"}

def format_data(data):
    if 'error' in data:
        return f"Error: {data['error']}"
    
    if not data or not isinstance(data, dict) or 'data' not in data:
        return "No data available"
    
    items = data['data']
    if not items:
        return "No results found"
    
    result = ""
    for item in items:
        for key, value in item.items():
            result += f"{key}: {value}\n"
        result += "\n"
    
    return result

@app.route('/dosen', methods=['GET'])
def get_dosen():
    keyword = request.args.get('keyword')
    if not keyword:
        return "Parameter 'keyword' (NIDN atau nama) is required.", 400
    data = get_data("enc/all", {"keyword": keyword})
    return render_template_string("<h1>Dosen Results</h1><pre>{{ results }}</pre>", results=format_data(data))

@app.route('/mahasiswa', methods=['GET'])
def get_mahasiswa():
    keyword = request.args.get('keyword')
    if not keyword:
        return "Parameter 'keyword' (NIM atau nama) is required.", 400
    data = get_data("enc/all", {"keyword": keyword})
    return render_template_string("<h1>Mahasiswa Results</h1><pre>{{ results }}</pre>", results=format_data(data))

@app.route('/pt', methods=['GET'])
def get_pt():
    pt_id = request.args.get('pt_id')
    if not pt_id:
        return "Parameter 'pt_id' is required.", 400
    data = get_data("detail-pt", {"pt_id": pt_id})
    return render_template_string("<h1>PT Results</h1><pre>{{ results }}</pre>", results=format_data(data))

@app.route('/prodi', methods=['GET'])
def get_prodi():
    prodi_id = request.args.get('prodi_id')
    if not prodi_id:
        return "Parameter 'prodi_id' is required.", 400
    data = get_data("detail-prodi", {"prodi_id": prodi_id})
    return render_template_string("<h1>Prodi Results</h1><pre>{{ results }}</pre>", results=format_data(data))

if __name__ == '__main__':
    app.run(debug=True)