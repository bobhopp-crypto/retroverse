import os
import re

# folder containing images
img_dir = "public/images"

# html file
html_file = "public/magazine/1978.html"

# mapping old → new
mapping = {
"1978_raw_02.png":"shadow_dancing.png",
"1978_raw_03.png":"hot_child_in_the_city.png",
"1978_raw_04.png":"kiss_you_all_over.png",
"1978_raw_05.png":"night_fever.png",
"1978_raw_06.png":"boogie_oogie_oogie.png",
"1978_raw_07.png":"lay_down_sally.png",
"1978_raw_08.png":"youre_the_one_that_i_want.png",
"1978_raw_09.png":"love_is_thicker_than_water.png",
"1978_raw_10.png":"i_love_the_nightlife.png",
"1978_raw_A.png":"stayin_alive.png",
"1978_raw_J.png":"sultans_of_swing.png",
"1978_raw_K.png":"baker_street.png",
"1978_raw_Q.png":"roll_with_the_changes.png",
"1978_raw_R1.png":"recap_11_20.png",
"1978_raw_R2.png":"recap_21_30.png",
"1978_raw_R3.png":"recap_31_40.png",
"1978_raw_R4.png":"year_overview.png"
}

# rename image files
for old,new in mapping.items():
    old_path=os.path.join(img_dir,old)
    new_path=os.path.join(img_dir,new)

    if os.path.exists(old_path):
        os.rename(old_path,new_path)

# update HTML references
with open(html_file,"r") as f:
    html=f.read()

for old,new in mapping.items():
    html=html.replace(old,new)

with open(html_file,"w") as f:
    f.write(html)

print("Images renamed and HTML updated.")