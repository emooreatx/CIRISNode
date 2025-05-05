import asyncio
import httpx


async def run_agent_loop():
    async with httpx.AsyncClient() as client:
        # First, authenticate to get a token
        auth_response = await client.post("http://localhost:8010/api/v1/wa/authenticate")
        auth_data = auth_response.json()
        token = auth_data.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print("Authenticated with token:", token)

        while True:
            # Simulated thought input (normally from Discord, etc.)
            thought = {"text": "Should I approve this?"}
            response = await client.post("http://localhost:8010/api/v1/wa/run", json=thought, headers=headers)
            print("Agent got decision result:", response.json())
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent_loop())
