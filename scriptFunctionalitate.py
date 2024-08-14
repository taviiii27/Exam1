import os

backup_folder = 'backup_intrari'
folder_entries = 'intrari'

if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)
    print(f"Folder de backup creat: {backup_folder}")
else:
    print(f"Folderul de backup există deja: {backup_folder}")

if not os.path.exists(folder_entries):
    os.makedirs(folder_entries)
    print(f"Folder pentru intrări creat: {folder_entries}")
else:
    print(f"Folderul pentru intrări există deja: {folder_entries}")

files_data = {
    'Poarta1.csv': [
        '2024-08-13 08:00:00',
        '2024-08-13 09:30:00',
        '2024-08-13 12:00:00',
        '2024-08-13 15:45:00',
    ],
    'Poarta2.txt': [
        '2024-08-13 10:00:00',
        '2024-08-13 11:30:00',
        '2024-08-13 13:15:00',
        '2024-08-13 17:00:00',
    ],
}

for file_name, lines in files_data.items():
    file_path = os.path.join(folder_entries, file_name)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            for line in lines:
                file.write(f"{line}\n")
        print(f"Fișier creat: {file_path}")
