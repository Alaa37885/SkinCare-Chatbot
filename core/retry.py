import asyncio
import random


RETRYABLE_ERRORS = [429, 500, 502, 503, 504]


async def invoke_with_retry(llm, user_input, max_attempts=5):

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[TRY {attempt}] Sending request...")  #  check start

            result = await llm.ainvoke(user_input)

            print(f"[SUCCESS] Attempt {attempt}")  #  check success
            return result

        except Exception as e:
            status = getattr(e, "status_code", None)

            print(f"[ERROR] Attempt {attempt} | Status: {status}")

            # check if retryable
            if status not in RETRYABLE_ERRORS:
                print("[STOP] Non-retryable error")
                raise e

            if attempt == max_attempts:
                print("[FAILED] Max retries reached")
                raise e

            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"[RETRY] Waiting {wait:.2f}s...\n")

            await asyncio.sleep(wait) 