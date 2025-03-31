from returns.result import Result, Success, Failure
import pandas as pd
from typing import List

def extract_urls_from_csv(file_path: str, column_name: str) -> Result[List[str], Exception]:
    """
    Extracts URLs from a specified column in a CSV file.

    :param file_path: Path to the CSV file.
    :param column_name: Name of the column containing URLs.
    :return: A Result containing a list of URLs or an Exception in case of failure.
    """
    try:
        if column_name not in pd.read_csv(file_path).columns:
            raise ValueError(f"Column '{column_name}' not found in the CSV file.")
        return Success(pd.read_csv(file_path)[column_name].dropna().tolist())
    except Exception as e:
        return Failure(e)


# Example usage
if __name__ == "__main__":

    result = extract_urls_from_csv("SRC/back_end/web_scrapping/Makro/Makro_URLs.csv", "URL")

    if isinstance(result, Success):
        print("Extracted URLs:", result.unwrap())
    else:
        print("Error:", result.failure())