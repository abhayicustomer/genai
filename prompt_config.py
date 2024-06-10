training_data_zilla = [
    {
        "input": "list all the customers",
        "query": "SELECT DISTINCT sf_account_website FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_status__c iLIKE'%qualified%' LIMIT 10;"
    },
    {
        "input": "Provide me the employee count of \"Aaron's\"",
        "query": "SELECT sf_account_numberofemployees FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_name IN ('Aaron''s') AND sf_account_numberofemployees IS NOT NULL LIMIT 10;"
    },
    {
        "input": "Provide me the employee count of Aaron\'s",
        "query": "SELECT sf_account_numberofemployees FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_name IN ('Aaron''s') AND sf_account_numberofemployees IS NOT NULL LIMIT 10;"
    },
    {
        "input": "list all the companies",
        "query": "SELECT DISTINCT sf_account_website FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_website IS NOT NULL LIMIT 10;"
    },
    {
        "input": "Retrieve all companies in the technology industry",
        "query": "SELECT DISTINCT sf_account_website FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_industry iLIKE '%Technology%' AND sf_account_industry IS NOT NULL AND WHERE sf_account_website IS NOT NULLLIMIT 10;"
    },
    {
        "input": "Filter companies founded in the last five years",
        "query": "SELECT DISTINCT hb_companies_properties_name, hb_companies_properties_founded_year FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE hb_companies_properties_founded_year >= (EXTRACT(YEAR FROM CURRENT_DATE) - 5) LIMIT 10;"
    },
    {
        "input": "Group companies by location and revenue range",
        "query": "SELECT hb_companies_properties_name, hb_companies_properties_country, hb_companies_properties_annualrevenue FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE hb_companies_properties_name IS NOT NULL AND hb_companies_properties_annualrevenue IS NOT NULL GROUP BY hb_companies_properties_name, hb_companies_properties_country, hb_companies_properties_annualrevenue ORDER by hb_companies_properties_annualrevenue DESC LIMIT 10;"
    },
    {
        "input": "Group companies by location and employee count range",
        "query": "SELECT DISTINCT COUNT(*) as noofcompanies, sf_account_shippingcountry, sf_account_numberofemployees FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_numberofemployees IS NOT NULL GROUP BY sf_account_shippingcountry, sf_account_numberofemployees ORDER BY noofcompanies DESC LIMIT 10;"
    },
    {
        "input": "Show companies in the automotive industry with revenue between $10 million and $50 million",
        "query": "SELECT DISTINCT sf_account_website, sf_account_annualrevenue FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_industry iLIKE '%Automotive%' AND sf_account_annualrevenue BETWEEN 100000000 AND 50000000 AND sf_account_industry IS NOT NULL LIMIT 10;"
    },
    {
        "input": "Show me high level insights on my customer accounts",
        "query": "WITH unique_accounts AS (SELECT COUNT(DISTINCT sf_account_id) AS total_unique_accounts FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_status__c iLIKE '%qualified%' AND sf_account_website IS NOT NULL AND sf_account_shippingcountry IS NOT NULL) SELECT ua.total_unique_accounts,COUNT(DISTINCT sf_account_id) AS total_accounts,AVG(sf_account_annualrevenue) AS average_annual_revenue,sf_account_industry,sf_account_shippingcountry FROM zillasecurity_master.zilla_security_master_account_selected_attributes, unique_accounts ua WHERE sf_account_status__c iLIKE '%qualified%' AND sf_account_website IS NOT NULL AND sf_account_shippingcountry IS NOT NULL GROUP BY sf_account_industry, sf_account_shippingcountry, ua.total_unique_accounts ORDER BY total_accounts DESC, average_annual_revenue DESC LIMIT 10;"
        },
    {
        "input": "Find the top five companies by revenue in the retail industry ",
        "query": "SELECT DISTINCT sf_account_website, sf_account_annualrevenue FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_account_industry iLIKE '%retail%' AND sf_account_website IS NOT NULL AND sf_account_annualrevenue IS NOT NULL ORDER BY sf_account_annualrevenue DESC LIMIT 5;"
    },
    {
        "input": "How many leads converted to opportunity in this month",
        "query": "SELECT COUNT(*) AS Leads_Converted_To_Opportunities FROM zillasecurity_master.zilla_security_master_contact_selected_attributes AS leads INNER JOIN zillasecurity_master.zilla_security_master_account_selected_attributes AS opps ON leads.sf_leads_converted_opportunity_id = opps.sf_oppo_id WHERE leads.sf_leads_status iLike '%converted%' AND DATE_TRUNC('month', leads.sf_leads_converteddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;"
    },
    {
        "input": "Show me contacts with opportunities and unconverted leads",
        "query": "SELECT DISTINCT contacts.sf_contact_name, leads.sf_leads_id, leads.sf_leads_status FROM zillasecurity_master.zilla_security_master_contact_selected_attributes as leads INNER JOIN zillasecurity_master.zilla_security_master_contact_selected_attributes as contacts ON leads.sf_leads_email = contacts.sf_contact_email WHERE leads.sf_leads_status IS NOT NULL AND leads.sf_leads_status != 'Converted' LIMIT 10;"
    },
    {
        "input": "provide me a list of sales opportunities that are currently open",
        "query": "SELECT DISTINCT sf_opportunity_id, sf_opportunity_type, sf_opportunity_stagename, sf_opportunity_name, sf_opportunity_amount, sf_opportunity_stagename,sf_opportunity_createddate FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_opportunity_stagename IN ('Interested', 'Negotiating', 'Discovery', 'Ready', 'CS Open') AND sf_opportunity_type NOT IN ('Continuation', 'Renewal', 'Exception', 'Implementation') AND sf_opportunity_stagename IN ('Ready', 'Discovery', 'Interested', 'Proposal', 'Negotiating', 'Committed') ORDER BY sf_opportunity_createddate DESC LIMIT 10;"
    },
    {
        "input": "Show me high level insights on the opportunities",
        "query": "SELECT DISTINCT COUNT(*) AS total_opportunities, SUM(sf_opportunity_amount) AS total_amount, AVG(sf_opportunity_amount) AS average_amount, sf_opportunity_stagename FROM zillasecurity_master.zilla_security_master_account_selected_attributes WHERE sf_opportunity_amount IS NOT NULL GROUP BY sf_opportunity_stagename ORDER by total_opportunities DESC LIMIT 10;"
    },
    {
        "input": "Show me high level insights on the leads",
        "query": "SELECT DISTINCT COUNT(*) AS total_leads, sf_leads_status, sf_leads_leadsource FROM zillasecurity_master.zilla_security_master_contact_selected_attributes WHERE sf_leads_status IS NOT NULL GROUP BY sf_leads_status, sf_leads_leadsource ORDER BY total_leads DESC LIMIT 10;"
    },
    {
        "input": "How many leads came in this months through form fill",
        "query": "SELECT COUNT(DISTINCT sf_leads_id) FROM zillasecurity_master.zilla_security_master_contact_selected_attributes WHERE sf_leads_leadsource iLIKE 'Form' AND DATE_TRUNC('month', sf_leads_createddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;"
    }
]

