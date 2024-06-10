Chat Agent:
  1. NLP2SQL
     - To chat with the structured data
     - Technology used
       - Python, Django, Openai
     - API(POST)
       http://54.237.107.120:8001/demoapp/structured/
       raw JSON body: {
        "query":"provide me their employee count as well",
        "session_id": "6e0331b2-f738-4efd-8c34-1d2502217eb6",
        "user_id":"abhay",
        "schemaname": "talkable_master",
        "tablename": "master_account_hfsf_account_deals_oppo, master_contact_hfsf_lead_contact"
    }
  2. Talkable-Unstructured
     - To chat with the unstructured data of Talkable(website, blogs, etc.)
     - Technology used
       - Python, Django, Openai
     - API(POST)
       http://54.237.107.120:8001/demoapp/unstructured/
       raw JSON body: {
        "query":"list all the products offered by talkable",
        "session_id": "6e0331b2-f738-4efd-8c34-1d2502217eb6",
        "user_id":"abhay"
    }
     
