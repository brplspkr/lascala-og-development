from pathlib import Path
import shutil
source=Path(__file__).resolve().parent
target=source.parent
names=['LaScala_OG_1977_R2.FCStd', 'LaScala_OG_1977_R2_Cabinet.step', 'LaScala_OG_1977_R2_With_Reference_Drivers.step', 'LaScala_OG_R2_assembled.png', 'LaScala_OG_R2_cutaway.png']
for name in names:
    shutil.copy2(source/name,target/name)
shutil.copy2(source/'R2_Review_Notes.txt',target/'LaScala_OG_1977_R2_Review_Notes.txt')
print(target)