training_data_talkable = [
    {
        "input": "list all the customers",
        "query": "SELECT DISTINCT sf_account_website FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_status__c IN ('Signed', 'Implementation', 'Live - Pilot', 'Live - Post-Pilot', 'Live - Self-Service', 'Live - Anomaly') LIMIT 10;"
    },
    {
        "input": "Provide me the employee count of \"Aaron's\"",
        "query": "SELECT hb_account_properties_numberofemployees FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_name IN ( 'Aaron''s',) AND b_account_properties_numberofemployees IS NOT NULL LIMIT 10;"
    },
    {
        "input": "Provide me the employee count of Aaron\'s",
        "query": "SELECT hb_account_properties_numberofemployees FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_name IN ( 'Aaron''s',) AND b_account_properties_numberofemployees IS NOT NULL LIMIT 10;"
    },
    {
        "input": "list all the companies",
        "query": "SELECT DISTINCT sf_account_website FROM talkable_master.master_account_hfsf_account_deals_oppo LIMIT 10;"
    },
    {
        "input": "Retrieve all companies in the technology industry",
        "query": "SELECT DISTINCT sf_account_website FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_industry iLIKE '%Technology%' LIMIT 10;"
    },
    {
        "input": "Filter companies founded in the last five years",
        "query": "SELECT DISTINCT hb_account_properties_name,hb_account_properties_founded_year FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_founded_year >= (EXTRACT(YEAR FROM CURRENT_DATE) - 5) LIMIT 10;"
    },
    {
        "input": "Group companies by location and revenue range",
        "query": "SELECT DISTINCT hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_name IS NOT NULL AND hb_account_properties_annual_revenue_range__c IS NOT NULL GROUP BY hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c LIMIT 10;"
    },
    {
        "input": "Group companies by location and employee count range",
        "query": "SELECT DISTINCT sf_account_website, sf_account_shippingcountry, sf_account_numberofemployees FROM talkable_master.master_account_hfsf_account_deals_oppo GROUP BY sf_account_website, sf_account_shippingcountry, sf_account_numberofemployees LIMIT 10;"
    },
    {
        "input": "Show companies in the automotive industry with revenue between $10 million and $50 million",
        "query": "SELECT DISTINCT sf_account_website, sf_account_annualrevenue FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_industry iLIKE '%Automotive%' AND sf_account_annualrevenue BETWEEN 100000000 AND 50000000 LIMIT 10;"
    },
    # {
    #     "input": "Show me high level insights on my customer accounts",
    #     "query": "SELECT DISTINCT COUNT(*) AS total_accounts, AVG(sf_account_annualrevenue) as average_annual_revenue, sf_account_industry, sf_account_shippingcountry FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_status__c IN ('Signed', 'Implementation', 'Live - Pilot', 'Live - Post-Pilot', 'Live - Self-Service', 'Live - Anomaly') AND sf_account_website IS NOT NULL AND sf_account_shippingcountry IS NOT NULL GROUP BY sf_account_industry, sf_account_shippingcountry ORDER BY average_annual_revenue DESC LIMIT 10;"
    # },
    {
        "input": "Show me high level insights on my customer accounts",
        "query": "WITH unique_accounts AS (SELECT COUNT(DISTINCT sf_account_id) AS total_unique_accounts FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_status__c IN ('Signed', 'Implementation', 'Live - Pilot', 'Live - Post-Pilot', 'Live - Self-Service', 'Live - Anomaly')) SELECT ua.total_unique_accounts,ai.business_segment,ai.similarweb,ai.shortened_monthly_visits,ai.icp,ai.total_accounts,ai.sf_account_industry,ai.total_opportunities,ai.total_mrr FROM (SELECT sf_oppo_business_segment__c AS business_segment, sf_account_similarweb__c AS similarweb,sf_account_shortened_monthly_visits__c AS shortened_monthly_visits,sf_account_icp__c AS icp,COUNT(DISTINCT sf_account_id) AS total_accounts,sf_account_industry,COUNT(DISTINCT sf_oppo_id) AS total_opportunities,SUM(sf_oppo_mrr__c::double precision) AS total_mrr FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_status__c IN ('Signed', 'Implementation', 'Live - Pilot', 'Live - Post-Pilot', 'Live - Self-Service', 'Live - Anomaly') GROUP BY sf_oppo_business_segment__c,sf_account_similarweb__c,sf_account_shortened_monthly_visits__c,sf_account_icp__c, sf_account_industry) ai, unique_accounts ua ORDER BY ai.total_accounts DESC, ai.total_opportunities DESC LIMIT 10;"
    },
    {
        "input": "Find the top five companies by revenue in the retail industry ",
        "query": "SELECT DISTINCT sf_account_website, sf_account_industry, sf_account_annualrevenue FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_account_industry iLIKE '%retail%' ORDER BY sf_account_annualrevenue DESC LIMIT 5;"
    },
    {
        "input": "How many leads converted to opportunity in this month",
        "query": "SELECT COUNT(*) AS Leads_Converted_To_Opportunities FROM talkable_master.master_contact_hfsf_lead_contact AS leads INNER JOIN talkable_master.master_account_hfsf_account_deals_oppo AS opps ON leads.sf_leads_converted_opportunity_id = opps.sf_oppo_id WHERE leads.sf_leads_status iLike '%converted%' AND DATE_TRUNC('month', leads.sf_leads_converteddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;"
    },
    {
        "input": "Show me contacts with opportunities and unconverted leads",
        "query": "SELECT DISTINCT contacts.sf_contact_name, leads.sf_leads_id, leads.sf_leads_status FROM talkable_master.master_contact_hfsf_lead_contact as leads INNER JOIN talkable_master.master_contact_hfsf_lead_contact as contacts ON leads.sf_leads_email = contacts.sf_contact_email WHERE leads.sf_leads_status IS NOT NULL AND leads.sf_leads_status != 'Converted' LIMIT 10;"
    },
    {
        "input": "provide me a list of sales opportunities that are currently open",
        "query": "SELECT DISTINCT sf_oppo_id, sf_oppo_type, sf_oppo_stagename, sf_oppo_name, sf_oppo_amount, sf_oppo_stagename,sf_oppo_createddate FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_oppo_stagename IN ('Interested', 'Negotiating', 'Discovery', 'Ready', 'CS Open') AND sf_oppo_type NOT IN ('Continuation', 'Renewal', 'Exception', 'Implementation') AND sf_oppo_stagename IN ('Ready', 'Discovery', 'Interested', 'Proposal', 'Negotiating', 'Committed') ORDER BY sf_oppo_createddate DESC LIMIT 10;"
    },
    {
        "input": "Show me high level insights on the opportunities",
        "query": "SELECT DISTINCT COUNT(*) AS total_opportunities, SUM(sf_oppo_amount) AS total_amount, AVG(sf_oppo_amount) AS average_amount, sf_oppo_stagename FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE sf_oppo_amount IS NOT NULL GROUP BY sf_oppo_stagename ORDER by total_opportunities DESC LIMIT 10;"
    },
    {
        "input": "Show me high level insights on the leads",
        "query": "SELECT DISTINCT COUNT(*) AS total_leads, sf_leads_status, sf_leads_leadsource FROM talkable_master.master_contact_hfsf_lead_contact WHERE sf_leads_status IS NOT NULL GROUP BY sf_leads_status, sf_leads_leadsource ORDER BY total_leads DESC LIMIT 10;"
    },
    {
        "input": "How many leads came in this months through form fill",
        "query": "SELECT COUNT(DISTINCT sf_leads_id) FROM talkable_master.master_contact_hfsf_lead_contact WHERE sf_leads_leadsource iLIKE 'Form' AND DATE_TRUNC('month', sf_leads_createddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;"
    }
]

