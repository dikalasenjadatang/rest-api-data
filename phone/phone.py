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

def create_table(data):
    if 'error' in data:
        return f"<p>Error: {data['error']}</p>"
    
    if not data or not isinstance(data, dict) or 'data' not in data:
        return "<p>No data available</p>"
    
    items = data['data']
    if not items:
        return "<p>No results found</p>"
    
    headers = items[0].keys()
    table_html = "<table border='1'><tr>"
    for header in headers:
        table_html += f"<th>{header}</th>"
    table_html += "</tr>"
    
    for item in items:
        table_html += "<tr>"
        for value in item.values():
            table_html += f"<td>{value}</td>"
        table_html += "</tr>"
    
    table_html += "</table>"
    return table_html

@app.route('/dosen', methods=['GET'])
def get_dosen():
    keyword = request.args.get('keyword')
    if not keyword:
        return "Parameter 'keyword' (NIDN atau nama) is required.", 400
    data = get_data("enc/all", {"keyword": keyword})
    return render_template_string("<h1>Dosen Results</h1>" + create_table(data))

@app.route('/mahasiswa', methods=['GET'])
def get_mahasiswa():
    keyword = request.args.get('keyword')
    if not keyword:
        return "Parameter 'keyword' (NIM atau nama) is required.", 400
    data = get_data("enc/all", {"keyword": keyword})
    return render_template_string("<h1>Mahasiswa Results</h1>" + create_table(data))

@app.route('/pt', methods=['GET'])
def get_pt():
    pt_id = request.args.get('pt_id')
    if not pt_id:
        return "Parameter 'pt_id' is required.", 400
    data = get_data("detail-pt", {"pt_id": pt_id})
    return render_template_string("<h1>PT Results</h1>" + create_table(data))

@app.route('/prodi', methods=['GET'])
def get_prodi():
    prodi_id = request.args.get('prodi_id')
    if not prodi_id:
        return "Parameter 'prodi_id' is required.", 400
    data = get_data("detail-prodi", {"prodi_id": prodi_id})
    return render_template_string("<h1>Prodi Results</h1>" + create_table(data))

if __name__ == '__main__':
    app.run(debug=True)