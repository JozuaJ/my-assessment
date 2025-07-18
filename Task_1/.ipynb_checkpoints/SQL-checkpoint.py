"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)


NOTE:
Each question in this section is isolated, for example, you do not need to consider how Q5 may affect Q4.
Remember to clean your data.

"""


def question_1():
    """
    Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    Return the `Name`, `Surname` and `CustomerID`
    """


    qry = """
        SELECT Name, Surname, CustomerID 
        FROM customers
        GROUP BY Name, Surname, CustomerID
        HAVING COUNT(CustomerID) > 1
        """

    # In this query, I simply select the required columns where the CustomerIDs appear more than once. The solution makes sense as it retrieves 14 entries, out of the 1014 entries in the table, and the CustomerIDs go to 1000. Also, running a quick check, all the duplicate customer ids have the entire entry duplicated.

    return qry


def question_2():
    """
    Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income
    """

    qry = """
        SELECT DISTINCT Name, Surname, Income
        FROM customers
        WHERE Gender = 'Female'
        ORDER BY Income DESC
        """

    # I used DISTINCT to remove any duplicate rows in the result
    
    return qry


def question_3():
    """
    Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    ie 50 not 0.5
    There is only 1 loan per customer ID.
    """

    qry = """
        WITH unique_loans AS (
            SELECT DISTINCT CustomerID, LoanTerm, ApprovalStatus
            FROM loans
        )
        SELECT LoanTerm,
            ROUND(100.0 * SUM(IF(ApprovalStatus = 'Approved', 1, 0)) / COUNT(*),2) AS ApprovedPercentage
            FROM unique_loans
            GROUP BY LoanTerm
            ORDER BY LoanTerm
        """

    # There are once again duplicate entries in the table. So, I created a temporary table with all the unique entries first, before doing the calculations.
    # Doing the same checks as above, the duplicate entries are entirely duplicated, so there won't be any problems with entries with the same CustomerIDs being slightly different
    
    return qry


def question_4():
    """
    Return a breakdown of the number of customers per CustomerClass in the credit data
    Return columns `CustomerClass` and `Count`
    """

    qry = """
        WITH unique_credit AS (
            SELECT DISTINCT CustomerID, CustomerClass
            FROM credit
        )
        SELECT CustomerClass, Count(*) AS Count
            FROM unique_credit
            GROUP BY CustomerClass
            ORDER BY Count DESC
        """

    # Similar to before, there are duplicate entries in the credit table.
    
    return qry


def question_5():
    """
    Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.
    """

    qry = """
        UPDATE credit
        SET CustomerClass = 'C'
        WHERE CreditScore BETWEEN 600 AND 650
        """

    return qry