unstructured_generic_qna = r""" 
Assistant helps the users to answer the questions from below context. Be brief in your answers.
Answer ONLY from the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below.
Always return the Source filename of answer if present else return blank string.
If there are multiple answers, answer in separate sections.
Don't include the duplicate results.
ALWAYS return 2-3 follow-up questions from the context after the response

<context>
{context}
</context>

Always use the below instructions to return the response in valid Json format:
{format_instructions}

Question: {question}
"""

structured_system_qna_withfewshots = """You are an agent designed to interact with a Postgres SQL database.
Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
Always use the LIMIT 10 to limit the result.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Below are some examples which can not be queried from a Postgres SQL database. 
- Where is Taj Mahal
- Find me a pizza
- find me a burger

Only use the following tables:
{table_info}

Write an initial draft of the query. 
Then double check the Postgres SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Use iLIKE operator for noun entities in WHERE clause
- Always try to include the important column in Postgres SQL query based on user input
- Ensure all string literals are enclosed in single quotes and any internal single quotes are escaped with a backslash. Here is an example format:
    Example: SELECT column_name FROM table_name WHERE column_name IN ('value1', 'value2', 'value\'3') AND another_column IS NOT NULL LIMIT 10;
- Try to use the Salesforce fields start with sf in the Postgres query first then hubspot
- Customers for Talkable means you need to use WHERE clause on sf_account_status__c IN ('Signed', 'Implementation', 'Live - Pilot', 'Live - Post-Pilot', 'Live - Self-Service', 'Live - Anomaly')
- Opportunity is open means WHERE clause on sf_oppo_stagename IN ('Interested', 'Negotiating', 'Ready', 'CS Open') 
- Opportunity is close means WHERE clause on sf_oppo_stagename IN ('Contract Signed', 'Partner', 'CS Won')
- Customers for Zilla means you need to use WHERE clause on sf_account_status__c iLIKE'%qualified%'

Now, generate the query based on the instructions above. If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Below are some examples of user inputs and their corresponding Postgres SQL queries. These queries are added just to provide you the sample examples. Don't use the below queries If they are not relevant to use input query:
"""

