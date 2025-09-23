
import pandas as pd
import re

def clean_and_merge_upcs(upc_file_path, partner_file_path, header_row_guess=0):
    upc_excel = pd.read_excel(upc_file_path, sheet_name=None, header=header_row_guess)
    upc_df = pd.concat(upc_excel.values(), ignore_index=True)
    partner_df = pd.read_excel(partner_file_path)

    upc_df.columns = [col.lower().strip() for col in upc_df.columns]
    partner_df.columns = [col.lower().strip() for col in partner_df.columns]

    desc_col = 'title' if 'title' in upc_df.columns else 'description' if 'description' in upc_df.columns else upc_df.columns[1]
    upc_col = next((col for col in ['gtin', 'upc', 'barcode'] if col in upc_df.columns), upc_df.columns[0])
    brand_col = 'brand' if 'brand' in upc_df.columns else None
    cat_col = next((col for col in upc_df.columns if upc_df[col].astype(str).str.contains('>').any()), None)

    upc_df[upc_col] = (
        upc_df[upc_col]
        .astype(str)
        .str.replace(r'[^\d]', '', regex=True)
    )
    partner_df['barcode'] = (
        partner_df['barcode']
        .astype(str)
        .str.extract(r'(\d+)', expand=False)
        .fillna('')
    )

    existing = set(partner_df['barcode'])
    upc_df['STATUS'] = upc_df[upc_col].apply(lambda x: 'Existing' if x in existing else 'New')
    new_df = upc_df[upc_df['STATUS'] == 'New'].copy()

    def extract_size_and_count(desc):
        desc = str(desc).lower()
        size_match = re.search(r'(\d+(\.\d+)?)\s?(oz|fl oz|l|ml|gallon|gal)', desc)
        count_match = re.search(r'(\d+)\s?ct', desc)
        return pd.Series({
            'sizevalue': size_match.group(1) if size_match else None,
            'sizemeasure': size_match.group(3).upper() if size_match else None,
            'itemcountvalue': count_match.group(1) if count_match else None,
            'itemcountmeasure': 'CT' if count_match else None
        })

    size_data = new_df[desc_col].apply(extract_size_and_count)
    new_df = pd.concat([new_df, size_data], axis=1)

    if cat_col:
        cats = new_df[cat_col].str.split('>', expand=True)
        new_df['ch1department'] = cats[0].str.strip().fillna("N/A") if 0 in cats else "N/A"
        new_df['ch2category'] = cats[1].str.strip().fillna("N/A") if 1 in cats else "N/A"
        new_df['ch3segment'] = cats[2].str.strip().fillna("N/A") if 2 in cats else "N/A"
    else:
        new_df['ch1department'] = "N/A"
        new_df['ch2category'] = "N/A"
        new_df['ch3segment'] = "N/A"

    output = pd.DataFrame({
        'barcode': new_df[upc_col],
        'bh2brand': new_df[brand_col].str.upper() if brand_col else "N/A",
        'name': new_df[desc_col],
        'description': new_df[desc_col],
        'ch1department': new_df['ch1department'],
        'ch2category': new_df['ch2category'],
        'ch3segment': new_df['ch3segment'],
        'itemcountvalue': new_df['itemcountvalue'],
        'itemcountmeasure': new_df['itemcountmeasure'],
        'sizevalue': new_df['sizevalue'],
        'sizemeasure': new_df['sizemeasure'],
        'partnerproduct': 'Y',
        'awardpoints': 'N'
    })

    for col in partner_df.columns:
        if col not in output.columns:
            output[col] = None
    output = output[partner_df.columns]

    return output
