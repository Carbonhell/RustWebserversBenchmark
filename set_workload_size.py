import sys
import os
import shutil

def main():
    if len(sys.argv) < 2 or int(sys.argv[1]) not in (1,2,3):
        print(f"Usage: {sys.argv[0]} SIZE")
        print("Allowed SIZE values:")
        print("1: Small (sets \"prototype_kilogram.jpg\" size to ~95KB, equal to \"prototype_kilogram_small.jpg\")")
        print("2: Medium (sets \"prototype_kilogram.jpg\" size to ~1MB, equal to \"prototype_kilogram_medium.jpg\")")
        print("2: Large (sets \"prototype_kilogram.jpg\" size to ~3MB, equal to \"prototype_kilogram_large.jpg\")")
        exit()
    target_dir = os.path.join(".", "static", "img")
    target_file = os.path.join(target_dir, "prototype_kilogram.jpg")
    if not os.path.exists(target_file):
        print("This script must be located next to the static folder along with the image files for each setting to work.")
        print("To generate the files, copy \"prototype_kilogram.jpg\" from the img folder to the folder containing this script, and use the \"truncate\" utility to adjust the file size for each setting.")
        exit()
    
    op = int(sys.argv[1])
    if op == 1:
        print("Setting size to: Small")
        shutil.copy("prototype_kilogram_small.jpg", target_file)
    elif op == 2:
        print("Setting size to: Medium")
        shutil.copy("prototype_kilogram_medium.jpg", target_file)
    elif op == 3:
        print("Setting size to: Large")
        shutil.copy("prototype_kilogram_large.jpg", target_file)
        
if __name__ == '__main__':
    main()