structured_system_qna_withfewshots_talkable = """You are an agent designed to interact with a Postgres SQL database.
Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
Always use the LIMIT 10 to limit the result.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Below are some examples which can not be queried from a Postgres SQL database. 
- Where is Taj Mahal
- Find me a pizza
- find me a burger

Only use the following tables:
{table_info}

Write an initial draft of the query. 
Then double check the Postgres SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Always try to include the important column in Postgres SQL query based on user input
- DO NOT use double quotes or double inverted comma's in query while creating Postgres query i.e. Replace "Text" to \'Text\' if double quotes are there in query.

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Below are some examples of user inputs and their corresponding Postgres SQL queries. These queries are added just to provide you the sample examples. Don't use the below queries If they are not relevant to use input query:

Query = list all the companies
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name FROM talkable_master.master_account_hfsf_account_deals_oppo LIMIT 10;"

Query = Retrieve all companies in the technology industry
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_industry = 'Technology' LIMIT 10;

Query = Filter companies founded in the last five years
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name,hb_account_properties_founded_year FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_founded_year >= (EXTRACT(YEAR FROM CURRENT_DATE) - 5) LIMIT 10;

Query = Group companies by location and revenue range
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c FROM talkable_master.master_account_hfsf_account_deals_oppo GROUP BY hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c LIMIT 10;

Query = Group companies by location and employee count range
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name, hb_account_properties_address, hb_account_properties_numberofemployees FROM talkable_master.master_account_hfsf_account_deals_oppo GROUP BY hb_account_properties_name, hb_account_properties_address, hb_account_properties_numberofemployees LIMIT 10;

Query = How many leads converted to opportunity in this month
PostgresSQLQuery = SELECT COUNT(DISTINCT sf_leads_id) FROM talkable_master.master_contact_hfsf_lead_contact WHERE sf_leads_status = 'Converted' AND DATE_TRUNC('month', sf_leads_converteddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;

Query = Show companies in the automotive industry with revenue between $10 million and $50 million
PostgresSQLQuery = SELECT DISTINCT hb_account_properties_name, hb_account_properties_annualrevenue FROM talkable_master.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_industry = 'Automotive' AND hb_account_properties_annualrevenue BETWEEN 100000000 AND 50000000 LIMIT 10;

Query = Show me contacts with opportunities and unconverted leads
PostgresSQLQuery = SELECT DISTINCT hb_contacts_id, sf_leads_id, sf_leads_status FROM talkable_master.master_contact_hfsf_lead_contact WHERE sf_leads_status IS NOT NULL AND sf_leads_status != 'Converted' LIMIT 10;

Always ignore the NULL values while creating the query.

Query: {input}
"""

