import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 1 default definition.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """

    # Find all of the loans that fulfill the Type 1 default criteria
    defaulted_loans = df_balances.groupby("LoanID").apply(
        lambda group: (group["ActualRepayment"] < group ["ScheduledRepayment"]).any()
    )

    # Find the total number of Type 1 defaulted loans
    num_defaulted = defaulted_loans.sum()
    # Find the total number of unique loans
    total_loans = defaulted_loans.shape[0]

    # Calculate the percentage of Type 1 defaulted loans
    default_rate_percent = (num_defaulted / total_loans) * 100

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 2 default definition

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """

    # Assign Year1 (months 1–12) or Year2 (months 13–24), since all loans have a loan term of 2 years
    df_balances["Year"] = df_balances["Month"].apply(lambda m: 1 if m <= 12 else 2)

    # Group by LoanID and Year to compute total scheduled and actual repayments per year (Aggregate)
    grouped = df_balances.groupby(["LoanID", "Year"]).agg({
        "ScheduledRepayment": "sum",
        "ActualRepayment": "sum"
    }).reset_index()

    # Calculate unpaid percentage also avoiding division by 0
    grouped["PercentUnpaid"] = grouped.apply(
        lambda row: ((row["ScheduledRepayment"] - row["ActualRepayment"]) / row["ScheduledRepayment"])
        if row["ScheduledRepayment"] > 0 else 0,
        axis=1
    )

    # Identify Type 2 default (unpaid percentage > 15%)
    grouped["Type2DefaultYear"] = grouped["PercentUnpaid"] > 0.15

    # A loan defaults if any of its years has a Type 2 default
    loan_defaults = grouped.groupby("LoanID")["Type2DefaultYear"].any()

    # Calculate the Type 2 default rate
    default_rate_percent = (loan_defaults.sum() / loan_defaults.count()) * 100

    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """

    # Make a copy of the dataframe to avoid modifying the original
    df = df_balances.copy()
    
    # Step 1: Calculate Scheduled Principal and Actual Principal
    # Calculate the Scheduled Principal portion for each repayment
    df["ScheduledPrincipal"] = df["ScheduledRepayment"] - df["InterestPayment"]
    # Calculate the Actual Principal paid
    df["ActualPrincipal"] = df["LoanBalanceStart"] - df["LoanBalanceEnd"]
    # Calculate the Unscheduled Principal
    df["UnscheduledPrincipal"] = df["ActualPrincipal"] - df["ScheduledPrincipal"]

    # Step 2: Calculate SMM
    # Remove rows where LoanBalanceStart is 0 or less (to avoid division by 0)
    df = df[df["LoanBalanceStart"] > 0]
    
    df["SMM"] = df["UnscheduledPrincipal"] / df["LoanBalanceStart"]

    # Step 3: Remove invalid SMM values (e.g., negative or nan)
    df = df[df["SMM"].notna() & (df["SMM"] >= 0)]

    # In case there remains no valid data after filtering
    if df.empty:
        return 0.0
    
    # Step 4: Calculate SMM_mean
    # ∏(1+SMM)
    smm_product = np.prod(1 + df["SMM"])
    #(∏(1+SMM))^(1/12) - 1
    smm_mean = smm_product**(1 / len(df)) - 1

    # Step 5: Calculate CPR
    cpr = 1 - (1 - smm_mean)**12
    cpr_percent = cpr * 100

    return cpr_percent


def question_4(df_scheduled, df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """

    # Step 1: Use Type 2 probability of default, as it reflects long-term cumulative risk of non-payment and potentially material financial distress from the customer. Type 1 probability of default only captures a single missed payment, which is short-term and could be rectified in the following month's payment.
    pd_percent = question_2(df_scheduled, df_balances)
    pd_decimal = pd_percent / 100

    # Step 2: Get only the balances at the end of the first year, and calculate the total exposure by adding the loan balances at the end of the that month (i.e. the end of year 1 and the start of year 2)
    year_2_balances = df_balances[df_balances["Month"] == 12]
    total_exposure = year_2_balances["LoanBalanceEnd"].sum()

    # Step 3: Recovery rate (Assumed 80%)
    recovery_rate = 0.80

    # Step 4: Calculate predicted loss
    total_loss = pd_decimal * total_exposure * (1 - recovery_rate)

    return total_loss
