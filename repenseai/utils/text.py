import re
from difflib import SequenceMatcher
from string import digits, punctuation, whitespace
from typing import List, Union

from unidecode import unidecode


def format_time_diff(time_diff: int) -> str:
    if time_diff >= 3600:
        return f"{(time_diff / 3600):.4f}h"
    elif time_diff >= 60:
        return f"{(time_diff / 60):.4f}min"
    else:
        return f"{(time_diff):.4f}s"


def similarity_index(str1, str2):
    seq_sim = SequenceMatcher(None, str1, str2).ratio()

    str1_words = set(str1.split())
    str2_words = set(str2.split())

    word_sim = len(str1_words.intersection(str2_words)) / len(
        str1_words.union(str2_words)
    )

    return 0.5 * seq_sim + 0.5 * word_sim


def extract_json_text(runions_text: str) -> str:
    try:
        try:
            pattern = r"(?<=```\n)([\s\S]*?)(?=\n```)"
            json_text = re.search(pattern, runions_text).group(0)
        except Exception:
            pattern = r"(?<=```json\n)([\s\S]*?)(?=\n```)"
            json_text = re.search(pattern, runions_text).group(0)
    except Exception:
        return runions_text

    return json_text


def to_lower(text: str) -> str:
    """
    replaces all letters to lower format
    """
    return text.lower()


def remove_accents(text: str) -> str:
    """
    replaces accented letters for normal ones
    """
    return unidecode(text)


def remove_digits(text: str) -> str:
    """
    removes digits
    """
    return text.translate(str.maketrans("", "", digits))


def remove_punctuation(text: str, custom_punctuation: str = "´¨") -> str:
    """
    replaces puctuation with whitespace
    """
    punctuation_tags = punctuation + custom_punctuation
    len_tags = " " * len(punctuation_tags)

    return text.translate(str.maketrans(punctuation_tags, " " * len(len_tags)))


def clean_whitespaces(text: str) -> str:
    """
    replaces whitespace characteres like "\n" with a whitespace
    corrects more than one whitespace
    removes whitespace from first and last characteres
    """

    whitespace_tags = whitespace.replace(" ", "") + "\x01"
    len_tags = " " * len(whitespace_tags)

    text_no_tags = text.strip().translate(str.maketrans(whitespace_tags, len_tags))

    whitespace_equalizer = re.compile(r"\s+")

    return whitespace_equalizer.sub(" ", text_no_tags)


def return_text(text: str) -> str:
    """
    just return the same text without any transformation
    """
    return text


def adjust_abbreviations(
    text: str, abbreviations_list: List[str], replacement_list: List[str]
) -> str:
    """
    just return the same text without any transformation
    """

    for abbreviation, replacement in zip(abbreviations_list, replacement_list):
        text = text.replace(abbreviation, replacement)

    return text


def clean_text(text: str, steps: Union[str, List[str]] = "all") -> str:
    """
    removes accents, punctuation, digits and makes text lowercase
    """

    steps_dict = {
        "lower": to_lower,
        "remove_accents": remove_accents,
        "remove_punctuation": remove_punctuation,
        "remove_digits": remove_digits,
        "clean_whitespaces": clean_whitespaces,
    }

    if isinstance(steps, list):
        for step in steps:
            text = steps_dict.get(step, return_text)(text)

    elif steps == "all":
        for step in steps_dict.values():
            text = step(text)

    else:
        raise Exception("Please, check the provided steps!")

    return text


def extract_digits(text: str) -> str:
    return "".join(filter(str.isdigit, text))
