from typing import Any, Dict

from langchain_core.messages import AIMessage

from ...classes import ResearchState
from .base import BaseResearcher
import subprocess, asyncio, os
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class CompanyAnalyzer(BaseResearcher):
    def __init__(self) -> None:
        super().__init__()
        self.analyst_type = "company_analyzer"
        self.serp_key = os.getenv("SERP_API_KEY")

    async def find_social_links(self, state: Dict):

        websocket_manager = state.get('websocket_manager')
        job_id = state.get('job_id')
        company = state.get('company')

        # Serp API ====================================================
        params = {
            "q": "site:facebook.com OR site:youtube.com OR site:tiktok.com " + company,
            "api_key": self.serp_key,
            "num": 10 # 10 result
        }

        response = requests.get("https://serpapi.com/search.json", params=params)
        results = response.json()

        # Get the right link ===========================================
        youtube = ""
        facebook = ""
        tiktok = ""

        for res in results.get("organic_results", []):
            link = res["link"]
            
            if "youtube.com" in link:
                # Ưu tiên link channel hoặc @
                if "/channel/" in link or "/@" or "/c/" in link:
                    youtube = link

            elif "facebook.com" in link:
                # Phân tích path
                p = urlparse(link).path
                parts = [p.strip("/") for p in p.split("/") if p.strip("/")]
                # Nếu chỉ có 1 phần sau domain (tức là page chính)
                if len(parts) == 1:
                    facebook = link

            elif "tiktok.com" in link:
                if "/video/" not in link:
                    tiktok = link

        result = [
            f"Youtube: {youtube}",
            f"Facebook: {facebook}",
            f"Tiktok: {tiktok}"
        ]

        # Stream result =======================================================
        try:
            queries = []

            if result:
                for query in result:
                    query = query.strip()
                    if query:
                        queries.append(query)
                        if websocket_manager and job_id:
                            await websocket_manager.send_status_update(
                                job_id=job_id,
                                status="query_generating",
                                message="Generated new research query",
                                result={
                                    "query": query,
                                    "query_number": len(queries),
                                    "category": self.analyst_type,
                                    "is_complete": False
                                }
                            )
            
            logger.info(f"Generated {len(queries)} queries for {self.analyst_type}: {queries}")

            if not queries:
                raise ValueError(f"No queries generated for {company}")

            # Limit to at most 3 queries.
            queries = queries[:3]
            logger.info(f"Final queries for {self.analyst_type}: {queries}")
            
            return queries
            
        except Exception as e:
            logger.error(f"Error generating queries for {company}: {e}")
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="error",
                    message=f"Failed to generate research queries: {str(e)}",
                    error=f"Query generation failed: {str(e)}"
                )
            return []
        

    async def analyze(self, state: ResearchState) -> Dict[str, Any]:

        company = state.get('company', 'Unknown Company')
        msg = [f"🏢 Company Analyzer analyzing {company}"]
        
        # Generate search queries using LLM
        queries = await self.find_social_links(state)

        # Chuyển sang dict_links
        dict_links = {}
        for q in queries:
            source, link = q.split(":", 1)
            dict_links[source.strip().lower()] = link.strip()

        # TODO
        # queries = [
        #     "Youtube: https://www.youtube.com/@raumamix4106",
        #     "Tiktok: https://www.tiktok.com/@raumamix.official",
        #     "Facebook: https://www.facebook.com/Raumamix"
        # ]

        # Add message to show subqueries with emojis
        # subqueries_msg = "🔍 Subqueries for company analysis:\n" + "\n".join([f"• {query}" for query in queries])
        messages = state.get('messages', [])
        # messages.append(AIMessage(content=subqueries_msg))
        state['messages'] = messages

        # Send queries through WebSocket
        if websocket_manager := state.get('websocket_manager'):
            if job_id := state.get('job_id'):
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="processing",
                    message="Company analysis: find social media links",
                    result={
                        "step": "Company Analyst",
                        "analyst_type": "Company Analyst",
                        "queries": queries
                    }
                )
        
        company_data = {}
        
        # If we have site_scrape data, include it first
        if site_scrape := state.get('site_scrape'):
            msg.append("\n📊 Including site scrape data in company analysis...")
            company_url = state.get('company_url', 'company-website')
            company_data[company_url] = {
                'title': state.get('company', 'Unknown Company'),
                'raw_content': site_scrape,
                'query': f'Company overview and information about {company}'  # Add a default query for site scrape
            }
        
        # TODO
        # # Perform additional research with comprehensive search
        # try:
        #     # Store documents with their respective queries
        #     for query in queries:
        #         documents = await self.search_documents(state, [query])
        #         if documents:  # Only process if we got results
        #             for url, doc in documents.items():
        #                 doc['query'] = query  # Associate each document with its query
        #                 company_data[url] = doc
            
        #     msg.append(f"\n✓ Found {len(company_data)} documents")
        #     if websocket_manager := state.get('websocket_manager'):
        #         if job_id := state.get('job_id'):
        #             await websocket_manager.send_status_update(
        #                 job_id=job_id,
        #                 status="processing",
        #                 message=f"Used Tavily Search to find {len(company_data)} documents",
        #                 result={
        #                     "step": "Searching",
        #                     "analyst_type": "Company Analyst",
        #                     "queries": queries
        #                 }
        #             )
        # except Exception as e:
        #     msg.append(f"\n⚠️ Error during research: {str(e)}")
        
        # Update state with our findings
        messages = state.get('messages', [])
        messages.append(AIMessage(content="\n".join(msg)))
        state['messages'] = messages
        state['company_data'] = company_data
        
        return {
            'message': msg,
            'company_data': company_data,
            'social_links': dict_links
        }

    async def run(self, state: ResearchState) -> Dict[str, Any]:
        return await self.analyze(state) 