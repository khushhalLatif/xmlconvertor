import os
import xml.etree.ElementTree as ET
import polars as pl

output_file = "output"
final_data = []
cols = ["Merchant Id", "Store Number", "GPR-Purchase Count", "GPR-Purchase Amount", "GPR-Purchase Charge Purchase Count", "GPR-Purchase Charge Purchase Amount", "GPR-Load Count", "GPR-Load Amount", "GPR-Purchase Charge Load Count", "GPR-Purchase Charge Load Amount", "GPR-Return Count", "GPR-Return Amount", "GPR-Commissions Paid Merchant Count", "GPR-Commissions Paid Merchant Amount", "GPR-Commissions Paid Program Owner Count", "GPR-Commissions Paid Program Owner Amount", "GPR-Commissions Paid FDC Count", "GPR-Commissions Paid FDC Amount", "GPR Liability-Commissions Disbursement Count", "GPR Liability-Commissions Disbursement Amount", "GPR-Liability Count", "GPR-Liability Amount", "GO Tag-Purchase Count", "GO Tag-Purchase Amount", "GO Tag-Purchase Charge Purchase Count", "GO Tag-Purchase Charge Purchase Amount", "GO Tag-Load Count", "GO Tag-Load Amount", "GO Tag-Purchase Charge Load Count", "GO Tag-Purchase Charge Load Amount", "GO Tag-Return Count", "GO Tag-Return Amount", "GO Tag-Commissions Paid Merchant Count", "GO Tag-Commissions Paid Merchant Amount", "GO Tag-Commissions Paid Program Owner Count", "GO Tag-Commissions Paid Program Owner Amount", "GO Tag-Commissions Paid FDC Count", "GO Tag-Commissions Paid FDC Amount", "GO Tag Liability-Commissions Disbursement Count", "GO Tag Liability-Commissions Disbursement Amount", "GO Tag-Liability Count", "GO Tag-Liability Amount", "Everywhere Card-Purchase Count", "Everywhere Card-Purchase Amount", "Everywhere Card-Purchase Charge Purchase Count", "Everywhere Card-Purchase Charge Purchase Amount", "Everywhere Card-Load Count", "Everywhere Card-Load Amount", "Everywhere Card-Purchase Charge Load Count", "Everywhere Card-Purchase Charge Load Amount", "Everywhere Card-Return Count", "Everywhere Card-Return Amount", "Everywhere Card-Commissions Paid Merchant Count", "Everywhere Card-Commissions Paid Merchant Amount", "Everywhere Card-Commissions Paid Program Owner Count", "Everywhere Card-Commissions Paid Program Owner Amount", "Everywhere Card-Commissions Paid FDC Count", "Everywhere Card-Commissions Paid FDC Amount", "Everywhere Card Liability-Commissions Disbursement Count", "Everywhere Card Liability-Commissions Disbursement Amount", "Everywhere Card-Liability Count", "Everywhere Card-Liability Amount", "Manual Adjustments Count", "Manual Adjustments Amount", "ACH Returns Count", "ACH Returns Amount", "ACH Rejects Count", "ACH Rejects Amount", "Not Settled Count", "Not Settled Amount", "Total Activity Count", "Total Activity Amount"]

template = {col: 0 for col in cols}

def process_xml_file(file_path):
    temp_template = template.copy()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            xml_content = f.read()
        
        wrapped_xml = f"<FakeRoot>{xml_content}</FakeRoot>"
        root = ET.fromstring(wrapped_xml)
        
        print(f"Processing: {file_path}")
        for item in root.findall("ValueLinkLineItem"):
            data = extract_data(item)
            print(data)
            temp_template["Merchant Id"] = data["Merchant Number"]
            temp_template["Store Number"] = data["Alt Merchant Number"]
            temp_template[data["Category"]+" Count"] += data["Count"]
            temp_template[data["Category"]+" Amount"] += data["Amount"]
        
        for key in temp_template:
            if "Amount" in key:
                temp_template[key] = int(temp_template[key] / 100)
        final_data.append(temp_template)
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")

def extract_data(item):
    amount_elem = item.find("amount/FSNDollarUS")
    merchant_number = item.find("merchantNumber").text
    alt_merchant_number = item.find("altMerchantNumber").text
    amount = amount_elem.attrib.get("amount", "0") if amount_elem is not None else "0"
    category = item.find("category").text if item.find("category") is not None else "N/A"
    count = item.find("count").text if item.find("count") is not None else "0"
    return {
        "Merchant Number": merchant_number,
        "Alt Merchant Number": alt_merchant_number,
        "Amount": int(amount),
        "Category": category,
        "Count": int(count)
    }

def main():
    input_folder = "input"
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return

    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):
            file_path = os.path.join(input_folder, filename)
            process_xml_file(file_path)

    df = pl.DataFrame(final_data)
    df.write_csv(f"{output_file}.csv")

if __name__ == "__main__":
    main()