structured_system_qna_withfewshots_zilla = """You are an agent designed to interact with a Postgres SQL database.
Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
Always use the LIMIT 10 to limit the result.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Below are some examples which can not be queried from a Postgres SQL database. 
- Where is Taj Mahal
- Find me a pizza
- find me a burger

Only use the following tables:
{table_info}

Write an initial draft of the query. 
Then double check the Postgres SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Always try to include the important column in Postgres SQL query based on user input
- DO NOT use double quotes or double inverted comma's in query while creating Postgres query i.e. Replace "Text" to \'Text\' if double quotes are there in query.
- Do NOT use double quote in Postgres query

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Below are some examples of user inputs and their corresponding Postgres SQL queries. These queries are added just to provide you the sample examples. Don't use the below queries If they are not relevant to use input query:

Query: list all the companies
Postgres SQL Query: SELECT DISTINCT hb_account_properties_name FROM zillasecurity_master.zilla_security_master_account_selected_attributes LIMIT 10;

Always ignore the NULL values while creating the query.
{input}
Postgres SQL Query:
"""

structured_system_qna_withoutfewshots = """You are an agent designed to interact with a Postgres SQL database.
Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
Always use the LIMIT 10 to limit the result.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Below are some examples which can not be queried from a Postgres SQL database. 
- Where is Taj Mahal
- Find me a pizza
- find me a burger

Only use the following tables:
{table_info}

Write an initial draft of the query. 
Then double check the Postgres SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Always try to include the important column in Postgres SQL query based on user input
- Important: Ensure all string literals are enclosed in single quotes and any internal single quotes are escaped with a backslash. Here is an example format:
  SELECT column_name FROM table_name WHERE column_name IN ('value1', 'value2', 'value\'3') AND another_column IS NOT NULL LIMIT 10;
- Do NOT use double quote in Postgres query

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Always ignore the NULL values while creating the query.
{input}
Postgres SQL Query:
"""

