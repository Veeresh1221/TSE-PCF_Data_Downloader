import pandas as pd

import glob
import logging
from include.operations.logger_file import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
def summeryCategorizer(one_file):
    final_columns = ['ETF Code', 'ETF Name', 'Cash & Others', 'Shares Outstanding', 'Fund Date', 'AUM', 'DT']
    column_mappings = {
        'Fund Cash Component': 'Cash & Others',
        'AUM': 'AUM'
    }
    sql_column_mappings = {
        'ETF Code': 'etf_code',
        'ETF Name': 'etf_name',
        'Cash & Others': 'cash_oth',
        'Shares Outstanding': 'outstanding',
        'Fund Date': 'fund_date',
        'AUM': 'amount',
        'DT': 'dt'
    }
    rows = []

    try:
        df = pd.read_csv(one_file, encoding='unicode_escape', on_bad_lines='skip')

        # Standardize column names
        df.rename(columns={**column_mappings, **{col: col for col in df.columns if col in final_columns}}, inplace=True)

        if df.shape[0] > 0:
            first_row = df.iloc[0].to_dict()
            standardized_row = {sql_column_mappings.get(col, col): first_row.get(col, pd.NA) for col in final_columns}

            # Append the standardized row
            rows.append(standardized_row)

    except (pd.errors.ParserError, FileNotFoundError, pd.errors.EmptyDataError) as e:
        logger.error(f"Error processing file {one_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing file {one_file}: {e}")

    # Create a DataFrame from the rows
    df = pd.DataFrame(rows, columns=sql_column_mappings.values())
    pd.set_option('future.no_silent_downcasting', True)

    # Ensure 'amount' and other numeric columns are not null
    numeric_columns = ['cash_oth', 'outstanding', 'amount', 'dt']
    df[numeric_columns] = df[numeric_columns].fillna(0)

    df.dropna(how='all', inplace=True)
    return df

def detailsCategorizer(one_file, summary_df):
    final_columns = ['CODE', 'NAME', 'ISIN', 'EXCHANGE', 'CURRENCY', 'SHARES AMOUNT', 'STOCK PRICE']
    column_mappings = {
        'ISIN': 'ISIN',
        'SHARES': 'SHARES AMOUNT',
        'STOCK PRICE': 'STOCK PRICE'
    }
    sql_column_mappings = {
        'ETF Code': 'etf_code',
        'CODE': 'code',
        'NAME': 'name',
        'ISIN': 'istn',
        'EXCHANGE': 'exchange',
        'CURRENCY': 'currency',
        'SHARES AMOUNT': 'shere_amount',
        'STOCK PRICE': 'stock_price'
    }
    unwanted_phrases = [
        "Nomura Asset Management Co., Ltd. does not assure that the material is accurate, current or complete and it should not be relied on as such.",
        "Nomura Asset Management Co., Ltd. is not liable for any kind of loss or damage that may be suffered or claimed by a user of this file in con",
        "Disclaimer",
        "By accessing the PCF, you agree not to reproduce, distribute or disseminate the PCF, in whole or in part, in any form without prior written ",
        "You agree (i) to use the PCF solely for the purposes of creating or redeeming shares of the relevant Funds; (ii) not to redistribute the PCF",
        "By accessing the PCF, you agree not to reproduce, distribute or disseminate the PCF, in whole or in part, in any form without prior written "   ]
    rows = []
    try:
        df = pd.read_csv(one_file, encoding='unicode_escape', skiprows=3)
        df.columns = df.columns.str.strip().str.upper()

        # Remove rows containing unwanted phrases
        for phrase in unwanted_phrases:
            df = df[~df.apply(lambda row: row.astype(str).str.contains(phrase, case=False, na=False, regex=False).any(), axis=1)]

        # Drop rows where both CODE and NAME are empty
        df.dropna(subset=['CODE', 'NAME'], how='all', inplace=True)

        # Assign NAME to CODE if CODE is missing
        df['CODE'] = df.apply(lambda row: row['NAME'] if pd.isna(row['CODE']) else row['CODE'], axis=1)
        matched_columns = [col for col in final_columns if col in df.columns]

        if set(matched_columns).issubset(df.columns):
            df.rename(columns={col.upper(): mapped_col.upper() for col, mapped_col in column_mappings.items()}, inplace=True)
            df = df.reindex(columns=final_columns)

            # Convert 'CODE' from float to integer
            df['CODE'] = df['CODE'].astype(str).replace(r'\.0$', '', regex=True)

            pd.set_option('future.no_silent_downcasting', True)

            for col in df.columns:
                if df[col].dtype not in ['float64', 'int64']:
                    df[col] = df[col].replace({'nan': pd.NA, '': pd.NA})
                else:
                    df[col] = df[col].fillna(0)

            if not summary_df.empty:
                df['ETF Code'] = summary_df['etf_code'].iloc[0]
            df.replace('nan', pd.NA, inplace=True)
            rows.extend(df.to_dict(orient='records'))

    except (pd.errors.ParserError, FileNotFoundError, pd.errors.EmptyDataError, KeyError) as e:
        logger.error(f"Error processing file {one_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing file {one_file}: {e}")

    df = pd.DataFrame(rows)
    df.rename(columns=sql_column_mappings, inplace=True)
    df.dropna(how='all', inplace=True)
    return df

def categorize(extracted_folder):
    summary_dfs = []
    detail_dfs = []

    for one_file in glob.glob(f'{extracted_folder}/*.csv'):
        summary_df = summeryCategorizer(one_file)
        detail_df = detailsCategorizer(one_file, summary_df)
        summary_dfs.append(summary_df)
        detail_dfs.append(detail_df)

    full_summary_df = pd.concat(summary_dfs, ignore_index=True)
    full_detail_df = pd.concat(detail_dfs, ignore_index=True)
    return full_summary_df ,full_detail_df
