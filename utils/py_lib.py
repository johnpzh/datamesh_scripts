import os


def check_is_data(node: str, attr: dict):
    if "abspath" in attr:
        return True

    ext = os.path.splitext(node)[1]
    if ext in [".vcf", ".gz", ".txt", ".h5", ".dcd", ".pt", ".pdb", ".json"]:
        return True

    return False
