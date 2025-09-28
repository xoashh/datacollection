import secrets

def generate_api_key():
    return secrets.token_urlsafe(16)

def add_key_to_api_file(key, buyer_name, api_file='selling_api.py'):
    # Load the current API_KEYS section
    with open(api_file, 'r') as f:
        lines = f.readlines()

    # Find the API_KEYS dictionary and add the new key before the closing }
    for i, line in enumerate(lines):
        if line.strip().startswith("API_KEYS"):
            # Find the closing brace
            for j in range(i, len(lines)):
                if lines[j].strip().startswith("}"):
                    # Insert new key before closing brace
                    lines.insert(j, f'    "{key}": "{buyer_name}",\n')
                    break
            break

    # Save the file
    with open(api_file, 'w') as f:
        f.writelines(lines)
    print(f"Added key for buyer '{buyer_name}' to {api_file}")

if __name__ == "__main__":
    buyer_name = input("Enter buyer name: ")
    key = generate_api_key()
    print(f"Generated API key for {buyer_name}: {key}")
    add = input("Add key directly to selling_api.py? (y/n): ").strip().lower()
    if add == 'y':
        add_key_to_api_file(key, buyer_name)
    else:
        print("Copy and add this line to API_KEYS in selling_api.py:")
        print(f'    "{key}": "{buyer_name}",')
