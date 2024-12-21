import os
import shutil

def copy_files_in_sequence(source_dir, target_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    
    files = [f for f in os.listdir(source_dir) if f.endswith('.json')]
    files.sort(key=lambda x: int(x.split('.')[0]))

    for i, file in enumerate(files):
        source_path = os.path.join(source_dir, file)
        target_path = os.path.join(target_dir, f'{i}.json')
        shutil.copy(source_path, target_path)
        print(f'Скопирован файл {source_path} в {target_path}')

source_directory = 'data_time'
target_directory = 'data'
copy_files_in_sequence(source_directory, target_directory)