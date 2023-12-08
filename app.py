from flask import Flask, render_template, request, redirect, url_for, send_file
from bs4 import BeautifulSoup
import requests
import ast
import pandas as pd

app = Flask(__name__)

soup = None
html_tree = None
part_parse_element = None
html_part_tree = None
data_for_parse = None
parse_class = None
parse_el_type = None

def make_tree(soup, level=0, node_id=0):
    parts = []
    if soup.name and soup:
        parts.append(f"<div class='tree-node' id='node_{node_id}' style='margin-left: {level * 5}px;'>{soup.name}. {soup.get('class')}\n")
        parts.append("<button class='plus-btn'>+</button>\n")
    for idx, child in enumerate(soup.children):
        if not isinstance(child, str):
            parts.append(make_tree(child, level + 1, f"{node_id}_{idx}"))
    parts.append("</div>")
    return ''.join(parts)

def make_tree_particular(soup, level=0, node_id=0):
    parts = []
    if soup.name and soup:
        parts.append(f"<div class='tree-node' id='node_{node_id}' style='margin-left: {level * 5}px;'>{soup.name}. {soup.get('class')}\n")
        parts.append("<button class='plus-btn-part'>+</button>\n") 
    for idx, child in enumerate(soup.children):
        if not isinstance(child, str):
            parts.append(make_tree_particular(child, level + 1, f"{node_id}_{idx}"))
    parts.append("</div>")
    return ''.join(parts)
    
@app.route('/')
def index():
    return render_template(
        'index.html', 
        output=soup, 
        html_tree=html_tree, 
        part_parse_element=part_parse_element, 
        html_part_tree=html_part_tree,
        data_for_parse=data_for_parse
    )

@app.route('/get_tree', methods=['POST'])
def get_tree():
    global soup, html_tree
    
    link = request.form.get("link")

    html_text = requests.get(link).content

    soup = BeautifulSoup(html_text, 'html.parser')
    soup = soup.find('body')
    for s in soup.select('script'):
        s.extract()

    html_tree = make_tree(soup)

    return redirect(url_for('index'))

@app.route('/parse_particular', methods=['POST'])
def parse_particular():
    global part_parse_element, soup, html_part_tree, parse_class, parse_el_type

    parse_el = request.form.get("parsed_element").split('. ')

    parse_class = ast.literal_eval(parse_el[1])[0]
    parse_el_type = parse_el[0]

    part_parse_element = soup.find(parse_el_type, class_=parse_class)

    html_part_tree = make_tree_particular(part_parse_element)

    print(html_part_tree)

    return redirect(url_for('index'))

@app.route('/parse_all', methods=['POST'])
def parse_all():
    global data_for_parse, parse_el_type, parse_class
    data_for_parse = request.json

    data_for_parse = ast.literal_eval(str(data_for_parse))

    print(data_for_parse)

    all_el = soup.find_all(parse_el_type, class_=parse_class)

    df = []

    for div in all_el:
        cur = []
        for el in data_for_parse:
            classname = ast.literal_eval(el["el_classname"])[0]
            cur.append(div.find(el["el_type"], classname).text.strip())
        df.append(cur)

    print(df)

    df = pd.DataFrame(df)
    df.to_csv('data.csv', index=False)

    return send_file('data.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)