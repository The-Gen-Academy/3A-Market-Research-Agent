import streamlit as st
import operator
import os
from typing import Annotated, TypedDict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LangChain & LangGraph imports
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# Load environment variables from .env
load_dotenv()
# --- DEBUG START ---
raw_key = os.getenv("GROQ_API_KEY", "NOT FOUND")
print(f"DEBUG: Key found: {'Yes' if raw_key != 'NOT FOUND' else 'No'}")
if raw_key != "NOT FOUND":
    print(f"DEBUG: Key starts with: {raw_key[:8]}...")
# --- DEBUG END ---

# --- 1. DATA MODELS & STATE ---

class ResearchState(TypedDict):
    company: str
    competitor_queue: List[str]
    current_target: str
    raw_data: str
    final_reports: Annotated[List[dict], operator.add]

class CompetitorReport(BaseModel):
    competitor_name: str
    pricing_model: str = Field(description='How they make money, specific prices if found.')
    core_features: List[str] = Field(description='List of 3-5 main features.')
    market_positioning: str
    recent_news: str = Field(description='Any recent launches or news found')

class CompetitorList(BaseModel):
    competitors: List[str] = Field(description="Exactly 3 specific competitor products or services.")

# --- 2. GRAPH NODES ---

web_search = DuckDuckGoSearchRun()

def get_llm():
    # Directly pulls from the .env loaded into the environment
    return ChatGroq(model='llama-3.3-70b-versatile', temperature=0)

def discovery_node(state: ResearchState):
    llm = get_llm()
    target_company = state['company']
    st.write(f"🔍 **Discovery:** Scanning market for '{target_company}' competitors...")
    
    query = f"Top 3 specific product competitors to {target_company} software."
    raw_results = web_search.invoke(query)
    
    structured_llm = llm.with_structured_output(CompetitorList)
    prompt = ChatPromptTemplate.from_template("Extract the top competitors from this data:\n{data}")
    result = (prompt | structured_llm).invoke({'data': raw_results})
    
    return {"competitor_queue": result.competitors}

def researcher_node(state: ResearchState):
    competitor_queue = state['competitor_queue'].copy()
    competitor_company = competitor_queue.pop(0)
    target_company = state['company']
    
    st.write(f"🌐 **Researcher:** Gathering data on `{competitor_company}`...")
    
    search_query = f'{competitor_company} software pricing features, news, market positioning vs {target_company}'
    search_results = web_search.invoke(search_query)
    
    return {
        'competitor_queue': competitor_queue,
        'current_target': competitor_company,
        'raw_data': search_results
    }

def analyst_node(state: ResearchState):
    llm = get_llm()
    competitor_company = state['current_target']
    st.write(f"📊 **Analyst:** Formatting report for `{competitor_company}`...")

    all_raw_data = state["raw_data"]
    structured_llm = llm.with_structured_output(CompetitorReport)

    system_prompt = f"""You are an elite market analyst. Extract the requested information from the raw web data.
    You are analyzing the competitor: {competitor_company}.
    Compare them against our company: {state['company']}.
    If you cannot find a specific detail in the text, write 'Data not found'."""

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        ("human", "Raw Web Data:\n{data}")
    ])

    report = (prompt | structured_llm).invoke({'data': all_raw_data})
    return {'final_reports': [report.model_dump()]}

def queue_router(state: ResearchState):
    if len(state["competitor_queue"]) == 0:
        return END
    return "Researcher"

# --- 3. STREAMLIT UI ---

def main():
    st.set_page_config(page_title="Market Research Agent", page_icon="📈")
    
    st.title("🚀 Market Research AI Agent")
    st.markdown("Enter your company name to analyze your top 3 competitors.")

    # Simple Input section
    company_name = st.text_input("Your Company/Product Name:", placeholder="e.g. Anthropic Claude")

    if st.button("Run Research Pipeline"):
        # Check if API Key exists in environment
        if not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY not found in .env file.")
            return
        
        if not company_name:
            st.warning("Please enter a company name.")
            return

        # Initialize the Graph
        builder = StateGraph(ResearchState)
        builder.add_node('Discovery', discovery_node)
        builder.add_node("Researcher", researcher_node)
        builder.add_node("Analyst", analyst_node)

        builder.add_edge(START, 'Discovery')
        builder.add_edge('Discovery', 'Researcher')
        builder.add_edge('Researcher', 'Analyst')
        builder.add_conditional_edges('Analyst', queue_router)

        graph = builder.compile()

        # Run Graph with progress status
        with st.status("Agent Pipeline Running...", expanded=True) as status:
            initial_state = {
                'company': company_name,
                'competitor_queue': [],
                'final_reports': []
            }
            final_output = graph.invoke(initial_state)
            status.update(label="Research Complete!", state="complete", expanded=False)

        # Display Results
        st.divider()
        st.header("🎯 Competitor Analysis Results")
        
        for report in final_output['final_reports']:
            with st.expander(f"🏁 {report['competitor_name']}", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Pricing")
                    st.write(report['pricing_model'])
                    
                    st.subheader("Market Position")
                    st.write(report['market_positioning'])

                with col2:
                    st.subheader("Core Features")
                    for feature in report['core_features']:
                        st.markdown(f"- {feature}")
                    
                    st.subheader("Recent News")
                    st.info(report['recent_news'])

if __name__ == "__main__":
    main()