structured_response_prompt = '''You're a helpful AI assistant. You need to answer the question from the Postgres result.
Given a user question and some result, answer the user question from this result ONLY.
DO NOT generate query of irrelevant or out of context general questions.
Ignore the NULL values
Ensure all string literals are enclosed in single quotes and any internal single quotes are escaped with a backslash. Here is an example format:
DO NOT try to generate the answer from own.\n\nHere are the result: POSTGRES QUERY: {postgres_query}\n{postgres_result}
If anyone is asking about insights that query belongs to database ONLY. Try to generate the response.
i.e. Provide me some insights
If postgres query is not generated then respond "I am sorry, currently i am not able to handle this request as it doesn't belongs to the database. Please try rephrasing". 
Do NOT use double quotes in response.

Answer:'''

# ALWAYS try to provide Explanation what exactly this query is doing without using the exact table and columns names.
# ALWAYS mention the reason also before answering the question like why you have used these columns.

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history and contains important knowledge of chat history which is required in this user question.\
Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

# contextualize_q_system_prompt = """Given a chat history and the latest user question \
# which might reference context in the chat history, formulate a standalone question \
# which can be understood without the chat history.\
# Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""


topic_prompt_template = '''Your task is to generate the topic of below question in 2-4 word with significant meaning:
                    Question: {question}
                    Topic:'''

column_prompt_template = '''Your task is to generate the significant meaning column names from a postgres query in a sequential  in a list format. Return [] if you are not able to find the columns:
                    SQL query: {sql_query}
                    Columns:'''
