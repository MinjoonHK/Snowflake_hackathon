import os

import streamlit as st
from dotenv import load_dotenv


@st.cache_resource
def get_session():
    try:
        from snowflake.snowpark.context import get_active_session

        return get_active_session()
    except Exception:
        from snowflake.snowpark import Session

        load_dotenv()
        return Session.builder.configs(
            {
                "account": os.environ["SF_ACCOUNT"],
                "user": os.environ["SF_USER"],
                "password": os.environ["SF_PASSWORD"],
                "warehouse": os.environ["SF_WAREHOUSE"],
                "database": "SPH_DATA",
                "schema": "GRANDATA",
            }
        ).create()
