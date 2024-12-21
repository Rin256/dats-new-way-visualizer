import os
import shutil

def copy_files_in_sequence(source_dir, target_dir):
    # Получаем список всех файлов с расширением .json в исходном каталоге
    files = [f for f in os.listdir(source_dir) if f.endswith('.json')]
    
    # Сортируем файлы по имени, чтобы они шли от минимального числа
    files.sort(key=lambda x: int(x.split('.')[0]))

    # Копируем файлы в целевой каталог с последовательной нумерацией
    for i, file in enumerate(files):
        source_path = os.path.join(source_dir, file)
        target_path = os.path.join(target_dir, f'{i}.json')
        shutil.copy(source_path, target_path)
        print(f'Скопирован файл {source_path} в {target_path}')

# Указываем исходный и целевой каталоги
source_directory = 'data_time'
target_directory = 'data_sequence'

# Проверка, существует ли целевой каталог, если нет - создаем
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

# Копируем файлы
copy_files_in_sequence(source_directory, target_directory)