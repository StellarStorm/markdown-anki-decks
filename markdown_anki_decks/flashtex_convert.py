import glob
import os
import re
import shutil

import fire
import mdformat


def convert_tex_delimiters(text: str) -> str:
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


def remove_img_resize(text: str) -> str:
    pattern = r"!\[\]\((.*?)\s*=\s*\d+x\d+\)"
    return re.sub(pattern, r"![](\1)", text)


def _increase_level(match):
    return match.group(0) + "#"


def reformat_card(text: str) -> str:
    """
    Change format to something like

    ## Question
    answer line 1
    answer line 2
    **Ref:** reference if any
    **Tags:** tags if any
    **ID:** card id if any
    """

    pattern = (
        r"\*\*(Que|Ans|Ref|Tags|ID):\*\*\s*(.*?)\s*(?=\*\*(Que|Ans|Ref|Tags|ID)|$)"
    )
    matches = re.findall(pattern, text, flags=re.DOTALL)
    card_values = {}
    for match in matches:
        key = match[0]
        value = match[1]
        card_values[key] = value

    new_format = f"## {card_values['Que']}\n\n{card_values['Ans']}\n\n"
    for optional_tag in ["Ref", "Tags", "ID"]:
        if card_values.get(optional_tag) is not None:
            new_format = (
                f"{new_format}**{optional_tag}:** {card_values[optional_tag]}\n\n"
            )
    return new_format


def main(filepath: str) -> None:
    parent_dir = os.path.dirname(filepath)

    img_dir = os.path.join(parent_dir, "images")
    images = glob.glob(os.path.join(img_dir, "*"))

    with open(filepath) as f:
        contents = f.read()

    title = re.findall(r"^# .*$", contents, re.MULTILINE)[0]
    cards = re.findall(r"---\n(.*?)(?=---\n|\Z(?!.*\n))", contents, re.DOTALL)
    if cards[-1] == r"":
        cards = cards[:-1]

    converted = [title + "\n\n"]
    for card in cards:
        card = re.sub(r"#+", _increase_level, card)
        card = card.replace("images/", "")
        card = reformat_card(card)
        card = convert_tex_delimiters(card)
        card = remove_img_resize(card)

        converted.append(card)

    for img in images:
        new_path = img.replace("images/", "")
        shutil.move(img, new_path)

    os.remove(filepath)
    new_file = filepath
    with open(new_file, "w") as f:
        f.writelines(converted)
    mdformat.file(filepath)


if __name__ == "__main__":
    fire.Fire(main)
