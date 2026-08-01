import pandas as pd


def load_statement(filepath: str) -> pd.DataFrame:
    """Load a bank CSV and normalize it to our standard schema:
    date, description, amount (negative = money out)"""
    df = pd.read_csv(filepath)

    df = df.rename(columns={"Date": "date", "Description": "description", "Amount": "amount"})

    df = df[["date", "description", "amount"]]
    return df


if __name__ == "__main__":
    df = load_statement("data/test_statement.csv")
    print(df)
    print("\nColumn types:")
    print(df.dtypes)
