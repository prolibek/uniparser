from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

soup = None
html_tree = None

def make_tree(soup, level=0, node_id=0):
    parts = []
    if soup.name and soup:
        parts.append(f"<div class='tree-node' id='node_{node_id}' style='margin-left: {level * 5}px;'>{soup.name}. {soup.get('class')}\n")
        parts.append("<button class='plus-btn'>+</button>\n")  # Add the plus button
    for idx, child in enumerate(soup.children):
        if not isinstance(child, str):
            parts.append(make_tree(child, level + 1, f"{node_id}_{idx}"))
    parts.append("</div>")
    return ''.join(parts)
    
@app.route('/')
def index():
    return render_template('index.html', output=soup, html_tree=html_tree)

@app.route('/', methods=['POST'])
def get_tree():
    global soup, html_tree
    
    link = request.form.get("link")

    html_text = requests.get(link).content

    soup = BeautifulSoup(html_text, 'html.parser')
    soup = soup.find('body')
    for s in soup.select('script'):
        s.extract()

    html_tree = make_tree(soup)

    print(html_tree)

    return redirect(url_for('index'))

@app.route('/', methods=['POST'])
def parse():
    pass

if __name__ == '__main__':
    app.run(debug=True)