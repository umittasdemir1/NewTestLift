from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Upload klasörü yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    df = pd.read_excel(filepath)

    # Ürün grubu sütunları sabit kabul ediliyor
    if 'ÜRÜN GRUBU' not in df.columns or 'FATURA NO' not in df.columns:
        return 'Missing required columns.'

    # Satış adedi = satır sayısı
    product_counts = df['ÜRÜN GRUBU'].value_counts().to_frame(name='Sales Count')
    product_counts.reset_index(inplace=True)
    product_counts.columns = ['Product Group', 'Sales Count']

    # Sepet analizi: aynı fatura içinde birlikte geçen ürün grupları
    grouped = df.groupby('FATURA NO')['ÜRÜN GRUBU'].apply(list)

    from itertools import combinations
    from collections import Counter
    combos = Counter()

    for items in grouped:
        unique_items = list(set(items))
        combos.update(combinations(sorted(unique_items), 2))

    top_combos = combos.most_common(10)
    combo_df = pd.DataFrame(top_combos, columns=['Product Pair', 'Count'])

    return render_template('result.html', product_counts=product_counts.to_html(index=False), combo_table=combo_df.to_html(index=False))

if __name__ == '__main__':
    app.run(debug=True)
