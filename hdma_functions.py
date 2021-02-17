import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import six

def read_in_and_clean_hdma_data(filepath,year,state_code=False):
    """
    inputs:
        filepath (str): filepath to the file 
        year (int): year of data you are working with (see note) 

    Note: Field naming conventions are different between 2007-2017 and 2018-2019. The 
    filtered done below, both based on columns want annd the filtering to loan types are specific to
    these two groups (here hardcoded for 2010 and 2019) but they are likely representative of their respective 
    groups, so if you want other years, can subsituate in the hardcoding. 

    """
    df = pd.read_csv(filepath)

    if year in [2019,2019]:
        df = df[df.derived_loan_product_type.isin(["Conventional:First Lien","FHA:First Lien",
                                               "VA:First Lien","FSA/RHS:First Lien"])] #first lien types 
        df = df[df.business_or_commercial_purpose == 2] #Not primarily for a business or commercial purpose
        df = df[df.loan_purpose == 1] #Home purchase
        #hmda_ca_19 = hmda_ca_19[hmda_ca_19.derived_dwelling_category == "Single Family (1-4 Units):Site-Built"] #dwelling type 
        df = df[df.occupancy_type == 1]  #Principal residence
        df = df[df.action_taken == 1]  #loan actually originated
        df["applicant_income"] = df.income * 1000 
        df = df[["loan_amount","property_value","applicant_income","county_code"]]
    if year in np.arange(2007,2018):
        df = df[df.owner_occupancy == 1] #owner occupied
        df = df[df.loan_purpose == 1]#loan for home purchase 
        df = df[df.action_taken == 1] #loan actually disbursed 
        df = df[df.lien_status == 1] #1st lien
        #hmda_ca_10 = hmda_ca_10[hmda_ca_10.property_type == 1] #single family home

        df["loan_amount"] = df["loan_amount_000s"] *1000
        df["applicant_income"] = df["applicant_income_000s"] *1000
        df = df[["loan_amount","applicant_income","county_name","county_code"]]

    df = df.dropna()
    df.county_code = df.county_code.astype(int)


    return df

def read_in_ami(file_path):
    """
    inputs:
        file_path (str) - filepath to AMI data
    read in county level AMI bands data and do some cleaning 
    """
    #read in county level AMI bands 
    county_level_AMI = pd.read_csv(file_path)
    county_level_AMI = county_level_AMI.rename(columns={"County_Name":"county_name"})#for clean merge
    #create 100% AMI columns from 80% columns 
    county_level_AMI["100% AMI"] = county_level_AMI["80%_AMI"] * 1.25
    #clean up names 
    county_level_AMI = county_level_AMI.rename(columns={"80%_AMI":"80% AMI","120%_AMI":"120% AMI"})

    county_level_AMI_2010 = county_level_AMI[county_level_AMI.year == 2010]
    county_level_AMI_2019 = county_level_AMI[county_level_AMI.year == 2019]
    return county_level_AMI_2010, county_level_AMI_2019

def middle_income(df,income_col):
    """
    Inputs:
        df (dataframe)
        income_col (str): name of column with income info 
    returns a new column binary value for whether the income is within 80-120 AMI or not 
    """
    return np.where((df[income_col] > df["80% AMI"])&(df[income_col] <= df["120% AMI"]), 1, 0)

def calc_percent_binary_col(df,binary_column):
    """
    Inputs:
    df (dataframe)
        binary_column (str): name of column to calculate sum of binary values over length of col
    """
    return df[binary_column].sum() / len(df[binary_column])

def percent_change(figure1, figure2):
    """
    Inputs:
        figure1 (int)
        figure2 (int)
    returns percent change between two figures 
    """
    pct_change = ((figure2 - figure1))/figure1
    return (pct_change * 100).round(2)

