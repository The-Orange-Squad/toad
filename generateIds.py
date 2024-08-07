import csv
import uuid
import sys

def generate_ids(input_file, output_file):
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        
        if 'ID' not in fieldnames:
            fieldnames.insert(0, 'ID')
        
        rows = []
        for row in reader:
            if not row.get('ID'):
                row['ID'] = str(uuid.uuid4())
            rows.append(row)
    
    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generateIds.py input_file.csv output_file.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_ids(input_file, output_file)
    print(f"UUIDs generated. Output saved to {output_file}")