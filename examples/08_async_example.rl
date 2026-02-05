# Async/Await Example

import net.http as http
import time
import concurrency as runtime

async def fetch_status(url):
    let response = await http.get(url)
    return response.status

async def main():
    let status = await fetch_status("https://example.com")
    print(format("Status: {}", status))
    await time.sleep(0.5)

# Entry point for the async runtime
runtime.run(main())
