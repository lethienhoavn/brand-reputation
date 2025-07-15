from langchain_core.messages import AIMessage

from ..classes import ResearchState
import subprocess, asyncio
import logging
from functools import partial
import shutil, os

logger = logging.getLogger(__name__)

class Collector:
    """Collects and organizes all scraped data before curation."""

    async def collect(self, state: ResearchState) -> ResearchState:
        """Collect and verify all scraped data is present."""

        company = state.get('company', 'Unknown Company')
        msg = [f"📦 Collecting scraped data for {company}:"]

        if websocket_manager := state.get('websocket_manager'):
            if job_id := state.get('job_id'):
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="processing",
                    message=f"Collecting scraped data for {company}",
                    result={"step": "Collecting"}
                )

        # Chuyển sang dict_links
        dict_links = state['social_links']

        # TODO
        try:
            python_exe = r".venv\Scripts\python.exe" # windows
            base_cwd = r"scrape"
            data_dir = base_cwd + "/data"

            # Delete old files
            shutil.rmtree(data_dir)
            os.makedirs(data_dir)

            loop = asyncio.get_running_loop()

            # Tạo 3 tasks subprocess chạy song song
            tasks = []
            if 'youtube' in dict_links:
                tasks.append(
                    loop.run_in_executor(
                        None,
                        partial(subprocess.run, [python_exe, "scripts/youtube_scrape.py", "--link", dict_links['youtube']], cwd=base_cwd)
                    )
                )
            if 'tiktok' in dict_links:
                tasks.append(
                    loop.run_in_executor(
                        None,
                        partial(subprocess.run, [python_exe, "scripts/tiktok_scrape.py", "--link", dict_links['tiktok']], cwd=base_cwd)
                    )
                )
            if 'facebook' in dict_links:
                tasks.append(
                    loop.run_in_executor(
                        None,
                        partial(subprocess.run, [python_exe, "scripts/fb_scrape.py", "--link", dict_links['facebook']], cwd=base_cwd)
                    )
                )              

            # Chờ tất cả xong
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"🔥 PYTHON RUNTIME ERROR: {repr(e)}")                
        
        # Check each type of research data
        research_types = {
            'financial_data': '💰 Financial',
            'news_data': '📰 News',
            'industry_data': '🏭 Industry',
            'company_data': '🏢 Company'
        }
        
        for data_field, label in research_types.items():
            data = state.get(data_field, {})
            if data:
                msg.append(f"• {label}: {len(data)} documents collected")
            else:
                msg.append(f"• {label}: No data found")
        
        # Update state with collection message
        messages = state.get('messages', [])
        messages.append(AIMessage(content="\n".join(msg)))
        state['messages'] = messages
        
        return state

    async def run(self, state: ResearchState) -> ResearchState:
        return await self.collect(state)