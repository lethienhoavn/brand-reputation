import logging
import os
from typing import Any, Dict
from pathlib import Path

from langchain_core.messages import AIMessage
from openai import AsyncOpenAI

from ..classes import ResearchState
from ..utils.references import format_references_section

logger = logging.getLogger(__name__)




class Editor:
    """Compiles individual section briefings into a cohesive final report."""
    
    def __init__(self) -> None:
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Configure OpenAI
        self.openai_client = AsyncOpenAI(api_key=self.openai_key)
        
        # Initialize context dictionary for use across methods
        self.context = {
            "company": "Unknown Company",
            "industry": "Unknown",
            "hq_location": "Unknown"
        }

    async def compile_briefings(self, state: ResearchState) -> ResearchState:
        """Compile individual briefing categories from state into a final report."""
        company = state.get('company', 'Unknown Company')
        
        # Update context with values from state
        self.context = {
            "company": company,
            "industry": state.get('industry', 'Unknown'),
            "hq_location": state.get('hq_location', 'Unknown')
        }
        
        # Send initial compilation status
        if websocket_manager := state.get('websocket_manager'):
            if job_id := state.get('job_id'):
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="processing",
                    message=f"Starting report compilation for {company}",
                    result={
                        "step": "Editor",
                        "substep": "initialization"
                    }
                )

        context = {
            "company": company,
            "industry": state.get('industry', 'Unknown'),
            "hq_location": state.get('hq_location', 'Unknown')
        }
        
        msg = [f"📑 Compiling final report for {company}..."]
        
        # Pull individual briefings from dedicated state keys
        briefing_keys = {
            'company': 'company_briefing',
            'industry': 'industry_briefing',
            'financial': 'financial_briefing',
            'news': 'news_briefing'
        }

        # Send briefing collection status
        if websocket_manager := state.get('websocket_manager'):
            if job_id := state.get('job_id'):
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="processing",
                    message="Collecting section briefings",
                    result={
                        "step": "Editor",
                        "substep": "collecting_briefings"
                    }
                )

        # TODO
        try:
            compiled_report = await self.edit_report(state, context)
            if not compiled_report or not compiled_report.strip():
                logger.error("Compiled report is empty!")
            else:
                logger.info(f"Successfully compiled report with {len(compiled_report)} characters")
        except Exception as e:
            logger.error(f"Error during report compilation: {e}")

        state.setdefault('messages', []).append(AIMessage(content="\n".join(msg)))
        return state
    
    async def edit_report(self, state: ResearchState, context: Dict[str, Any]) -> str:
        """Compile section briefings into a final report and update the state."""
        try:
            company = self.context["company"]
            
            # Step 1: Initial Compilation
            if websocket_manager := state.get('websocket_manager'):
                if job_id := state.get('job_id'):
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="processing",
                        message="Compiling initial research report",
                        result={
                            "step": "Editor",
                            "substep": "compilation"
                        }
                    )

            edited_report = await self.compile_content(state, company)
            if not edited_report:
                logger.error("Initial compilation failed")
                return ""

            # Step 2: Deduplication and Cleanup
            if websocket_manager := state.get('websocket_manager'):
                if job_id := state.get('job_id'):
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="processing",
                        message="Cleaning up and organizing report",
                        result={
                            "step": "Editor",
                            "substep": "cleanup"
                        }
                    )

            # Step 3: Formatting Final Report
            if websocket_manager := state.get('websocket_manager'):
                if job_id := state.get('job_id'):
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="processing",
                        message="Formatting final report",
                        result={
                            "step": "Editor",
                            "substep": "format"
                        }
                    )
            final_report = await self.content_sweep(state, edited_report, company)
            
            final_report = final_report or ""
            
            logger.info(f"Final report compiled with {len(final_report)} characters")
            if not final_report.strip():
                logger.error("Final report is empty!")
                return ""
            
            logger.info("Final report preview:")
            logger.info(final_report[:500])
            
            # Update state with the final report in two locations
            state['report'] = final_report
            state['status'] = "editor_complete"
            if 'editor' not in state or not isinstance(state['editor'], dict):
                state['editor'] = {}
            state['editor']['report'] = final_report
            logger.info(f"Report length in state: {len(state.get('report', ''))}")
            
            if websocket_manager := state.get('websocket_manager'):
                if job_id := state.get('job_id'):
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="editor_complete",
                        message="Research report completed",
                        result={
                            "step": "Editor",
                            "report": final_report,
                            "company": company,
                            "is_final": True,
                            "status": "completed"
                        }
                    )
            
            return final_report
        except Exception as e:
            logger.error(f"Error in edit_report: {e}")
            return ""
    
    async def compile_content(self, state: ResearchState, company: str) -> str:
        """Initial compilation of research sections."""

        # TODO
        # combined_content = "\n\n".join(content for content in briefings.values())
        base_path = Path("scrape/data")
        files = ["fb.txt", "tiktok.txt", "youtube.txt"]
        chunks = []

        for file in files:
            file_path = base_path / file
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        source = file.replace(".txt", "")
                        chunks.append(f"{source}\n{content}")

        combined_content = "\n".join(chunks)


        #
        references = state.get('references', [])
        reference_text = ""
        if references:
            logger.info(f"Found {len(references)} references to add during compilation")
            
            # Get pre-processed reference info from curator
            reference_info = state.get('reference_info', {})
            reference_titles = state.get('reference_titles', {})
            
            logger.info(f"Reference info from state: {reference_info}")
            logger.info(f"Reference titles from state: {reference_titles}")
            
            # Use the references module to format the references section
            reference_text = format_references_section(references, reference_info, reference_titles)
            logger.info(f"Added {len(references)} references during compilation")
        
        # Use values from centralized context
        company = self.context["company"]
        industry = self.context["industry"]
        hq_location = self.context["hq_location"]

        youtube_link = state['social_links']['youtube']
        fb_link = state['social_links']['facebook']
        tiktok_link = state['social_links']['tiktok']
        
        prompt = f"""You are compiling a comprehensive research report about {company}.

                    Compiled briefings:
                    {combined_content}

                    Create a comprehensive and focused report on brand {company} that:
                    1. Integrates information from all sections into a cohesive non-repetitive narrative
                    2. Logically organizes information and uses clear section headers and structure
                    3. Here are the social media links of brand {company}, Youtube: {youtube_link}, Facebook: {fb_link}, Tiktok: {tiktok_link}. Use this info as context to find the right info of the brand
                    4. Find some competitors of brand {company} and look for some general social media stat (num likes, followers,...) to fulfill the report. Only show infos that you're sure
                    5. Remember to give some introduction about the brand {company}. Give some infos like: the industry of the company, when it is created, how many stores it has, the owner of the company, some products that it serves,.... Only show infos that you're sure
                    6. In Social Media & User Engagement section, first give general stats. Then, give table num likes / reaction, table num comments, table num shares,.... of the last 10 videos / posts on 3 platforms Youtube, Tiktok, Facebook. Give explanations & insights, not just raw numbers

                    Formatting rules:
                    Strictly enforce this EXACT document structure:

                    # {company} Reputation Report

                    ## Social Media & User Engagement
                    [Company content with ### subsections]

                    ## Competitors
                    [Competitors with ### subsections]

                    Return the report in clean markdown format"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert report editor that looks for useful infos of the company and compiles research briefings into comprehensive company reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                stream=False
            )
            initial_report = response.choices[0].message.content.strip()
            
            # Append the references section after LLM processing
            if reference_text:
                initial_report = f"{initial_report}\n\n{reference_text}"
            
            return initial_report
        except Exception as e:
            logger.error(f"Error in initial compilation: {e}")
            return (combined_content or "").strip()
        
    async def content_sweep(self, state: ResearchState, content: str, company: str) -> str:
        """Sweep the content for any redundant information."""
        # Use values from centralized context
        company = self.context["company"]
        industry = self.context["industry"]
        hq_location = self.context["hq_location"]
        
        prompt = f"""You are an expert briefing editor. You are given a report on {company}.

                    Current report:
                    {content}

                    1. Remove redundant or repetitive information
                    2. Remove information that is not relevant to {company}
                    3. Remove sections lacking substantial content

                    Strictly enforce this EXACT document structure:

                    ## Social Media & User Engagement
                    [Company content with ### subsections]

                    ## Competitors
                    [Competitors content with ### subsections]              

                    Critical rules:
                    1. The document MUST start with "# {company} Reputation Report"
                    2. The document MUST ONLY use these exact ## headers in this order:
                    - ## Social Media & User Engagement
                    - ## Competitors
                    3. NO OTHER ## HEADERS ARE ALLOWED
                    4. Use ### for subsections in Social Media & User Engagement / Competitors sections
                    5. Never use code blocks (```)
                    6. Never use more than one blank line between sections
                    7. Format all bullet points with *, EXCEPT for tables num likes, num shares, num comments
                    8. Add one blank line before and after each section/list

                    Return the polished report in flawless markdown format

                    Return the cleaned report in flawless markdown format."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1", 
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert markdown formatter that ensures consistent document structure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                stream=True
            )
            
            accumulated_text = ""
            buffer = ""
            
            async for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    websocket_manager = state.get('websocket_manager')
                    if websocket_manager and buffer:
                        job_id = state.get('job_id')
                        if job_id:
                            await websocket_manager.send_status_update(
                                job_id=job_id,
                                status="report_chunk",
                                message="Formatting final report",
                                result={
                                    "chunk": buffer,
                                    "step": "Editor"
                                }
                            )
                    break
                    
                chunk_text = chunk.choices[0].delta.content
                if chunk_text:
                    accumulated_text += chunk_text
                    buffer += chunk_text
                    
                    if any(char in buffer for char in ['.', '!', '?', '\n']) and len(buffer) > 10:
                        if websocket_manager := state.get('websocket_manager'):
                            if job_id := state.get('job_id'):
                                await websocket_manager.send_status_update(
                                    job_id=job_id,
                                    status="report_chunk",
                                    message="Formatting final report",
                                    result={
                                        "chunk": buffer,
                                        "step": "Editor"
                                    }
                                )
                        buffer = ""
            
            return (accumulated_text or "").strip()
        except Exception as e:
            logger.error(f"Error in formatting: {e}")
            return (content or "").strip()

    async def run(self, state: ResearchState) -> ResearchState:
        state = await self.compile_briefings(state)
        # Ensure the Editor node's output is stored both top-level and under "editor"
        if 'report' in state:
            if 'editor' not in state or not isinstance(state['editor'], dict):
                state['editor'] = {}
            state['editor']['report'] = state['report']
        return state
