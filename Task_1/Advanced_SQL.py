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
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """
        WITH unique_customers AS (
            SELECT DISTINCT CustomerID, Income
            FROM customers
        ),
        unique_credit AS (
            SELECT DISTINCT CustomerID, CustomerClass
            FROM credit
        )
        SELECT cr.CustomerClass, ROUND(AVG(cu.Income),2) AS AverageIncome
            FROM unique_credit AS cr
            INNER JOIN unique_customers cu ON cr.CustomerID = cu.CustomerID
            GROUP BY cr.CustomerClass
        """

    # Since the database has duplicate entries for both tables, I first created temporary tables which doesn't have the duplicated entries.
    # I then calculated the average income per CustomerClass, rounding to 2 decimal places.
    
    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """
        WITH unique_customers AS (
            SELECT DISTINCT CustomerID,
                CASE
                    WHEN Region = 'EasternCape' THEN 'EC'
                    WHEN Region = 'WesternCape' THEN 'WC'
                    WHEN Region = 'NorthernCape' THEN 'NC'
                    WHEN Region = 'FreeState' THEN 'FS'
                    WHEN Region = 'KwaZulu-Natal' THEN 'KZN'
                    WHEN Region = 'Gauteng' THEN 'GT'
                    WHEN Region = 'Limpopo' THEN 'LP'
                    WHEN Region = 'Mpumalanga' THEN 'MP'
                    WHEN Region = 'NorthWest' THEN 'NW'
                    ELSE Region
                END AS StandardizedRegion
            FROM customers
        ),
        unique_loans AS (
            SELECT DISTINCT CustomerID, ApprovalStatus
            FROM loans
        )
        SELECT c.StandardizedRegion, COUNT(*) AS RejectedApplications
        FROM unique_loans AS l
        INNER JOIN unique_customers c ON l.CustomerID = c.CustomerID
        WHERE l.ApprovalStatus = 'Rejected'
        GROUP BY c.StandardizedRegion
        """

    # In this case while cleaning the data, since there are duplicate entries, I also standardised the Regions / Provinces to the abbreviated version.
    # I noticed that the North West provice only had the abbreviated version, however, I still included it since it could just be pure chance that there are no rejected applications with the full name as the Region.
    
    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
        CREATE TABLE financing (
            CustomerID TEXT,
            Income REAL,
            LoanAmount REAL,
            LoanTerm INTEGER,
            InterestRate REAL,
            ApprovalStatus TEXT,
            CreditScore INTEGER
        );
        
        INSERT INTO financing
        SELECT DISTINCT
            c.CustomerID,
            c.Income,
            l.LoanAmount,
            l.LoanTerm,
            l.InterestRate,
            l.ApprovalStatus,
            cr.CreditScore
        FROM customers c
        INNER JOIN loans l ON c.CustomerID = l.CustomerID
        INNER JOIN credit cr ON c.CustomerID = cr.CustomerID
        """

    # I answer this question in 2 steps:
    # Step 1 is to create a new table called fianncing with the appropriate schema.
    # Step 2 is to populate the table by joining the relevant tables and removing the duplicates as before.

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    qry = """
        CREATE TABLE timeline AS
        WITH unique_customers AS (
            SELECT DISTINCT *
            FROM customers
        )
        SELECT
            c.CustomerID,
            m.MonthName,
            COALESCE(COUNT(r.RepaymentID),0) AS NumberOfRepayments,
            COALESCE(ROUND(SUM(r.Amount), 2), 0) AS AmountTotal
        FROM unique_customers c
        CROSS JOIN months m
        LEFT JOIN
            repayments r ON r.CustomerID = c.CustomerID
            AND EXTRACT(MONTH FROM r.RepaymentDate AT TIME ZONE r.Timezone AT TIME ZONE 'Europe/London') = m.MonthID
            AND EXTRACT(HOUR FROM r.RepaymentDate AT TIME ZONE r.Timezone AT TIME ZONE 'Europe/London') BETWEEN 6 AND 18
        GROUP BY
            c.CustomerID, m.MonthName, m.MonthID
        ORDER BY
            c.CustomerID, m.MonthID
        """

    # This query creates the table timeline and populates it with a summary of the customer repayments for each month.
    # I started by once again cleaning the data in the customers table by removing the duplicates and avoid double counting.
    # During the LEFT JOIN of the repayments table, I made sure to only select the entries where the repayments are made in that month, as well as between 6am and 6pm, after converting the timestamps from the local timezone to London Time.
    # COALESCE fills all nulls with 0, and ROUND ensures that the amounts are rounded to 2 decimal places.
    # However, during my checks, I found that the Amount values were not rounded to 2 decimals in the output, and I am unsure why.

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """        
        SELECT
            CustomerID,
            -- January
            CAST(SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JanuaryRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0 END), 2) AS JanuaryTotal,
            -- February
            CAST(SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS FebruaryRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0 END), 2) AS FebruaryTotal,
            -- March
            CAST(SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MarchRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0 END), 2) AS MarchTotal,
            -- April
            CAST(SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AprilRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0 END), 2) AS AprilTotal,
            -- May
            CAST(SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MayRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0 END), 2) AS MayTotal,
            -- June
            CAST(SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JuneRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0 END), 2) AS JuneTotal,
            -- July
            CAST(SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JulyRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0 END), 2) AS JulyTotal,
            -- August
            CAST(SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AugustRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0 END), 2) AS AugustTotal,
            -- September
            CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS SeptemberRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END), 2) AS SeptemberTotal,
            -- October
            CAST(SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS OctoberRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0 END), 2) AS OctoberTotal,
            -- November
            CAST(SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS NovemberRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0 END), 2) AS NovemberTotal,
            -- December
            CAST(SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS DecemberRepayments,
            ROUND(SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0 END), 2) AS DecemberTotal
        FROM timeline
        GROUP BY CustomerID
        ORDER BY CustomerID
        """

    # This query pivots the timeline table to display all information relating to a customerID into a wide format.
    # Each row corresponds to one customer with monthly repayment counts and totals, which was calculated in the previous question. I made the query slightly more dynamic by adding all the values, if there were to appear more than 1 row for a given CustomerID and Month

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
        CREATE TABLE corrected_customers AS
        WITH cleaned_customers AS (
            SELECT DISTINCT CustomerID, Age, Gender
            FROM customers
        ),
        numbered AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY Gender ORDER BY CustomerID) AS rn
            FROM cleaned_customers
        ),
        counted AS (
            SELECT Gender, COUNT(*) AS total_rows
            FROM numbered
            GROUP BY Gender
        ),
        with_loop AS (
            SELECT n.CustomerID,
                   n.Age,
                   n.Gender,
                   ((n.rn - 2 - 1 + c.total_rows) % c.total_rows) + 1 AS target_rn

            FROM numbered n
            JOIN counted c ON n.Gender = c.Gender
        ),
        final AS (
            SELECT w.CustomerID,
                   n.Age AS OriginalAge,
                   n2.Age AS CorrectedAge,
                   n.Gender
            FROM with_loop w
            JOIN numbered n ON w.CustomerID = n.CustomerID
            JOIN numbered n2 ON w.Gender = n2.Gender AND w.target_rn = n2.rn
        )
        SELECT CustomerID, OriginalAge AS Age, CorrectedAge, Gender
        FROM final;
        
        SELECT * FROM corrected_customers
        ORDER BY CustomerID
        """

    # I answer this question in a number of steps:
    # Step 1: Once again create a clean customers temporary table, by removing duplicate entries
    # Step 2: Assign a row number to each customer within the gender groups. This row number acts as a consistent index for shifting
    # Step 3: Create another temporary table that holds the total number of Males and Females in the table. This is used for wrap-around when shifting the ages.
    # Step 4: In the with_loop temporary table I then move all of the ages 2 rows down (since they were moved 2 rows up during the conversion), wrapping the movement to the top when necessary
    # Step 5: Join the original and shifted tables on gender and the calculated row number to match each customer with their corrected age.
    # Step 6: Select the required information from the temporary table, final, to store in the created table corrected_customers
    
    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """
        WITH customer_repayments AS (
            SELECT 
                c.CustomerID,
                c.Age,
                c.CorrectedAge,
                c.Gender,
                CASE 
                    WHEN c.CorrectedAge < 20 THEN 'Teen'
                    WHEN c.CorrectedAge < 30 THEN 'Young Adult'
                    WHEN c.CorrectedAge < 60 THEN 'Adult'
                    ELSE 'Pensioner'
                END AS AgeCategory,
                COALESCE(COUNT(r.RepaymentID), 0) AS TotalRepayments
            FROM corrected_customers c
            LEFT JOIN repayments r ON c.CustomerID = r.CustomerID
            GROUP BY c.CustomerID, c.Age, c.CorrectedAge, c.Gender
        )
        SELECT 
            CustomerID,
            Age,
            CorrectedAge,
            Gender,
            AgeCategory,
            DENSE_RANK() OVER (
                PARTITION BY AgeCategory
                ORDER BY TotalRepayments DESC
            ) AS Rank
        FROM customer_repayments
        ORDER BY CustomerID;
        """

    # I answer this question in a number of steps:
    # Step 1: Create a temporary table that joins the corrected_customers table with the repayments table. In this step also count the number of repayments per customer and classify them into AgeCategory based on Corrected Age.
    # Step 2: COALESCE ensures that customers with no repayment has a 0 instead of null
    # Step 3: Then select all the required information from the temporary table and apply DENSE_RANK within each AgeCategory based on the TotalRepayments. This ranking is done in a descreasing order.

    return qry
