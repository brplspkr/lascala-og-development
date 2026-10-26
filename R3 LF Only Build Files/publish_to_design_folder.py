from pathlib import Path
import shutil
source=Path(__file__).resolve().parent
target=source.parent
names=['LaScala_OG_LF_Only_R3.FCStd', 'LaScala_OG_LF_Only_R3_Cabinet.step', 'LaScala_OG_LF_Only_R3_Full_Assembly.step', 'LaScala_OG_LF_Only_R3_assembled.png', 'LaScala_OG_LF_Only_R3_cutaway.png']
for name in names:
    shutil.copy2(source/name,target/name)
shutil.copy2(source/'R3_LF_Only_Notes.txt',target/'LaScala_OG_LF_Only_R3_Notes.txt')
print(target)
