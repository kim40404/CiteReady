import asyncio
import httpx
from colorama import init, Fore, Style

init(autoreset=True)

EVAL_URLS = [
    "https://flyrank.com",
    "https://example.com"
]

API_URL = "http://localhost:8000/api/v1/analyze"

async def run_eval():
    print(f"{Style.BRIGHT}🚀 Starting CiteReady AI Evaluation Runner...\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for url in EVAL_URLS:
            print(f"{Fore.CYAN}Evaluating URL: {url}{Style.RESET_ALL}")
            try:
                response = await client.post(API_URL, json={"url": url})
                
                if response.status_code == 200:
                    data = response.json()
                    geo = data.get("geo_score", 0)
                    ai_score = data.get("semantic_score", 0)
                    tech_score = round((geo - (ai_score * 0.4)) / 0.6, 1) if ai_score > 0 else geo
                    
                    print(f"  {Fore.YELLOW}Technical Score:{Style.RESET_ALL} {tech_score}/100")
                    print(f"  {Fore.GREEN}AI Semantic Score:{Style.RESET_ALL} {ai_score}/100")
                    print(f"  {Style.BRIGHT}Final Blended GEO:{Style.RESET_ALL} {geo}/100 (Grade: {data.get('grade')})")
                    
                    print(f"\n  {Fore.MAGENTA}AI Insights (Reasoning):{Style.RESET_ALL}")
                    for insight in data.get("ai_insights", []):
                        print(f"    - {insight}")
                    print("-" * 50)
                else:
                    print(f"  {Fore.RED}Failed:{Style.RESET_ALL} HTTP {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"  {Fore.RED}Error:{Style.RESET_ALL} {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_eval())