#https://stackoverflow.com/questions/26678467/export-a-pandas-dataframe-as-a-table-image
def render_mpl_table(data, col_width=14.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def change_in_absolute_number(df1, df2):
    """
    creates a data frame showing, in absolute numbers, what is the change between the number of 
    middle income households that bought houses by county between 2010 and 2019?
    inputs: 
        df1 (dataframe): here, 2019 middle income HDMA loans 
        df2 (dataframe): here, 2010 middle income HDMA loans 
    
    """
    df = pd.DataFrame(df1.groupby("county_name").size() - df2.groupby("county_name").size())
    df = df.reset_index().rename(columns={0:"Change in Number of Middle Income Home Buyers"}).drop([10,28])
    #drop madera and shasta as there is no 2010 AMI data for them 
    df = df.rename(columns={"county_name":"County Name"})
    return df 

def calc_house_afford(x,interest_2010=True):
    """
    Inputs:
        x (int): income
        interest_2010 (bool): true if 2010 interest rate, which is hardcoded, should be used
                                if false, 2019 interest rates are hardcoded. Both from Freddie Mac. 
        
    This function returns value of total loan someone at a given 
    income, x, could afford. This function multiplies by 12*30 (12 months, 30 year mortgate) to back out the total cost with these monthy costs. But because we are assumign out the 20% down payment, the actual home value is 25% more. However, in the HDMA loan data we are seeing value of the loans, not total value of house
    so do NOT need to add down payment back in when calculating how many of the loans in the HMDA data would have been 
    affordable, but important to note if we want to talk about cost of loan one can afford VS. value of house one can afford. 
    
    We are assuming 20% down and that 30% of monthly income is the maximum affordable payment. Also assuming a 30 year mortage.     
    """
    #below should be complete and 

    if interest_2010 == True:
        interest = 4.69
    if interest_2010 == False:
        #this is the 2019 rate 
        interest = 3.94

    #need to add a line that checks weather data is 2010 or 2019 for
    #which interest rate to use, or seperate dataframes and concat back together
    monthly_wage = x/12 #yearly wage / 12 
    N = (30*12) #assuming a 30 year mortgage 
    r = (interest /100)/12 #monthly interest rate, IR_2010 is for 2010 data. Divide by 100 to get 3.94 to 0.0394
    denom = 1 - (1 + r)**-N 
    P = (denom * .3 * monthly_wage)/r
    return P

def calc_loan_values_2019(x):
    return calc_house_afford(x,interest_2010=False)
def calc_loan_values(x):
    return calc_house_afford(x)

#col = "120%_AMI"
def calc_value(df,col, year):
    """
    inputs:
        df with county name, income for AMI band
        col: string, name of AMI band we are calculating value for 
        year: int, in this case either 2010 or 2019. Makes sure we use interest rates for year we are trying to calculate for 
    Below I am calculating the max affordable loan amount for a XXX AMI household and then 
    calculating, for each county, how many of all loans fall below that threshold  
     
    """
    if col not in df:
        print("Column not in dataframe")
    
    max_afford_str = "Max_Affordable_Loan_" + col
    is_affordable_str = "Total Number of Loans Affordable to " + col + " or Lower Households " + str(year)
    
    if year == 2019:
        df[max_afford_str]= df[col].apply(lambda x: calc_loan_values_2019(x))
    elif year == 2010:
        df[max_afford_str]= df[col].apply(lambda x: calc_loan_values(x))
    else:
        print("Invalid Year")
    df[is_affordable_str] = np.where(df[max_afford_str] >= df["loan_amount"], 1, 0)

    total_affordable= df[["county_name",is_affordable_str]].groupby("county_name").sum().reset_index() #get sum of affordable loans
    total_affordable = total_affordable[(total_affordable != 0).all(1)]#drop zero columns; here they are just <75k population counties 

    return total_affordable

def merge_years(df2010,df2019):
    """
    After doing Max Loan value calculations for each 2010 and 2019 above, 
    this little function just merges these columns together, keeps only the cols we want
    and then calcualtes the percentage change in percentage of affordable loans in 2010 and 2019
    """
    affordable_2010_2019 = df2019.merge(df2010,on="county_name")
    col_2019 = [i for i in affordable_2010_2019.columns.tolist() if "Households 2019" in i]
    col_2010 = [i for i in affordable_2010_2019.columns.tolist() if "Households 2010" in i] 
    affordable_2010_2019["Percent Change"] = percent_change(affordable_2010_2019[col_2010[0]],affordable_2010_2019[col_2019[0]])
    affordable_2010_2019 = affordable_2010_2019.sort_values("Percent Change")
    affordable_2010_2019 = affordable_2010_2019.rename(columns={"county_name":"County Name"})
    return affordable_2010_2019
