import glob
import os
import re
import shutil

import fire


def convert_tex_delimiters(text):
    # Define regular expression patterns to match single and double dollar signs, and equation environment syntax
    single_dollar_pattern = r"(?<!\\)\$(.*?)(?<!\\)\$"
    double_dollar_pattern = r"\$\$(.*?)\$\$"

    replaced_text = text
    replaced_text = re.sub(
        double_dollar_pattern, r"\\\[\1\\\]", replaced_text, flags=re.DOTALL
    )
    replaced_text = re.sub(
        single_dollar_pattern, r"\\\(\1\\\)", replaced_text, flags=re.DOTALL
    )
    replaced_text = replaced_text.replace("\\\n", "\\\\\n")

    return replaced_text


def main(filepath: str):
    parent_dir = os.path.dirname(filepath)

    img_dir = os.path.join(parent_dir, "images")
    images = glob.glob(os.path.join(img_dir, "*"))

    with open(filepath) as f:
        contents = f.read()

    x = contents.split("---")
    title = x[0]
    cards = x[1:]

    converted = [title]
    for card in cards:
        card = (
            card.replace("##", "###").replace("**Que:**", "##").replace("**Ans:** ", "")
        )
        # move frontmatter like tags to end
        try:
            front_idx = card.index("##")
            if front_idx > 0:
                old_front = card[:front_idx]
                card = card[front_idx:] + old_front
        except ValueError:
            pass

        card = card.replace("images/", "")
        card = convert_tex_delimiters(card)
        converted.append(card)

    for img in images:
        new_path = img.replace("images/", "")
        shutil.move(img, new_path)

    os.remove(filepath)
    new_file = filepath
    with open(new_file, "w") as f:
        f.writelines(converted)


if __name__ == "__main__":
    fire.Fire(main)
